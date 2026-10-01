# app.py - Flask backend for the Hospital Management Appointment System
import sqlite3, re, uuid
from datetime import date
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)
DB = "hospital.db"

# Doctor list (kept in Python so it is easy to edit)
DOCTORS = [
    {"name": "Dr. Anil Sharma", "dept": "General Medicine", "exp": 12, "days": "Mon - Fri", "time": "9:00 AM - 1:00 PM"},
    {"name": "Dr. Priya Nair", "dept": "Cardiology", "exp": 15, "days": "Mon, Wed, Fri", "time": "10:00 AM - 4:00 PM"},
    {"name": "Dr. Rahul Mehta", "dept": "Dermatology", "exp": 8, "days": "Tue, Thu, Sat", "time": "11:00 AM - 3:00 PM"},
    {"name": "Dr. Sneha Iyer", "dept": "Pediatrics", "exp": 10, "days": "Mon - Sat", "time": "9:00 AM - 2:00 PM"},
    {"name": "Dr. Karan Patel", "dept": "Orthopedics", "exp": 14, "days": "Tue, Thu, Fri", "time": "2:00 PM - 6:00 PM"},
]

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates hospital.db and the appointments table if they do not exist."""
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            patient_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            doctor TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending')""")

def validate(d):
    """Returns an error message, or None if the data is valid."""
    for f in ["patient_name", "age", "gender", "phone", "email", "department",
              "doctor", "appointment_date", "appointment_time", "symptoms"]:
        if not str(d.get(f, "")).strip():
            return f.replace("_", " ").title() + " is required."
    if not str(d["age"]).isdigit() or not (0 < int(d["age"]) < 121):
        return "Enter a valid age (1-120)."
    if not re.fullmatch(r"\d{10}", d["phone"]):
        return "Phone number must be 10 digits."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", d["email"]):
        return "Enter a valid email address."
    if d["appointment_date"] < date.today().isoformat():
        return "Appointment date cannot be in the past."
    return None

@app.route("/")
def home():
    return render_template("index.html", doctors=DOCTORS)

@app.route("/doctors")
def doctors():
    return render_template("doctors.html", doctors=DOCTORS)

@app.route("/appointment")
def appointment():
    return render_template("appointment.html", doctors=DOCTORS,
                           today=date.today().isoformat())

@app.route("/book", methods=["POST"])
def book():
    data = request.get_json(force=True)
    error = validate(data)
    if error:
        return jsonify(success=False, message=error), 400
    appt_id = "APT" + uuid.uuid4().hex[:6].upper()
    with get_db() as conn:
        conn.execute("INSERT INTO appointments VALUES (?,?,?,?,?,?,?,?,?,?,?,'Pending')",
            (appt_id, data["patient_name"].strip(), int(data["age"]), data["gender"],
             data["phone"], data["email"], data["department"], data["doctor"],
             data["appointment_date"], data["appointment_time"], data["symptoms"].strip()))
    return jsonify(success=True, appointment_id=appt_id,
                   message="Appointment booked successfully.")

@app.route("/admin")
def admin():
    today = date.today().isoformat()
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM appointments ORDER BY appointment_date DESC, appointment_time").fetchall()
        one = lambda q, *a: conn.execute(q, a).fetchone()[0]
        stats = {
            "total": one("SELECT COUNT(*) FROM appointments"),
            "today": one("SELECT COUNT(*) FROM appointments WHERE appointment_date=?", today),
            "pending": one("SELECT COUNT(*) FROM appointments WHERE status='Pending'"),
            "completed": one("SELECT COUNT(*) FROM appointments WHERE status='Completed'"),
        }
    return render_template("admin.html", appointments=rows, stats=stats)

@app.route("/admin/status/<appt_id>/<status>", methods=["POST"])
def update_status(appt_id, status):
    if status in ("Confirmed", "Completed", "Cancelled"):
        with get_db() as conn:
            conn.execute("UPDATE appointments SET status=? WHERE id=?", (status, appt_id))
    return redirect(url_for("admin"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
