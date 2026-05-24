"""Database setup and helper utilities for Saya Beauty Parlor Management System."""
import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "saya_parlor.db")


def get_db_connection():
    """Return a SQLite connection with rows accessible as dictionaries."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create database tables and seed default data."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'manager',
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
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
    """)

    cur.execute("""
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
    """)

    cur.execute("""
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
    """)

    cur.execute("""
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
    """)

    cur.execute("""
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
    """)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Default admin user. Password: admin123
    cur.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
            ("admin", generate_password_hash("admin123"), "manager", now),
        )

    # Seed services only when empty.
    cur.execute("SELECT COUNT(*) AS total FROM services")
    if cur.fetchone()["total"] == 0:
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
        cur.executemany(
            "INSERT INTO services (name, category, description, price, duration, status, created_at) VALUES (?, ?, ?, ?, ?, 'Active', ?)",
            [(name, cat, desc, price, duration, now) for name, cat, desc, price, duration in services],
        )

    cur.execute("SELECT COUNT(*) AS total FROM staff")
    if cur.fetchone()["total"] == 0:
        staff = [
            ("Priya Sharma", "9876543210", "priya@saya.com", "Senior Beautician", "Facial, Skin Care", "5 Years", 22000, "2024-01-10"),
            ("Riya Patil", "9876501234", "riya@saya.com", "Makeup Artist", "Bridal and Party Makeup", "4 Years", 25000, "2024-03-15"),
            ("Neha Jadhav", "9988776655", "neha@saya.com", "Hair Stylist", "Hair Cut, Spa, Color", "3 Years", 20000, "2024-05-20"),
        ]
        cur.executemany(
            """
            INSERT INTO staff (name, mobile, email, role, specialization, experience, salary, joining_date, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?)
            """,
            [(*row, now) for row in staff],
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
