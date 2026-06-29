from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Sum, F
from django.core.mail import send_mail
from django.conf import settings

from bookstore.models import Book, RequestBook, ProcureBook, Cart, Inventory, Sales, Vendor, Vendor_list
from datetime import datetime, timedelta
from rangefilter.filters import DateRangeFilter

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend — required for Django (no GUI thread)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64

# admin.site.register(Cart)

# ─────────────────────────────────────────────────────
#  Simple admin registrations (no customisation needed)
# ─────────────────────────────────────────────────────

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display  = ('title', 'author', 'isbn', 'publisher', 'price')
    ordering      = ('title',)
    search_fields = ('title', 'author', 'isbn', 'publisher', 'genre')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('book', 'stock', 'rack_number')
    ordering     = ('rack_number',)


@admin.register(RequestBook)
class RequestBookAdmin(admin.ModelAdmin):
    list_display  = ('date_of_request', 'book', 'requested_by', 'quantity')
    ordering      = ('date_of_request',)
    search_fields = ('requested_by',)


@admin.register(ProcureBook)
class ProcureBookAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'book_title')


# ─────────────────────────────────────────────────────
#  Matplotlib helpers — light theme to match Django admin
# ─────────────────────────────────────────────────────

PALETTE = [
    '#2563EB', '#DC2626', '#16A34A', '#9333EA',
    '#D97706', '#0891B2', '#BE185D', '#4F46E5',
    '#059669', '#EA580C',
]


def _fig_to_b64(fig):
    """Render a matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=110)
    buf.seek(0)
    data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return data


def _style_axes(ax, title, xlabel='', ylabel=''):
    """Apply a clean, light style that blends with Django admin's white UI."""
    ax.set_facecolor('#F8FAFC')
    ax.figure.patch.set_facecolor('#FFFFFF')
    ax.set_title(title, color='#1E293B', fontsize=12, fontweight='bold', pad=10)
    ax.set_xlabel(xlabel, color='#475569', fontsize=9)
    ax.set_ylabel(ylabel, color='#475569', fontsize=9)
    ax.tick_params(colors='#475569', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#CBD5E1')
    ax.grid(color='#E2E8F0', linestyle='--', linewidth=0.7, alpha=0.9, zorder=0)


# ─────────────────────────────────────────────────────
#  SalesAdmin — analytics dashboard
# ─────────────────────────────────────────────────────

@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('date', 'book', 'buyer_name', 'revenue', 'quantity')
    ordering     = ('-date',)

    list_filter = (
        ('date', DateRangeFilter),
        'book',
    )

    change_list_template = 'admin/sales_change_list.html'

    # ── Main changelist hook ────────────────────────────────────────────────
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        # Guard: some redirects won't have context_data
        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        # Materialise queryset once with related book data
        sales_list = list(queryset.select_related('book'))

        # ── KPI cards ──────────────────────────────────────────────────────
        total_revenue = sum(float(s.revenue) for s in sales_list)
        total_qty     = sum(s.quantity for s in sales_list)
        unique_books  = len({s.book_id for s in sales_list})

        book_rev = {}
        for s in sales_list:
            book_rev[s.book.title] = book_rev.get(s.book.title, 0) + float(s.revenue)
        top_book = max(book_rev, key=book_rev.get) if book_rev else '—'

        response.context_data['total_revenue'] = round(total_revenue, 2)
        response.context_data['total_qty']     = total_qty
        response.context_data['unique_books']  = unique_books
        response.context_data['top_book']      = top_book

        # ── Charts ─────────────────────────────────────────────────────────
        response.context_data['chart_daily_revenue'] = self._chart_daily_revenue(sales_list)
        response.context_data['chart_top_books']     = self._chart_top_books(sales_list)
        response.context_data['chart_genre_pie']     = self._chart_genre_pie(sales_list)
        response.context_data['chart_monthly']       = self._chart_monthly(sales_list)

        return response

    # ── Chart 1: Daily Revenue Bar Chart ───────────────────────────────────
    def _chart_daily_revenue(self, sales_list):
        date_rev = {}
        for s in sales_list:
            d = (s.date + timedelta(hours=5, minutes=30)).date()
            date_rev[d] = date_rev.get(d, 0) + float(s.revenue)

        if not date_rev:
            return None

        dates    = sorted(date_rev.keys())
        revenues = [date_rev[d] for d in dates]

        fig, ax = plt.subplots(figsize=(10, 3.8))
        ax.bar(dates, revenues, color='#2563EB', width=0.5, zorder=3,
               edgecolor='#1D4ED8', linewidth=0.5)

        interval = max(1, len(dates) // 12)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
        _style_axes(ax, 'Daily Revenue', 'Date', 'Revenue (₹)')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        return _fig_to_b64(fig)

    # ── Chart 2: Top 10 Books by Revenue (horizontal bar) ──────────────────
    def _chart_top_books(self, sales_list):
        book_rev = {}
        for s in sales_list:
            title = s.book.title
            label = (title[:27] + '…') if len(title) > 27 else title
            book_rev[label] = book_rev.get(label, 0) + float(s.revenue)

        if not book_rev:
            return None

        top10   = sorted(book_rev.items(), key=lambda x: x[1], reverse=True)[:10]
        labels  = [b[0] for b in reversed(top10)]
        values  = [b[1] for b in reversed(top10)]
        colors  = PALETTE[:len(labels)]

        fig, ax = plt.subplots(figsize=(10, max(3.5, len(labels) * 0.5)))
        ax.barh(labels, values, color=colors, height=0.55, zorder=3,
                edgecolor='white', linewidth=0.4)

        for i, val in enumerate(values):
            ax.text(val + max(values) * 0.015, i, f'₹{val:,.0f}',
                    va='center', color='#1E293B', fontsize=7.5, fontweight='bold')

        _style_axes(ax, 'Top 10 Books by Revenue', 'Revenue (₹)')
        ax.set_xlim(0, max(values) * 1.22)

        return _fig_to_b64(fig)

    # ── Chart 3: Revenue by Genre (pie chart) ──────────────────────────────
    def _chart_genre_pie(self, sales_list):
        genre_rev = {}
        for s in sales_list:
            g = (getattr(s.book, 'genre', None) or 'Other').strip() or 'Other'
            genre_rev[g] = genre_rev.get(g, 0) + float(s.revenue)

        if not genre_rev:
            return None

        # Merge slices < 3% into "Other"
        total  = sum(genre_rev.values())
        merged = {}
        other  = 0.0
        for k, v in genre_rev.items():
            if v / total < 0.03:
                other += v
            else:
                merged[k] = v
        if other:
            merged['Other'] = merged.get('Other', 0) + other

        labels  = list(merged.keys())
        sizes   = list(merged.values())
        colors  = PALETTE[:len(labels)]
        explode = [0.03] * len(labels)

        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor('#FFFFFF')
        _, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors, explode=explode,
            autopct='%1.1f%%', startangle=140,
            textprops={'color': '#1E293B', 'fontsize': 8.5},
            wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'},
        )
        for at in autotexts:
            at.set_fontweight('bold')
            at.set_fontsize(8)
        ax.set_title('Revenue by Genre', color='#1E293B', fontsize=12,
                     fontweight='bold', pad=12)

        return _fig_to_b64(fig)

    # ── Chart 4: Monthly Revenue & Units Sold (dual-axis line) ──────────────
    def _chart_monthly(self, sales_list):
        month_rev = {}
        month_qty = {}
        for s in sales_list:
            d   = (s.date + timedelta(hours=5, minutes=30)).date()
            key = d.replace(day=1)
            month_rev[key] = month_rev.get(key, 0) + float(s.revenue)
            month_qty[key] = month_qty.get(key, 0) + s.quantity

        if not month_rev:
            return None

        months   = sorted(month_rev.keys())
        revenues = [month_rev[m] for m in months]
        qtys     = [month_qty[m] for m in months]
        labels   = [m.strftime('%b %Y') for m in months]
        x        = list(range(len(labels)))

        c_rev = '#2563EB'
        c_qty = '#DC2626'

        fig, ax1 = plt.subplots(figsize=(10, 3.8))
        fig.patch.set_facecolor('#FFFFFF')
        ax1.set_facecolor('#F8FAFC')

        ax1.plot(x, revenues, color=c_rev, marker='o', linewidth=2.2,
                 markersize=6, zorder=3, label='Revenue (₹)')
        ax1.fill_between(x, revenues, alpha=0.08, color=c_rev)
        ax1.set_xticks(x)
        ax1.set_xticklabels(labels, rotation=35, ha='right', fontsize=8, color='#475569')
        ax1.set_ylabel('Revenue (₹)', color=c_rev, fontsize=9)
        ax1.tick_params(axis='y', labelcolor=c_rev, labelsize=8)
        ax1.set_title('Monthly Revenue & Units Sold', color='#1E293B',
                      fontsize=12, fontweight='bold', pad=10)
        ax1.grid(color='#E2E8F0', linestyle='--', linewidth=0.7, alpha=0.9)
        for sp in ax1.spines.values():
            sp.set_edgecolor('#CBD5E1')

        ax2 = ax1.twinx()
        ax2.plot(x, qtys, color=c_qty, marker='s', linewidth=2,
                 linestyle='--', markersize=5, zorder=3, label='Units Sold')
        ax2.set_ylabel('Units Sold', color=c_qty, fontsize=9)
        ax2.tick_params(axis='y', labelcolor=c_qty, labelsize=8)
        for sp in ax2.spines.values():
            sp.set_edgecolor('#CBD5E1')

        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, loc='upper left',
                   facecolor='white', edgecolor='#CBD5E1', fontsize=8)

        return _fig_to_b64(fig)


# ─────────────────────────────────────────────────────
#  Vendor / inventory threshold filter
# ─────────────────────────────────────────────────────

class ThresholdFIlter(admin.SimpleListFilter):
    title          = _("Threshold")
    parameter_name = "threshold"

    def lookups(self, request, model_admin):
        return [("threshold", "Update threshold and Show books below threshold")]

    def queryset(self, request, queryset):
        if self.value() == "threshold":
            two_weeks_ago = timezone.localtime(timezone.now()) - timedelta(days=14)

            books_sold = Sales.objects.filter(
                date__gte=two_weeks_ago,
            ).values('book').annotate(total_sold=Sum('quantity'))

            updated_thresholds = {}
            for book_sold in books_sold:
                book_id   = book_sold['book']
                total_sold = book_sold['total_sold']
                updated_thresholds[book_id] = 20 + total_sold

            for book_id, new_threshold in updated_thresholds.items():
                Vendor_list.objects.filter(book_id=book_id).update(threshold=new_threshold)

            return Vendor_list.objects.filter(book__inventory__stock__lt=F('threshold'))


@admin.register(Vendor_list)
class VendorListAdmin(admin.ModelAdmin):
    list_display = ('book', 'vendor', 'threshold', 'stock')
    list_filter  = [ThresholdFIlter]
    ordering     = ('vendor',)
    actions      = ['send_orders_to_vendors']

    def send_orders_to_vendors(self, request, queryset):
        vendor_books = {}
        for vendor_list in queryset:
            if vendor_list.stock < vendor_list.threshold:
                vid = vendor_list.vendor.id
                if vid not in vendor_books:
                    vendor_books[vid] = []
                vendor_books[vid].append(vendor_list)

        for vendor_id, books in vendor_books.items():
            vendor        = Vendor.objects.get(id=vendor_id)
            order_message = "Please supply the following books:\n\n"
            for book in books:
                order_message += f"- {book.book.title} ({book.threshold - book.stock} copies)\n"

            send_mail(
                subject="Order Request",
                message=order_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[vendor.email],
            )

        self.message_user(request, _("Orders sent to vendors successfully."))


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
