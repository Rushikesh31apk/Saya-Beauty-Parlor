"""Saya Beauty Parlor Management System - Flask Application."""
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = "change-this-secret-key-in-production"


def login_required(view_func):
    """Protect manager routes from unauthenticated users."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access manager dashboard.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


def query_all(sql, params=()):
    conn = get_db_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def query_one(sql, params=()):
    conn = get_db_connection()
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return row


def execute(sql, params=()):
    conn = get_db_connection()
    cur = conn.execute(sql, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


@app.context_processor
def inject_now():
    return {"today_date": date.today().isoformat(), "current_year": datetime.now().year}


@app.route("/")
def index():
    services = query_all("SELECT * FROM services WHERE status='Active' ORDER BY id LIMIT 16")
    staff = query_all("SELECT * FROM staff WHERE status='Active' ORDER BY id")
    return render_template("index.html", services=services, staff=staff)


@app.route("/services")
def public_services():
    services = query_all("SELECT * FROM services WHERE status='Active' ORDER BY category, name")
    staff = query_all("SELECT * FROM staff WHERE status='Active' ORDER BY name")
    return render_template("index.html", services=services, staff=staff)


@app.route("/contact")
def contact():
    return redirect(url_for("index") + "#contact")


@app.route("/book-appointment", methods=["POST"])
def book_appointment():
    name = request.form.get("customer_name", "").strip()
    mobile = request.form.get("mobile", "").strip()
    email = request.form.get("email", "").strip()
    service_id = request.form.get("service_id") or None
    staff_id = request.form.get("staff_id") or None
    appointment_date = request.form.get("appointment_date", "").strip()
    appointment_time = request.form.get("appointment_time", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not mobile or not service_id or not appointment_date or not appointment_time:
        flash("Please fill all required appointment fields.", "danger")
        return redirect(url_for("index") + "#booking")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute(
        """
        INSERT INTO appointments (customer_name, mobile, email, service_id, staff_id, appointment_date, appointment_time, message, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
        """,
        (name, mobile, email, service_id, staff_id, appointment_date, appointment_time, message, now),
    )

    # Create customer if not present.
    existing = query_one("SELECT id FROM customers WHERE mobile=?", (mobile,))
    if existing is None:
        execute(
            "INSERT INTO customers (name, mobile, email, total_visits, total_spend, last_visit, created_at) VALUES (?, ?, ?, 0, 0, NULL, ?)",
            (name, mobile, email, now),
        )

    flash("Your appointment has been booked successfully. Our team will contact you soon.", "success")
    return redirect(url_for("index") + "#booking")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = query_one("SELECT * FROM users WHERE username=?", (username,))
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful. Welcome to manager dashboard.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    today = date.today().isoformat()
    stats = {
        "total_appointments": query_one("SELECT COUNT(*) AS c FROM appointments")["c"],
        "today_appointments": query_one("SELECT COUNT(*) AS c FROM appointments WHERE appointment_date=?", (today,))["c"],
        "pending": query_one("SELECT COUNT(*) AS c FROM appointments WHERE status='Pending'")["c"],
        "completed": query_one("SELECT COUNT(*) AS c FROM appointments WHERE status='Completed'")["c"],
        "customers": query_one("SELECT COUNT(*) AS c FROM customers")["c"],
        "staff": query_one("SELECT COUNT(*) AS c FROM staff")["c"],
        "today_revenue": query_one("SELECT COALESCE(SUM(final_amount),0) AS s FROM bills WHERE bill_date=? AND payment_status='Paid'", (today,))["s"],
        "total_revenue": query_one("SELECT COALESCE(SUM(final_amount),0) AS s FROM bills WHERE payment_status='Paid'")["s"],
    }
    recent = query_all("""
        SELECT a.*, s.name AS service_name, st.name AS staff_name
        FROM appointments a
        LEFT JOIN services s ON a.service_id=s.id
        LEFT JOIN staff st ON a.staff_id=st.id
        ORDER BY a.id DESC LIMIT 8
    """)
    status_rows = query_all("SELECT status, COUNT(*) AS total FROM appointments GROUP BY status")
    revenue_rows = query_all("""
        SELECT bill_date, COALESCE(SUM(final_amount),0) AS total
        FROM bills
        WHERE bill_date >= ?
        GROUP BY bill_date ORDER BY bill_date
    """, ((date.today() - timedelta(days=6)).isoformat(),))
    return render_template("admin/dashboard.html", stats=stats, recent=recent, status_rows=status_rows, revenue_rows=revenue_rows)


def appointment_query(where="1=1", params=()):
    return query_all(f"""
        SELECT a.*, s.name AS service_name, s.price AS service_price, st.name AS staff_name
        FROM appointments a
        LEFT JOIN services s ON a.service_id=s.id
        LEFT JOIN staff st ON a.staff_id=st.id
        WHERE {where}
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """, params)


@app.route("/appointments")
@login_required
def appointments():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    app_date = request.args.get("date", "").strip()
    where = ["1=1"]
    params = []
    if search:
        where.append("(a.customer_name LIKE ? OR a.mobile LIKE ?)")
        params += [f"%{search}%", f"%{search}%"]
    if status:
        where.append("a.status=?")
        params.append(status)
    if app_date:
        where.append("a.appointment_date=?")
        params.append(app_date)
    rows = appointment_query(" AND ".join(where), tuple(params))
    return render_template("admin/appointments.html", appointments=rows, title="All Appointments")


@app.route("/appointments/today")
@login_required
def today_appointments():
    rows = appointment_query("a.appointment_date=?", (date.today().isoformat(),))
    return render_template("admin/today_appointments.html", appointments=rows, title="Today Appointments")


@app.route("/appointments/pending")
@login_required
def pending_appointments():
    rows = appointment_query("a.status='Pending'")
    return render_template("admin/appointments.html", appointments=rows, title="Pending Appointments")


@app.route("/appointments/completed")
@login_required
def completed_appointments():
    rows = appointment_query("a.status='Completed'")
    return render_template("admin/appointments.html", appointments=rows, title="Completed Appointments")


@app.route("/appointment/<action>/<int:id>")
@login_required
def update_appointment_status(action, id):
    status_map = {"confirm": "Confirmed", "complete": "Completed", "cancel": "Cancelled"}
    if action not in status_map:
        flash("Invalid action.", "danger")
        return redirect(url_for("appointments"))
    execute("UPDATE appointments SET status=? WHERE id=?", (status_map[action], id))
    flash(f"Appointment marked as {status_map[action]}.", "success")
    return redirect(request.referrer or url_for("appointments"))


@app.route("/appointment/delete/<int:id>")
@login_required
def delete_appointment(id):
    execute("DELETE FROM appointments WHERE id=?", (id,))
    flash("Appointment deleted successfully.", "info")
    return redirect(url_for("appointments"))


@app.route("/customers")
@login_required
def customers():
    search = request.args.get("search", "").strip()
    if search:
        rows = query_all("SELECT * FROM customers WHERE name LIKE ? OR mobile LIKE ? ORDER BY id DESC", (f"%{search}%", f"%{search}%"))
    else:
        rows = query_all("SELECT * FROM customers ORDER BY id DESC")
    return render_template("admin/customers.html", customers=rows)


@app.route("/customer/<int:id>")
@login_required
def customer_details(id):
    customer = query_one("SELECT * FROM customers WHERE id=?", (id,))
    if not customer:
        flash("Customer not found.", "danger")
        return redirect(url_for("customers"))
    history = appointment_query("a.mobile=?", (customer["mobile"],))
    return render_template("admin/customer_details.html", customer=customer, history=history)


@app.route("/staff")
@login_required
def staff():
    rows = query_all("SELECT * FROM staff ORDER BY id DESC")
    return render_template("admin/staff.html", staff=rows)


@app.route("/staff/add", methods=["GET", "POST"])
@login_required
def add_staff():
    if request.method == "POST":
        execute("""
            INSERT INTO staff (name, mobile, email, role, specialization, experience, salary, joining_date, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["name"], request.form.get("mobile"), request.form.get("email"), request.form["role"],
            request.form.get("specialization"), request.form.get("experience"), request.form.get("salary") or 0,
            request.form.get("joining_date"), request.form.get("status"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        flash("Staff member added successfully.", "success")
        return redirect(url_for("staff"))
    return render_template("admin/add_staff.html", staff=None)


@app.route("/staff/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_staff(id):
    row = query_one("SELECT * FROM staff WHERE id=?", (id,))
    if request.method == "POST":
        execute("""
            UPDATE staff SET name=?, mobile=?, email=?, role=?, specialization=?, experience=?, salary=?, joining_date=?, status=? WHERE id=?
        """, (request.form["name"], request.form.get("mobile"), request.form.get("email"), request.form["role"], request.form.get("specialization"), request.form.get("experience"), request.form.get("salary") or 0, request.form.get("joining_date"), request.form.get("status"), id))
        flash("Staff member updated successfully.", "success")
        return redirect(url_for("staff"))
    return render_template("admin/edit_staff.html", staff=row)


@app.route("/staff/delete/<int:id>")
@login_required
def delete_staff(id):
    execute("DELETE FROM staff WHERE id=?", (id,))
    flash("Staff member deleted.", "info")
    return redirect(url_for("staff"))


@app.route("/admin/services")
@login_required
def admin_services():
    rows = query_all("SELECT * FROM services ORDER BY id DESC")
    return render_template("admin/services.html", services=rows)


@app.route("/admin/services/add", methods=["GET", "POST"])
@login_required
def add_service():
    if request.method == "POST":
        execute("""
            INSERT INTO services (name, category, description, price, duration, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (request.form["name"], request.form["category"], request.form.get("description"), request.form.get("price") or 0, request.form.get("duration"), request.form.get("status"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        flash("Service added successfully.", "success")
        return redirect(url_for("admin_services"))
    return render_template("admin/add_service.html", service=None)


@app.route("/admin/services/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_service(id):
    row = query_one("SELECT * FROM services WHERE id=?", (id,))
    if request.method == "POST":
        execute("""
            UPDATE services SET name=?, category=?, description=?, price=?, duration=?, status=? WHERE id=?
        """, (request.form["name"], request.form["category"], request.form.get("description"), request.form.get("price") or 0, request.form.get("duration"), request.form.get("status"), id))
        flash("Service updated successfully.", "success")
        return redirect(url_for("admin_services"))
    return render_template("admin/edit_service.html", service=row)


@app.route("/admin/services/delete/<int:id>")
@login_required
def delete_service(id):
    execute("DELETE FROM services WHERE id=?", (id,))
    flash("Service deleted.", "info")
    return redirect(url_for("admin_services"))


@app.route("/bill/generate/<int:appointment_id>", methods=["GET", "POST"])
@login_required
def generate_bill(appointment_id):
    appt = query_one("""
        SELECT a.*, s.name AS service_name, s.price AS service_price, s.id AS sid
        FROM appointments a LEFT JOIN services s ON a.service_id=s.id WHERE a.id=?
    """, (appointment_id,))
    if not appt:
        flash("Appointment not found.", "danger")
        return redirect(url_for("appointments"))
    existing_bill = query_one("SELECT id FROM bills WHERE appointment_id=?", (appointment_id,))
    if existing_bill:
        return redirect(url_for("view_bill", bill_id=existing_bill["id"]))
    if request.method == "POST":
        service_price = float(request.form.get("service_price") or 0)
        extra = float(request.form.get("extra_charges") or 0)
        discount = float(request.form.get("discount") or 0)
        gst = float(request.form.get("gst") or 0)
        subtotal = service_price + extra - discount
        final_amount = subtotal + (subtotal * gst / 100)
        customer = query_one("SELECT * FROM customers WHERE mobile=?", (appt["mobile"],))
        customer_id = customer["id"] if customer else None
        bill_id = execute("""
            INSERT INTO bills (appointment_id, customer_id, service_id, service_price, extra_charges, discount, gst, final_amount, payment_mode, payment_status, bill_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (appointment_id, customer_id, appt["service_id"], service_price, extra, discount, gst, final_amount, request.form["payment_mode"], request.form["payment_status"], date.today().isoformat(), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        execute("UPDATE appointments SET status='Completed' WHERE id=?", (appointment_id,))
        if customer_id:
            execute("UPDATE customers SET total_visits=total_visits+1, total_spend=total_spend+?, last_visit=? WHERE id=?", (final_amount, date.today().isoformat(), customer_id))
        flash("Bill generated successfully.", "success")
        return redirect(url_for("view_bill", bill_id=bill_id))
    return render_template("admin/generate_bill.html", appt=appt)


@app.route("/bill/view/<int:bill_id>")
@login_required
def view_bill(bill_id):
    bill = query_one("""
        SELECT b.*, a.customer_name, a.mobile, a.email, s.name AS service_name
        FROM bills b
        LEFT JOIN appointments a ON b.appointment_id=a.id
        LEFT JOIN services s ON b.service_id=s.id
        WHERE b.id=?
    """, (bill_id,))
    return render_template("admin/view_bill.html", bill=bill)


@app.route("/bill/print/<int:bill_id>")
@login_required
def print_bill(bill_id):
    return redirect(url_for("view_bill", bill_id=bill_id))


@app.route("/reports/revenue")
@login_required
def revenue_report():
    from_date = request.args.get("from_date") or (date.today() - timedelta(days=30)).isoformat()
    to_date = request.args.get("to_date") or date.today().isoformat()
    payment_mode = request.args.get("payment_mode", "")
    where = ["b.bill_date BETWEEN ? AND ?"]
    params = [from_date, to_date]
    if payment_mode:
        where.append("b.payment_mode=?")
        params.append(payment_mode)
    where_sql = " AND ".join(where)
    bills = query_all(f"""
        SELECT b.*, a.customer_name, s.name AS service_name
        FROM bills b
        LEFT JOIN appointments a ON b.appointment_id=a.id
        LEFT JOIN services s ON b.service_id=s.id
        WHERE {where_sql}
        ORDER BY b.bill_date DESC
    """, tuple(params))
    summary = query_one(f"SELECT COALESCE(SUM(final_amount),0) AS total, COUNT(*) AS count FROM bills b WHERE {where_sql}", tuple(params))
    by_service = query_all(f"""
        SELECT s.name AS label, COALESCE(SUM(b.final_amount),0) AS total
        FROM bills b LEFT JOIN services s ON b.service_id=s.id
        WHERE {where_sql} GROUP BY s.name
    """, tuple(params))
    by_mode = query_all(f"SELECT payment_mode AS label, COALESCE(SUM(final_amount),0) AS total FROM bills b WHERE {where_sql} GROUP BY payment_mode", tuple(params))
    return render_template("admin/revenue_report.html", bills=bills, summary=summary, by_service=by_service, by_mode=by_mode, from_date=from_date, to_date=to_date, payment_mode=payment_mode)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
