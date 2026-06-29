# 📚 Bookstore Automation System (BAS)

A web-based bookstore management system built with **Django 5** and **SQLite**. It provides a customer-facing storefront for browsing and purchasing books, and a powerful admin portal for managing inventory, vendors, sales analytics, and automated re-order notifications.

---

## 🚀 Features

### 👤 Customer Portal
- Browse and search books by title, author, ISBN, publisher, or genre
- View detailed book information
- Add books to cart and proceed to purchase
- Receive a bill on checkout
- Request out-of-stock books
- Submit procurement requests for new books
- Send wishlist via email

### 🔐 Admin Portal (`/admin`)
- Manage books, inventory, vendors, and vendor lists
- View and filter all sales records by date range or book
- **Sales Analytics Dashboard** (matplotlib charts):
  - Daily Revenue bar chart
  - Top 10 Books by Revenue
  - Revenue by Genre (pie chart)
  - Monthly Revenue & Units Sold trend
- Automated threshold detection — flags books below stock threshold
- One-click email order requests sent to vendors

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 |
| Database | SQLite 3 |
| Analytics | Matplotlib |
| Email | Gmail SMTP |
| Auth | Custom backend (email or username login) |
| Admin date filter | `django-rangefilter` |

---

## 📁 Project Structure

```
Bookstore-Automation-System/
└── BAS/
    ├── manage.py               # Django entry point
    ├── db.sqlite3              # SQLite database (pre-seeded)
    ├── BAS/                    # Project config (settings, urls, wsgi)
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── bookstore/              # Main Django app
    │   ├── models.py           # Data models
    │   ├── views.py            # Business logic
    │   ├── admin.py            # Admin panel + analytics
    │   ├── urls.py             # App URL routes
    │   └── backends.py         # Custom auth backend
    ├── templates/              # HTML templates
    │   ├── base.html
    │   ├── index.html
    │   ├── search.html
    │   ├── cart.html
    │   ├── bill.html
    │   └── admin/
    │       └── sales_change_list.html   # Analytics dashboard template
    └── static/                 # CSS, JS, images
```

---

## ⚙️ Prerequisites

Make sure you have the following installed:

- **Python 3.10+**
- **pip**

---

## 🔧 Installation & Setup

### 1. Clone or extract the project

```bash
cd Bookstore-Automation-System/BAS
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django
pip install django-rangefilter
pip install matplotlib
pip install pillow
```

> **Note:** `Pillow` is required for the `ImageField` used in the `Book` model.

### 4. Apply database migrations

> The project includes a pre-seeded `db.sqlite3` file. If you want to start fresh, delete it and run:

```bash
python manage.py migrate
```

### 5. Create a superuser (skip if using the existing database)

```bash
python manage.py createsuperuser
```

> The existing database already has an admin account:
> - **Username:** `DAM`
> - **Password:** `Admin@1234`

### 6. Run the development server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

---

## 🌐 URL Reference

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/` | Home page |
| `http://127.0.0.1:8000/customer_to_search/` | Customer browsing page |
| `http://127.0.0.1:8000/search/` | Book search |
| `http://127.0.0.1:8000/cart/` | Shopping cart |
| `http://127.0.0.1:8000/login/` | Customer login |
| `http://127.0.0.1:8000/register/` | Customer registration |
| `http://127.0.0.1:8000/admin/` | Admin portal login |
| `http://127.0.0.1:8000/admin/bookstore/sales/` | Sales + Analytics dashboard |

---

## 📊 Admin Analytics Dashboard

Navigate to **Admin → Bookstore → Saless** (`/admin/bookstore/sales/`) to view the analytics dashboard.

It shows:
- **KPI Cards:** Total Revenue · Units Sold · Unique Titles · Top Selling Book
- **Charts** (all generated server-side using matplotlib):
  - Daily revenue bar chart
  - Top 10 books by revenue (horizontal bar)
  - Revenue by genre (pie chart)
  - Monthly revenue & units sold (dual-axis line chart)

> All charts respond to Django admin's **date range filter** in the sidebar.

---

## 🔔 Automated Vendor Ordering

In **Admin → Bookstore → Vendor_lists**:

1. Apply the **"Update threshold and Show books below threshold"** filter to identify books that need restocking.
2. Select the books and use the **"Send orders to vendors"** action to email the vendor automatically.

The threshold is dynamically recalculated based on sales in the last 14 days.

---

## 📧 Email Configuration

Email is configured for Gmail SMTP in `settings.py`. To use your own email account:

```python
# BAS/settings.py
EMAIL_HOST_USER     = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'   # Use a Gmail App Password
```

> Generate a Gmail App Password at: https://myaccount.google.com/apppasswords

---

## 🗄️ Data Models

| Model | Purpose |
|---|---|
| `Book` | Book catalogue (title, author, ISBN, genre, price, image) |
| `Inventory` | Stock count and rack number per book |
| `Sales` | Record of each sale (book, buyer, revenue, date) |
| `Cart` | Temporary cart items per user session |
| `RequestBook` | Customer requests for out-of-stock books |
| `ProcureBook` | Customer requests to add a new book to the catalogue |
| `Vendor` | Vendor contact details |
| `Vendor_list` | Book ↔ Vendor mapping with reorder threshold |

---

## ⚠️ Known Warnings

The following are non-critical warnings from Django's system check:

```
bookstore.RequestBook.date_of_request: (fields.W161) Fixed default value provided.
bookstore.Sales.date: (fields.W161) Fixed default value provided.
```

These do not affect functionality. They can be fixed by changing the model defaults to `django.utils.timezone.now` (callable) instead of `timezone.now()` (evaluated at startup).

---

## 🧪 Running Tests

```bash
python manage.py test bookstore
```

---

## 📄 License

This project was developed as part of a Software Engineering coursework by **Team MAD**.
