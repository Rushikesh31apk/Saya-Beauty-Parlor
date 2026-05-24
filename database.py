"""Database setup and helper utilities for Saya Beauty Parlor Management System.

Run this file once:
    python database.py

Default manager login:
    username: admin
    password: admin123

This file creates:
- users
- services
- staff
- customers
- appointments
- bills

It also inserts complete dummy demo data so your dashboard shows:
- appointments
- pending/completed counts
- customers
- staff
- today revenue
- total revenue
- last 7 days revenue
"""

import os
import sqlite3
from datetime import datetime, date, timedelta

from werkzeug.security import generate_password_hash


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "saya_parlor.db")

# Keep this False to avoid deleting your real appointments/bills.
# Change to True only if you want to recreate demo appointments and bills.
RESET_DEMO_APPOINTMENTS_AND_BILLS = False


def get_db_connection():
    """Return a SQLite connection with rows accessible as dictionaries."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def table_count(cur, table_name):
    """Return total rows from a table."""
    cur.execute(f"SELECT COUNT(*) AS total FROM {table_name}")
    return cur.fetchone()["total"]


def get_service_id(cur, service_name):
    """Return service id by service name."""
    cur.execute("SELECT id FROM services WHERE name = ?", (service_name,))
    row = cur.fetchone()
    return row["id"] if row else None


def get_staff_id(cur, mobile):
    """Return staff id by mobile number."""
    cur.execute("SELECT id FROM staff WHERE mobile = ?", (mobile,))
    row = cur.fetchone()
    return row["id"] if row else None


def get_customer_id(cur, mobile):
    """Return customer id by mobile number."""
    cur.execute("SELECT id FROM customers WHERE mobile = ?", (mobile,))
    row = cur.fetchone()
    return row["id"] if row else None


def ensure_service(cur, service, now):
    """Insert service if missing and return its id."""
    name, category, description, price, duration = service
    cur.execute("SELECT id FROM services WHERE name = ?", (name,))
    row = cur.fetchone()

    if row:
        return row["id"]

    cur.execute(
        """
        INSERT INTO services
        (name, category, description, price, duration, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'Active', ?)
        """,
        (name, category, description, price, duration, now),
    )
    return cur.lastrowid


def ensure_staff(cur, staff_member, now):
    """Insert staff member if missing and return staff id."""
    name, mobile, email, role, specialization, experience, salary, joining_date = staff_member

    cur.execute("SELECT id FROM staff WHERE mobile = ?", (mobile,))
    row = cur.fetchone()

    if row:
        return row["id"]

    cur.execute(
        """
        INSERT INTO staff
        (name, mobile, email, role, specialization, experience, salary, joining_date, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?)
        """,
        (name, mobile, email, role, specialization, experience, salary, joining_date, now),
    )
    return cur.lastrowid


def ensure_customer(cur, customer, now):
    """Insert customer if missing and return customer id."""
    name, mobile, email, total_visits, total_spend, last_visit = customer

    cur.execute("SELECT id FROM customers WHERE mobile = ?", (mobile,))
    row = cur.fetchone()

    if row:
        return row["id"]

    cur.execute(
        """
        INSERT INTO customers
        (name, mobile, email, total_visits, total_spend, last_visit, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (name, mobile, email, total_visits, total_spend, last_visit, now),
    )
    return cur.lastrowid


def create_tables(cur):
    """Create all required database tables."""
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'manager',
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL DEFAULT 0,
            duration TEXT,
            status TEXT NOT NULL DEFAULT 'Active',
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT,
            email TEXT,
            role TEXT NOT NULL,
            specialization TEXT,
            experience TEXT,
            salary REAL DEFAULT 0,
            joining_date TEXT,
            status TEXT NOT NULL DEFAULT 'Active',
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE,
            email TEXT,
            total_visits INTEGER NOT NULL DEFAULT 0,
            total_spend REAL NOT NULL DEFAULT 0,
            last_visit TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT,
            service_id INTEGER,
            staff_id INTEGER,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            message TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL,
            FOREIGN KEY(service_id) REFERENCES services(id),
            FOREIGN KEY(staff_id) REFERENCES staff(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            customer_id INTEGER,
            service_id INTEGER,
            service_price REAL NOT NULL DEFAULT 0,
            extra_charges REAL NOT NULL DEFAULT 0,
            discount REAL NOT NULL DEFAULT 0,
            gst REAL NOT NULL DEFAULT 0,
            final_amount REAL NOT NULL DEFAULT 0,
            payment_mode TEXT NOT NULL,
            payment_status TEXT NOT NULL DEFAULT 'Paid',
            bill_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(appointment_id) REFERENCES appointments(id),
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(service_id) REFERENCES services(id)
        )
        """
    )


def seed_master_data(cur, now):
    """Seed admin user, services, staff, and customers."""
    # Default admin user. Password: admin123
    cur.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if cur.fetchone() is None:
        cur.execute(
            """
            INSERT INTO users (username, password, role, created_at)
            VALUES (?, ?, ?, ?)
            """,
            ("admin", generate_password_hash("admin123"), "manager", now),
        )

    services = [
        ("Hair Cut", "Hair", "Trendy haircut with expert finishing.", 250, "30 min"),
        ("Hair Styling", "Hair", "Party-ready styling and blow dry.", 500, "45 min"),
        ("Hair Spa", "Hair", "Deep nourishing hair spa treatment.", 900, "60 min"),
        ("Hair Coloring", "Hair", "Premium hair color with consultation.", 1500, "120 min"),
        ("Facial", "Skin", "Glow facial for fresh and clean skin.", 800, "60 min"),
        ("Cleanup", "Skin", "Quick cleanup for instant freshness.", 400, "30 min"),
        ("Threading", "Skin", "Eyebrow and upper lip threading.", 80, "15 min"),
        ("Waxing", "Skin", "Smooth waxing service with hygiene care.", 600, "45 min"),
        ("Manicure", "Nails", "Nail shaping, cleaning and hand care.", 500, "40 min"),
        ("Pedicure", "Nails", "Relaxing foot care and nail grooming.", 600, "45 min"),
        ("Bridal Makeup", "Bridal", "Complete bridal makeup and styling.", 8000, "180 min"),
        ("Party Makeup", "Makeup", "Elegant makeup for special occasions.", 2500, "90 min"),
        ("Saree Draping", "Bridal", "Perfect saree draping for events.", 500, "30 min"),
        ("Mehendi", "Mehendi", "Beautiful traditional mehendi designs.", 700, "60 min"),
        ("Skin Care Treatment", "Skin", "Personalized skin care treatment.", 1200, "75 min"),
        ("Spa Treatment", "Spa", "Relaxing spa therapy for body and mind.", 1800, "90 min"),
    ]

    for service in services:
        ensure_service(cur, service, now)

    staff = [
        ("Priya Sharma", "9876543210", "priya@saya.com", "Senior Beautician", "Facial, Skin Care", "5 Years", 22000, "2024-01-10"),
        ("Riya Patil", "9876501234", "riya@saya.com", "Makeup Artist", "Bridal and Party Makeup", "4 Years", 25000, "2024-03-15"),
        ("Neha Jadhav", "9988776655", "neha@saya.com", "Hair Stylist", "Hair Cut, Spa, Color", "3 Years", 20000, "2024-05-20"),
        ("Sakshi More", "9123456780", "sakshi@saya.com", "Nail Artist", "Manicure, Pedicure, Nail Art", "2 Years", 18000, "2025-01-05"),
        ("Komal Shinde", "9012345678", "komal@saya.com", "Spa Therapist", "Spa, Waxing, Cleanup", "3 Years", 19000, "2025-02-12"),
    ]

    for staff_member in staff:
        ensure_staff(cur, staff_member, now)

    today = date.today()

    customers = [
        ("Akshda", "9922334455", "akshda@example.com", 3, 4200, str(today - timedelta(days=4))),
        ("Sneha Patil", "9988001122", "sneha.patil@example.com", 5, 7800, str(today)),
        ("Pooja Sharma", "9876123450", "pooja.sharma@example.com", 2, 2100, str(today - timedelta(days=6))),
        ("Anjali Jadhav", "9765432109", "anjali.jadhav@example.com", 4, 5600, str(today)),
        ("Rutuja Kale", "9155556677", "rutuja.kale@example.com", 1, 800, str(today - timedelta(days=14))),
        ("Megha More", "9090909090", "megha.more@example.com", 6, 12400, str(today - timedelta(days=1))),
        ("Kavya Joshi", "9321456789", "kavya.joshi@example.com", 2, 3000, str(today - timedelta(days=3))),
        ("Divya Pawar", "9833445566", "divya.pawar@example.com", 3, 4600, str(today)),
        ("Isha Kulkarni", "9766123456", "isha.kulkarni@example.com", 1, 2500, str(today + timedelta(days=1))),
        ("Tanvi Desai", "9654321098", "tanvi.desai@example.com", 2, 3200, str(today + timedelta(days=2))),
    ]

    for customer in customers:
        ensure_customer(cur, customer, now)


def seed_appointments_and_bills(cur, now):
    """Seed complete appointment and billing demo data."""
    today = date.today()
    today_str = str(today)

    if RESET_DEMO_APPOINTMENTS_AND_BILLS:
        cur.execute("DELETE FROM bills")
        cur.execute("DELETE FROM appointments")

    if table_count(cur, "appointments") > 0:
        # Avoid duplicate demo appointments every time the app starts.
        return

    appointment_seed = [
        # customer, mobile, email, service, staff_mobile, date, time, status, message
        ("Sneha Patil", "9988001122", "sneha.patil@example.com", "Facial", "9876543210", today_str, "10:00 AM", "Completed", "Gold facial completed successfully."),
        ("Anjali Jadhav", "9765432109", "anjali.jadhav@example.com", "Hair Spa", "9988776655", today_str, "11:30 AM", "Completed", "Hair spa with premium serum."),
        ("Divya Pawar", "9833445566", "divya.pawar@example.com", "Party Makeup", "9876501234", today_str, "01:00 PM", "Completed", "Party makeup for evening event."),
        ("Akshda", "9922334455", "akshda@example.com", "Threading", "9876543210", today_str, "03:00 PM", "Pending", "Eyebrow threading appointment."),
        ("Kavya Joshi", "9321456789", "kavya.joshi@example.com", "Manicure", "9123456780", today_str, "05:00 PM", "Pending", "Manicure appointment."),
        ("Megha More", "9090909090", "megha.more@example.com", "Bridal Makeup", "9876501234", str(today - timedelta(days=1)), "09:30 AM", "Completed", "Bridal makeup package completed."),
        ("Pooja Sharma", "9876123450", "pooja.sharma@example.com", "Hair Cut", "9988776655", str(today - timedelta(days=2)), "04:30 PM", "Completed", "Layer cut and finishing."),
        ("Rutuja Kale", "9155556677", "rutuja.kale@example.com", "Cleanup", "9012345678", str(today - timedelta(days=3)), "12:00 PM", "Completed", "Fresh cleanup completed."),
        ("Isha Kulkarni", "9766123456", "isha.kulkarni@example.com", "Hair Coloring", "9988776655", str(today + timedelta(days=1)), "02:00 PM", "Confirmed", "Global hair color booking."),
        ("Tanvi Desai", "9654321098", "tanvi.desai@example.com", "Spa Treatment", "9012345678", str(today + timedelta(days=2)), "11:00 AM", "Pending", "Relaxing spa appointment."),
        ("Sneha Patil", "9988001122", "sneha.patil@example.com", "Waxing", "9012345678", str(today + timedelta(days=3)), "04:00 PM", "Pending", "Full arms waxing."),
        ("Anjali Jadhav", "9765432109", "anjali.jadhav@example.com", "Mehendi", "9123456780", str(today - timedelta(days=7)), "06:00 PM", "Cancelled", "Customer cancelled appointment."),
    ]

    created_appointments = []

    for item in appointment_seed:
        customer_name, mobile, email, service_name, staff_mobile, app_date, app_time, status, message = item
        service_id = get_service_id(cur, service_name)
        staff_id = get_staff_id(cur, staff_mobile)

        cur.execute(
            """
            INSERT INTO appointments
            (customer_name, mobile, email, service_id, staff_id, appointment_date, appointment_time, message, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_name,
                mobile,
                email,
                service_id,
                staff_id,
                app_date,
                app_time,
                message,
                status,
                now,
            ),
        )

        created_appointments.append(
            {
                "appointment_id": cur.lastrowid,
                "mobile": mobile,
                "service_id": service_id,
                "status": status,
                "appointment_date": app_date,
            }
        )

    if table_count(cur, "bills") > 0:
        return

    payment_modes = ["Cash", "UPI", "Card", "UPI", "Cash", "Card"]
    payment_index = 0

    for appointment in created_appointments:
        if appointment["status"] != "Completed":
            continue

        cur.execute("SELECT price FROM services WHERE id = ?", (appointment["service_id"],))
        service_row = cur.fetchone()
        service_price = float(service_row["price"]) if service_row else 0

        customer_id = get_customer_id(cur, appointment["mobile"])

        # Demo calculation.
        extra_charges = 100 if service_price >= 1500 else 0
        discount = 200 if service_price >= 2500 else 0
        gst = round((service_price + extra_charges - discount) * 0.18, 2)
        final_amount = round(service_price + extra_charges - discount + gst, 2)

        cur.execute(
            """
            INSERT INTO bills
            (appointment_id, customer_id, service_id, service_price, extra_charges, discount, gst,
             final_amount, payment_mode, payment_status, bill_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Paid', ?, ?)
            """,
            (
                appointment["appointment_id"],
                customer_id,
                appointment["service_id"],
                service_price,
                extra_charges,
                discount,
                gst,
                final_amount,
                payment_modes[payment_index % len(payment_modes)],
                appointment["appointment_date"],
                now,
            ),
        )
        payment_index += 1

    # Update customer total visits/spend from completed paid bills.
    cur.execute(
        """
        UPDATE customers
        SET
            total_visits = (
                SELECT COUNT(*)
                FROM bills
                JOIN appointments ON appointments.id = bills.appointment_id
                WHERE bills.customer_id = customers.id
                  AND bills.payment_status = 'Paid'
                  AND appointments.status = 'Completed'
            ),
            total_spend = COALESCE((
                SELECT SUM(final_amount)
                FROM bills
                WHERE bills.customer_id = customers.id
                  AND bills.payment_status = 'Paid'
            ), 0),
            last_visit = COALESCE((
                SELECT MAX(bill_date)
                FROM bills
                WHERE bills.customer_id = customers.id
                  AND bills.payment_status = 'Paid'
            ), last_visit)
        """
    )


def init_db():
    """Create database tables and seed default data."""
    conn = get_db_connection()
    cur = conn.cursor()

    create_tables(cur)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    seed_master_data(cur, now)
    seed_appointments_and_bills(cur, now)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()

    conn = get_db_connection()
    cur = conn.cursor()

    print(f"Database initialized at: {DB_PATH}")
    print("Demo login: admin / admin123")
    print("-" * 40)
    print(f"Services: {table_count(cur, 'services')}")
    print(f"Staff: {table_count(cur, 'staff')}")
    print(f"Customers: {table_count(cur, 'customers')}")
    print(f"Appointments: {table_count(cur, 'appointments')}")
    print(f"Bills: {table_count(cur, 'bills')}")

    cur.execute("SELECT COUNT(*) AS total FROM appointments WHERE appointment_date = ?", (str(date.today()),))
    print(f"Today appointments: {cur.fetchone()['total']}")

    cur.execute("SELECT COUNT(*) AS total FROM appointments WHERE status = 'Pending'")
    print(f"Pending appointments: {cur.fetchone()['total']}")

    cur.execute("SELECT COUNT(*) AS total FROM appointments WHERE status = 'Completed'")
    print(f"Completed appointments: {cur.fetchone()['total']}")

    cur.execute("SELECT COALESCE(SUM(final_amount), 0) AS total FROM bills WHERE bill_date = ?", (str(date.today()),))
    print(f"Today revenue: ₹{cur.fetchone()['total']}")

    cur.execute("SELECT COALESCE(SUM(final_amount), 0) AS total FROM bills")
    print(f"Total revenue: ₹{cur.fetchone()['total']}")

    conn.close()
