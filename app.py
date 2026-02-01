from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super-secret"

client = MongoClient("mongodb://localhost:27017/")
db = client["hospital_db"]
users = db["users"]
appointments = db["appointments"]


# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html")


# ================= MAIN PAGES =================
@app.route("/specialities")
def specialities():
    return render_template("specialities.html")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/about")
def about():
    return render_template("about.html")


# ================= AUTH =================
# @app.route("/choose-role")
# def choose_role():
#     return render_template("auth/choose_role.html")

@app.route("/login")
def choose_role():
    return render_template("auth/choose_role.html")

@app.route("/login/patient", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        user = users.find_one({"email": request.form["email"], "role": "patient"})
        if user and check_password_hash(user["password"], request.form["password"]):
            session["user_id"] = str(user["_id"])
            session["role"] = "patient"
            return redirect("/book-appointment")
    return render_template("auth/patient_login.html")

@app.route("/login/doctor", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        user = users.find_one({"email": request.form["email"], "role": "doctor"})
        if user and check_password_hash(user["password"], request.form["password"]):
            session["user_id"] = str(user["_id"])
            session["role"] = "doctor"
            return redirect("/dashboard/doctor")
    return render_template("auth/doctor_login.html")

@app.route("/login/manager", methods=["GET", "POST"])
def manager_login():
    if request.method == "POST":
        user = users.find_one({"email": request.form["email"], "role": "manager"})
        if user and check_password_hash(user["password"], request.form["password"]):
            session["user_id"] = str(user["_id"])
            session["role"] = "manager"
            return redirect("/dashboard/manager")
    return render_template("auth/manager_login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users.insert_one({
            "name": request.form["name"],
            "email": request.form["email"],
            "password": generate_password_hash(request.form["password"]),
            "role": "patient",
            "created_at": datetime.now()
        })
        return redirect("/login")
    return render_template("auth/signup.html")


# ================= APPOINTMENTS =================
@app.route("/book-appointment", methods=["GET", "POST"])
def book_appointment():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        appointments.insert_one({
            "patient_id": session["user_id"],
            "department": request.form["department"],
            "date": request.form["date"],
            "time": request.form["time"],
            "status": "pending",
            "created_at": datetime.now()
        })
        return redirect("/dashboard/patient")

    return render_template("book_appointment.html")


# ================= DEPARTMENTS =================
@app.route("/department/cardiology")
def cardiology():
    return render_template("departments/cardiology.html")

@app.route("/department/neurology")
def neurology():
    return render_template("departments/neurology.html")

@app.route("/department/orthopedics")
def orthopedic():
    return render_template("departments/orthopedics.html")

@app.route("/department/dentistry")
def dental():
    return render_template("departments/dentistry.html")

@app.route("/department/pediatrics")
def pediatrics():
    return render_template("departments/pediatrics.html")


# ================= DASHBOARDS =================
@app.route("/dashboard/patient")
def patient_dashboard():
    return render_template("dashboards/patient_dashboard.html")

@app.route("/dashboard/doctor")
def doctor_dashboard():
    return render_template("dashboards/doctor_dashboard.html")

@app.route("/dashboard/manager")
def manager_dashboard():
    return render_template("dashboards/manager_dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)
