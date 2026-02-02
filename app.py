from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# import os,json

app = Flask(__name__)
app.secret_key = "super-secret"

# 
def pages (pagNum,Collname):
    page = int(request.args.get('page',1))
    per_page = pagNum
    skip_among=(page-1)*per_page
    allItems = list(Collname.find().sort('_id',-1).skip(skip_among).limit(per_page))
    total=Collname.count_documents({})
    has_next =total>(page*per_page)
    return allItems,has_next ,page

client = MongoClient("mongodb://localhost:2009/")
db = client["healthcare_db"]
users = db["users"]
appointments = db["appointments"]
patients = db["patients"]
operations = db["operations"]
doctors = db["doctors"]
news = db["news"]
departments = db["departments"]
admin = db["admin"]


# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html")


# ================= MAIN PAGES =================
@app.route("/specialities")
def specialities():
    return render_template("specialities.html")

@app.route("/about")
def about():
    return render_template("about.html")

#=====================================

@app.route("/news")
def news_page():
    page = int(request.args.get('page',1))
    # per_page = 10
    skip_among=(page-1)*10
    allItem = list(news.find().sort('_id',-1).skip(skip_among).limit(10))
    total=news.count_documents({})
    has_next =total>(page*10)
    # nextpage=pages (6,news)
    # return render_template("news.html",Pnews=nextpage.allItem,current=nextpage.page,has_next=nextpage.has_next)
    return render_template("news.html",Pnews=allItem,current=page,has_next= has_next)

# ================= AUTH =================
# @app.route("/choose-role")
# def choose_role():
#     return render_template("auth/choose_role.html")

@app.route("/login")
def choose_role():
    return render_template("auth/choose_role.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/login/patient", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        user = users.find_one({"email": request.form["email"], "role": "patient"})
        # check=check_password_hash(user["password"], request.form["password"]) or request.form["password"] == user["password"]
        if user:
            password_input=request.form["password"]
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
        return redirect("/login/patient")
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

    return render_template("index.html")


# ================= DEPARTMENTS =================
@app.route("/department/cardiology")
def cardiology():
    query = {
  "mainSpecialty": {'$in':[
      "Interventional Cardiologist",'Heart Failure Specialist',
  'Interventional Cardiologist',
  ] }
}
    cardiology_doctors = list(doctors.find(query))
    return render_template("departments/cardiology.html", cDoctors=cardiology_doctors)

@app.route("/department/neurology")
def neurology():
    query = {
   
  'mainSpecialty': {
    '$in': ['Neurologist', 'Epileptologist']
                    }
            }
    neurology_doctors = list(doctors.find(query))
    return render_template("departments/neurology.html", cDoctors=neurology_doctors)

@app.route("/department/orthopedics")
def orthopedic():
    query = {
    'mainSpecialty': {
        '$in': [
            'Spine Surgeon',  'Orthopedic Surgeon',
        ]
    }
}
    orthopedics_doctors = list(doctors.find(query))
    return render_template("departments/orthopedics.html", cDoctors=orthopedics_doctors)

@app.route("/department/dentistry")
def dental():
    query = {
  'mainSpecialty': {
    '$in': [
        'Periodontist', 'Dentist',
    ]
}
}
    dentistry_doctors = list(doctors.find(query))
    return render_template("departments/dentistry.html", cDoctors=dentistry_doctors)

@app.route("/department/pediatrics")
def pediatrics():
    query = {
  'mainSpecialty': {
    '$in': [
        'Pediatrician', 'Pediatric Cardiologist',
  'Pediatric Neurologist'
    ]
}
}
    pediatrics_doctors = list(doctors.find(query))
    return render_template("departments/pediatrics.html", cDoctors=pediatrics_doctors)


# ================= DASHBOARDS =================
@app.route("/dashboard/patient")
def patient_dashboard():
    def patient_dashboard():
        if "user_id" not in session or session.get("role") != "patient":
            return redirect("/login")

    user_id = session["user_id"]
   
    upcoming_appts = list(appointments.find({
        "patient_id": user_id,
        "status": "scheduled"
    }).sort("date", 1))

    past_appts = list(appointments.find({
        "patient_id": user_id,
        "status": {"$in": ["completed", "cancelled"]}
    }).sort("date", -1))

    return render_template("dashboards/patient_dashboard.html",
    upcoming=upcoming_appts,history=past_appts)

@app.route("/dashboard/doctor")
def doctor_dashboard():
    return render_template("dashboards/doctor_dashboard.html")

# ================= ADMIN =================
@app.route("/dashboard/manager")
def manager_dashboard():
    return render_template("admin/manager_dashboard.html")

@app.route("/admin/add-user", methods=["POST"])
def add_user():
    users.insert_one({
        "name": request.form["name"],
        "email": request.form["email"],
        "role": request.form["role"]
    })
    return redirect("/dashboard/manager")

@app.route("/admin/create-db", methods=["POST"])
def create_db():
    db_name = request.form["db_name"]
    client[db_name]
    return redirect("/dashboard/manager")

@app.route("/admin/collections")
def show_collections():
    cols = db.list_collection_names()
    return {"collections": cols}

if __name__ == "__main__":
    app.run(debug=True, port=2009)
