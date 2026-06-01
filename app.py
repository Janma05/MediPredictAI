from flask import Flask, render_template, request, redirect, url_for, flash,Response
import csv
import sqlite3
import pickle
import os
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "medipredict_secret_key"

DATABASE = "database.db"

# -----------------------------
# LOAD ML MODEL
# -----------------------------

with open("model.pkl", "rb") as file:
    model = pickle.load(file)


# -----------------------------
# DATABASE CONNECTION
# -----------------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# CREATE TABLE
# -----------------------------

def create_table():

    conn = get_db_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS patients (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        full_name TEXT NOT NULL,

        dob DATE NOT NULL,

        email TEXT NOT NULL,

        glucose REAL NOT NULL,

        haemoglobin REAL NOT NULL,

        cholesterol REAL NOT NULL,

        risk_level TEXT,

        remarks TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()
    conn.close()


create_table()


# -----------------------------
# EMAIL VALIDATION
# -----------------------------

def validate_email(email):

    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    return re.match(pattern, email)


# -----------------------------
# AI REMARKS
# -----------------------------

def generate_remarks(risk):

    if risk == "Low Risk":
        return (
            "Patient parameters appear normal. "
            "Maintain a healthy lifestyle and continue routine health checkups."
        )

    elif risk == "Medium Risk":
        return (
            "Patient shows moderate risk indicators. "
            "Regular monitoring, healthy diet, and exercise are recommended."
        )

    else:
        return (
            "Patient shows elevated risk indicators. "
            "Immediate medical consultation is advised."
        )


# -----------------------------
# PREDICT RISK
# -----------------------------

def predict_risk(glucose, haemoglobin, cholesterol):

    prediction = model.predict([
        [
            glucose,
            haemoglobin,
            cholesterol
        ]
    ])

    return prediction[0]


# -----------------------------
# DASHBOARD
# -----------------------------

@app.route("/")
@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()

    total_patients = conn.execute(
        "SELECT COUNT(*) FROM patients"
    ).fetchone()[0]

    low_risk = conn.execute(
        "SELECT COUNT(*) FROM patients WHERE risk_level='Low Risk'"
    ).fetchone()[0]

    medium_risk = conn.execute(
        "SELECT COUNT(*) FROM patients WHERE risk_level='Medium Risk'"
    ).fetchone()[0]

    high_risk = conn.execute(
        "SELECT COUNT(*) FROM patients WHERE risk_level='High Risk'"
    ).fetchone()[0]

    recent_patients = conn.execute("""
        SELECT *
        FROM patients
        ORDER BY created_at DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_patients=total_patients,
        low_risk=low_risk,
        medium_risk=medium_risk,
        high_risk=high_risk,
        recent_patients=recent_patients
    )


# -----------------------------
# PATIENT LIST
# -----------------------------

@app.route("/patients")
def patients():

    search = request.args.get("search", "")

    conn = get_db_connection()

    patients = conn.execute("""
        SELECT *
        FROM patients
        WHERE full_name LIKE ?
             OR email LIKE ?               
        ORDER BY created_at DESC
    """, (f"%{search}%",f"%{search}%")).fetchall()

    conn.close()

    return render_template(
        "patients.html",
        patients=patients,
        search=search
    )


# -----------------------------
# ADD PATIENT
# -----------------------------

@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():

    if request.method == "POST":

        full_name = request.form["full_name"].strip()
        dob = request.form["dob"]
        email = request.form["email"].strip()

        glucose = request.form["glucose"]
        haemoglobin = request.form["haemoglobin"]
        cholesterol = request.form["cholesterol"]

        # VALIDATIONS

        if not full_name:
            flash("Full Name is required", "danger")
            return redirect(url_for("add_patient"))

        if not validate_email(email):
            flash("Invalid Email Address", "danger")
            return redirect(url_for("add_patient"))

        if datetime.strptime(dob, "%Y-%m-%d").date() > datetime.today().date():
            flash("Date of Birth cannot be in the future", "danger")
            return redirect(url_for("add_patient"))

        try:

            glucose = float(glucose)
            haemoglobin = float(haemoglobin)
            cholesterol = float(cholesterol)

            if glucose <= 0 or haemoglobin <= 0 or cholesterol <= 0:

                flash("Values must be greater than zero", "danger")
                return redirect(url_for("add_patient"))

        except:

            flash("Numeric values required", "danger")
            return redirect(url_for("add_patient"))

        risk_level = predict_risk(
            glucose,
            haemoglobin,
            cholesterol
        )

        remarks = generate_remarks(risk_level)

        conn = get_db_connection()

        conn.execute("""
        INSERT INTO patients
        (
            full_name,
            dob,
            email,
            glucose,
            haemoglobin,
            cholesterol,
            risk_level,
            remarks
        )
        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            full_name,
            dob,
            email,
            glucose,
            haemoglobin,
            cholesterol,
            risk_level,
            remarks
        ))

        conn.commit()
        conn.close()

        flash(
            "Patient Added Successfully",
            "success"
        )

        return redirect(url_for("patients"))

    return render_template("add_patient.html")


# -----------------------------
# EDIT PATIENT
# -----------------------------

@app.route("/edit_patient/<int:id>", methods=["GET", "POST"])
def edit_patient(id):

    conn = get_db_connection()

    patient = conn.execute(
        "SELECT * FROM patients WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        full_name = request.form["full_name"]
        dob = request.form["dob"]
        email = request.form["email"]

        glucose = float(request.form["glucose"])
        haemoglobin = float(request.form["haemoglobin"])
        cholesterol = float(request.form["cholesterol"])

        risk_level = predict_risk(
            glucose,
            haemoglobin,
            cholesterol
        )

        remarks = generate_remarks(
            risk_level
        )

        conn.execute("""
        UPDATE patients
        SET

        full_name=?,
        dob=?,
        email=?,
        glucose=?,
        haemoglobin=?,
        cholesterol=?,
        risk_level=?,
        remarks=?

        WHERE id=?

        """,
        (
            full_name,
            dob,
            email,
            glucose,
            haemoglobin,
            cholesterol,
            risk_level,
            remarks,
            id
        ))

        conn.commit()
        conn.close()

        flash(
            "Patient Updated Successfully",
            "success"
        )

        return redirect(url_for("patients"))

    conn.close()

    return render_template(
        "edit_patient.html",
        patient=patient
    )


# -----------------------------
# DELETE PATIENT
# -----------------------------

@app.route("/delete_patient/<int:id>")
def delete_patient(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM patients WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash(
        "Patient Deleted Successfully",
        "warning"
    )

    return redirect(url_for("patients"))

@app.route('/view_patient/<int:patient_id>')
def view_patient(patient_id):

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE id=?
    """, (patient_id,))

    patient = cursor.fetchone()

    conn.close()

    return render_template(
        'view_patient.html',
        patient=patient
    )

# -----------------------------
# EXPORT CSV
# -----------------------------

@app.route("/export_csv")
def export_csv():

    conn = get_db_connection()

    patients = conn.execute("""
        SELECT *
        FROM patients
        ORDER BY created_at DESC
    """).fetchall()

    conn.close()

    def generate():

        yield "ID,Name,DOB,Email,Glucose,Haemoglobin,Cholesterol,Risk Level,Remarks\n"

        for p in patients:

            yield (
                f"{p['id']},"
                f"{p['full_name']},"
                f"{p['dob']},"
                f"{p['email']},"
                f"{p['glucose']},"
                f"{p['haemoglobin']},"
                f"{p['cholesterol']},"
                f"{p['risk_level']},"
                f"{p['remarks']}\n"
            )

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=patients.csv"
        }
    )
# -----------------------------
# RUN APP
# -----------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )