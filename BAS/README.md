# 📚 Bookstore Automation System (BAS)

A web-based bookstore management system built with **Django 5** and **SQLite**. It provides a customer-facing storefront for browsing and purchasing books, and a powerful admin portal for managing inventory, vendors, sales analytics, and automated vendor re-order notifications.

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
| Environment config | `python-decouple` |

---

## ⚡ Quick Start (Clone & Run)

Follow these steps exactly to get the project running on your machine.

### Step 1 — Clone the repository

```bash
git clone https://github.com/your-username/Bookstore-Automation-System.git
cd Bookstore-Automation-System/BAS
```

> Replace the URL with the actual GitHub repo link.

---

### Step 2 — Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows (Command Prompt / PowerShell)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

---

### Step 3 — Install dependencies

```bash
pip install django django-rangefilter matplotlib pillow python-decouple
```

| Package | Why it's needed |
|---|---|
| `django` | Web framework |
| `django-rangefilter` | Date range filter in admin |
| `matplotlib` | Sales analytics charts |
| `pillow` | Book cover image handling |
| `python-decouple` | Reads secrets from `.env` file |

---

### Step 4 — Set up your `.env` file

The project uses a `.env` file to store secrets. **It is not included in the repo** (gitignored for security).

Copy the example file and fill in your values:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and update it:

```env
# Django
SECRET_KEY=any-long-random-string-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Gmail SMTP (used for vendor emails and wishlists)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

> **How to get a Gmail App Password:**
> 1. Go to https://myaccount.google.com/apppasswords
> 2. Select app → **Mail**, device → **Other**
> 3. Copy the 16-character password into `.env`

> **Tip:** If you don't need email functionality right now, you can put any placeholder values — the app will still run.

---

### Step 5 — Apply database migrations

The repo includes a pre-seeded `db.sqlite3` with sample books, inventory, and sales data.

If you want to use the existing data, **skip this step**.

To start with a fresh empty database:

```bash
# Delete the existing database first
del db.sqlite3          # Windows
rm db.sqlite3           # macOS / Linux

# Then run migrations
python manage.py migrate

# Create your own admin account
python manage.py createsuperuser
```

---

### Step 6 — Run the server

```bash
python manage.py runserver
```

Open your browser and go to: **http://127.0.0.1:8000/**

---

## 🔑 Default Admin Credentials

If you are using the pre-seeded database (default):

| Field | Value |
|---|---|
| URL | http://127.0.0.1:8000/admin/ |
| Username | `DAM` |
| Password | `Admin@1234` |

---

## 🌐 All URLs

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/` | Home page |
| `http://127.0.0.1:8000/customer_to_search/` | Customer browsing page |
| `http://127.0.0.1:8000/search/` | Book search |
| `http://127.0.0.1:8000/cart/` | Shopping cart |
| `http://127.0.0.1:8000/login/` | Customer login |
| `http://127.0.0.1:8000/register/` | Customer registration |
| `http://127.0.0.1:8000/admin/` | Admin portal |
| `http://127.0.0.1:8000/admin/bookstore/sales/` | Sales analytics dashboard |

---

## 📊 Admin Analytics Dashboard

Go to **Admin → Bookstore → Saless** to view the analytics dashboard.

It shows:
- **KPI Cards:** Total Revenue · Units Sold · Unique Titles · Top Selling Book
- **4 matplotlib charts** (server-rendered, no JS dependencies):
  - Daily revenue bar chart
  - Top 10 books by revenue (horizontal bar)
  - Revenue by genre (pie chart)
  - Monthly revenue & units sold (dual-axis line chart)

> All charts update dynamically when you use the **date range filter** in the sidebar.

---

## 🔔 Automated Vendor Ordering

In **Admin → Bookstore → Vendor_lists**:

1. Apply the **"Update threshold and Show books below threshold"** filter.
2. Select the listed books.
3. Use the **"Send orders to vendors"** action to automatically email each vendor.

The threshold is recalculated based on sales from the last 14 days.

---

## 📁 Project Structure

```
Bookstore-Automation-System/
├── .gitignore
└── BAS/
    ├── .env                    ← You create this (gitignored)
    ├── .env.example            ← Template to copy from
    ├── manage.py               ← Django entry point
    ├── db.sqlite3              ← Pre-seeded SQLite database
    ├── README.md
    ├── BAS/                    ← Project config
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── bookstore/              ← Main Django app
    │   ├── models.py           ← 8 data models
    │   ├── views.py            ← Business logic
    │   ├── admin.py            ← Admin + analytics charts
    │   ├── urls.py             ← App URL routes
    │   └── backends.py         ← Custom auth (login by email or username)
    ├── templates/              ← HTML templates
    │   ├── base.html
    │   ├── index.html
    │   ├── search.html
    │   ├── cart.html
    │   ├── bill.html
    │   └── admin/
    │       └── sales_change_list.html
    └── static/                 ← CSS, JS, images
```

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

These are **non-critical** warnings shown at server start:

```
bookstore.RequestBook.date_of_request: (fields.W161) Fixed default value provided.
bookstore.Sales.date: (fields.W161) Fixed default value provided.
```

They do not affect any functionality and can be safely ignored.

---

## 🧪 Running Tests

```bash
python manage.py test bookstore
```

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'decouple'` | Run `pip install python-decouple` |
| `ModuleNotFoundError: No module named 'rangefilter'` | Run `pip install django-rangefilter` |
| `.env file not found` | Copy `.env.example` to `.env` and fill in values |
| Charts not loading (500 error) | Make sure `matplotlib` is installed: `pip install matplotlib` |
| `Pillow` error on book image | Run `pip install pillow` |
| Port already in use | Run `python manage.py runserver 8080` to use a different port |

---

## 📄 License

This project was developed as part of a Software Engineering coursework by **Team MAD**.
