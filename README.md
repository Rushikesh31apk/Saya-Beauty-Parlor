# 💅 Saya Beauty Parlor 💇‍♀️✨

A complete, modern, and responsive Beauty Parlor Management System built with **Python Flask**, **SQLite**, **Bootstrap 5**, and **Jinja2 Templates**. Designed for managing appointments, customers, staff, services, billing, and revenue — all from a clean admin dashboard.

---

## 📁 Folder Structure

```
saya-beauty-parlor/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── dashboard.css
│   ├── js/
│   │   ├── main.js
│   │   └── dashboard.js
│   └── images/
│       ├── hero.jpg
│       ├── about.jpg
│       ├── gallery1.jpg
│       ├── gallery2.jpg
│       └── logo.png
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── admin/
│       ├── dashboard.html
│       ├── appointments.html
│       ├── today_appointments.html
│       ├── customers.html
│       ├── staff.html
│       ├── add_staff.html
│       ├── edit_staff.html
│       ├── services.html
│       ├── add_service.html
│       ├── edit_service.html
│       ├── generate_bill.html
│       ├── view_bill.html
│       └── revenue_report.html
│
└── database/
    └── saya_parlor.db
```

---

## ⚙️ Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | HTML5, CSS3, Bootstrap 5, JavaScript |
| Icons      | Font Awesome                        |
| Fonts      | Google Fonts                        |
| Charts     | Chart.js                            |
| Backend    | Python Flask                        |
| Database   | SQLite                              |
| Templates  | Jinja2                              |
| Auth       | Flask Session + Werkzeug Hashing    |

---

## 🚀 Installation & Setup

### 1. Clone or Download the Project

```bash
git clone https://github.com/your-username/saya-beauty-parlor.git
cd saya-beauty-parlor
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

```bash
python database.py
```

> This will create the SQLite database at `database/saya_parlor.db` and populate it with default admin credentials and sample data.

### 5. Run the Flask Application

```bash
python app.py
```

---

## 🌐 Access the Application

| Page              | URL                              |
|-------------------|----------------------------------|
| Landing Website   | http://127.0.0.1:5000/           |
| Admin Login       | http://127.0.0.1:5000/login      |
| Admin Dashboard   | http://127.0.0.1:5000/dashboard  |

---

## 🧭 How to Use the Dashboard

### Appointments
- View all appointments at `/appointments`
- Today's appointments at `/appointments/today`
- Filter by **Pending**, **Confirmed**, **Completed**, or **Cancelled**
- Actions: **Confirm → Complete → Generate Bill → Print**

### Customers
- Auto-saved when an appointment is booked
- View visit history and total spend at `/customers`
- Search by name or mobile number

### Staff Management
- Add/Edit/Delete staff at `/staff`
- Fields: Name, Role, Specialization, Experience, Salary, Status

### Service Management
- Add/Edit/Delete services at `/admin/services`
- Categories: Hair, Skin, Makeup, Bridal, Spa, Nails, Mehendi

### Billing
- Generate bill after marking appointment as **Completed**
- Supports: Cash, UPI, Card, Online payment modes
- Print or download a clean professional invoice

### Revenue Reports
- View Today / Weekly / Monthly / Total revenue at `/reports/revenue`
- Filter by date range, payment mode, or service
- Visual charts powered by Chart.js

---


## 💅 Public Website Sections

- **Hero** — "Glow Naturally, Shine Beautifully"
- **About** — Parlor introduction
- **Services** — 16 services with price, duration & booking
- **Packages** — 5 curated beauty packages with offer badges
- **Gallery** — Parlor & work showcase images
- **Staff** — Team cards with role & specialization
- **Testimonials** — Customer reviews with star ratings
- **Why Choose Us** — Key highlights
- **Contact** — Address, phone, WhatsApp, email, hours & map
- **Appointment Booking Form** — Inline booking with success message

---

## 🛡️ Security Features

- Session-based authentication
- All admin routes are login-protected
- Passwords hashed with **Werkzeug**
- Parameterized SQLite queries (SQL injection safe)
- Form validation on frontend and backend
- Flash messages for success and error feedback

---

## 📦 requirements.txt

```
Flask==2.3.3
Werkzeug==2.3.7
```

---

## 🎨 Design Theme

| Element     | Value                          |
|-------------|--------------------------------|
| Primary     | Pink / Rose Gold               |
| Background  | White / Soft Cream             |
| Accent      | Light Purple                   |
| Text        | Soft Black                     |
| Style       | Feminine, Elegant, Premium     |
| Responsive  | Yes — Mobile & Desktop ready   |

---

## 🙌 Credits

**Developed for:** Saya Beauty Parlor  
**Stack:** Flask · SQLite · Bootstrap 5 · Chart.js  
**Purpose:** Complete Parlor Management System — Client Ready

---

> Made with Rushikesh Narawade
