import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

patients = [
    ("Rahul Sharma", "2000-05-15", "rahul@gmail.com", 95, 15, 120, "Low Risk", "Healthy"),
    ("Priya Singh", "1999-08-21", "priya@gmail.com", 140, 11, 220, "Medium Risk", "Needs monitoring"),
    ("Amit Kumar", "1998-03-10", "amit@gmail.com", 180, 9, 260, "High Risk", "Consult doctor"),
    ("Sneha Patel", "2001-07-12", "sneha@gmail.com", 100, 14, 150, "Low Risk", "Healthy"),
    ("Arjun Rao", "1997-01-25", "arjun@gmail.com", 170, 10, 240, "High Risk", "Requires treatment"),
    ("Kiran Kumar", "2002-11-08", "kiran@gmail.com", 110, 13, 180, "Low Risk", "Healthy"),
    ("Pooja Shetty", "2000-04-17", "pooja@gmail.com", 145, 11, 210, "Medium Risk", "Monitor diet"),
    ("Manoj Bhat", "1995-09-14", "manoj@gmail.com", 190, 8, 280, "High Risk", "Immediate care"),
    ("Divya Rao", "2003-06-20", "divya@gmail.com", 105, 14, 160, "Low Risk", "Healthy"),
    ("Rakesh Gowda", "1996-12-05", "rakesh@gmail.com", 155, 10, 230, "Medium Risk", "Regular checkup")
]

for p in patients:
    cursor.execute("""
        INSERT INTO patients
        (full_name, dob, email, glucose, haemoglobin,
         cholesterol, risk_level, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, p)

conn.commit()
conn.close()

print("10 Demo Patients Added Successfully!")