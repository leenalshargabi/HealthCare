import math
from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from datetime import timedelta
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

client = MongoClient("mongodb://localhost:27017/")
db = client["healthcare_db"]
users = db["users"]
appointments = db["appointments"]
patients = db["patients"]
operations_coll = db["operations"]
doctors = db["doctors"]
news = db["news"]
departments = db["departments"]
admin = db["admin"]
rooms_coll = db["rooms"]
emergency_rooms = db["rooms"]


# ================= HOME =================
@app.route("/")
def home():
    total_patients = operations_coll.count_documents({}) 

    total_rooms = rooms_coll.count_documents({})

    total_er = rooms_coll.count_documents({"category": "Service/ER"})

    return render_template("index.html", 
                           patients_count=total_patients, 
                           rooms_count=total_rooms, 
                           er_count=total_er)

# ================= MAIN PAGES =================
@app.route("/specialities")
def specialities():
    return render_template("specialities.html")

@app.route("/about")
def about():
    return render_template("about.html")



# SURGERIES PAGE
@app.route("/surgeries")
def surgeries():
    page = int(request.args.get('page', 1))
    per_page = 10
    q_doctor = request.args.get('doctor', '').strip()
    q_date = request.args.get('date', '').strip()
    order = int(request.args.get('order', -1))

    query = {}

    if q_doctor:
        query["doctor.fullName"] = {"$regex": q_doctor, "$options": "i"}

    if q_date:
        try:
            start_date = datetime.strptime(q_date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
            query["scheduling.startTime"] = {"$gte": start_date, "$lt": end_date}
        except ValueError:
            pass

    projection = {
        "operationCode": 1,
        "patient.fullName": 1,
        "doctor.fullName": 1,
        "medicalDetails.procedure": 1,
        "scheduling.room": 1,
        "scheduling.startTime": 1,
        "status": 1,
        "_id": 0
    }

    total = operations_coll.count_documents(query)
    total_pages = math.ceil(total / per_page)
    skip = (page - 1) * per_page

    ops_data = list(operations_coll.find(query, projection)
                                   .sort('scheduling.startTime', order)
                                   .skip(skip)
                                   .limit(per_page))

    return render_template("surgeries.html", 
                           operations=ops_data, 
                           current=page, 
                           has_next=(page < total_pages), 
                           total_pages=total_pages,
                           q_doctor=q_doctor, 
                           q_date=q_date, 
                           order=order)

# ROOMS PAGE
@app.route("/rooms")
def rooms():
    page = int(request.args.get('page', 1))
    per_page = 10
    q_room = request.args.get('roomNumber', '').strip()
    q_floor = request.args.get('floor', '').strip()
    sort_by = request.args.get('sort', 'roomNumber')
    order = int(request.args.get('order', 1))

    projection = {
        "roomNumber": 1,
        "floor": 1,
        "departmentName": 1,
        "roomType": 1,
        "category": 1,   
        "roomName": 1,   
        "status": 1,
        "metadata": 1,   
        "_id": 0         
    }

    query = {}
    if q_room: query["roomNumber"] = {"$regex": q_room, "$options": "i"}
    if q_floor:
        try: query["floor"] = int(q_floor)
        except: pass

    total = rooms_coll.count_documents(query)
    total_pages = math.ceil(total / per_page) 
    
    skip = (page - 1) * per_page
    rooms_data = list(rooms_coll.find(query, projection).sort(sort_by, order).skip(skip).limit(per_page))

    return render_template("rooms.html", 
                           rooms=rooms_data, 
                           current=page, 
                           has_next=(page < total_pages), 
                           total_pages=total_pages,
                           q_room=q_room, 
                           q_floor=q_floor, 
                           sort_by=sort_by, 
                           order=order)

# EMERGENCY ROOMS 
@app.route("/EmergencyRoomspython")
def emergencyrooms():
    page = int(request.args.get('page', 1))
    per_page = 10
    query = {"category": "Service/ER"} 
    
    total = rooms_coll.count_documents(query)
    total_pages = math.ceil(total / per_page)
    
    skip = (page - 1) * per_page
    rooms_data = list(rooms_coll.find(query).skip(skip).limit(per_page))

    return render_template("EmergencyRooms.html", rooms=rooms_data, 
                           current=page, has_next=(page < total_pages), 
                           total_pages=total_pages)

# NEWS PAGE
@app.route("/news")
def news_page():

    page = int(request.args.get('page', 1))
    sort_type = request.args.get('sort', 'new')
    query_text = request.args.get('q', '').strip()

    # sort direction
    direction = -1 if sort_type == 'new' else 1

    # pagination
    per_page = 6
    skip_amount = (page - 1) * per_page

    # search query
    query = {}

    if query_text:
        query["$or"] = [
            {"title": {"$regex": query_text, "$options": "i"}},
            {"summary": {"$regex": query_text, "$options": "i"}},
            {"category": {"$regex": query_text, "$options": "i"}},
            {"author": {"$regex": query_text, "$options": "i"}}
        ]

    # fetch news
    all_items = list(
        news.find(query)
        .sort("publishDate", direction)
        .skip(skip_amount)
        .limit(per_page)
    )

    total = news.count_documents(query)
    has_next = total > (page * per_page)

    return render_template(
        "news.html",
        Pnews=all_items,
        current=page,
        has_next=has_next,
        sort_type=sort_type,
        query_text=query_text
    )


# ================= AUTH =================
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
        email = request.form["email"]
        password_input = request.form["password"]
        user = users.find_one({"email": email, "role": "patient"})
        if user:
            if check_password_hash(user["password"], password_input) or password_input == user["password"]:
                session["user_id"] = str(user["_id"])
                session["role"] = "patient"
                session["name"] = user.get("name", "Patient")
                return redirect("/")
            else:
                return "Invalid password. Please try again."
        else:
            return "Email not found. Please register first."
           
    return render_template("auth/patient_login.html")

@app.route("/login/doctor", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        email = request.form["email"]
        password_input = request.form["password"]
        user = users.find_one({"email": email, "role": "doctor"})
        if user:
            if check_password_hash(user["passwordHash"], password_input) or password_input == user["passwordHash"]:
                session["user_id"] = str(user["_id"])
                session["role"] = "doctor"
                session["name"] = user.get("name", "doctor")
                return redirect("/")
            else:
                return "Invalid password. Please try again."
        else:
            return "Email not found. Please register first."

    return render_template("auth/doctor_login.html")

@app.route("/login/manager", methods=["GET", "POST"])
def manager_login():
    if request.method == "POST":
        email = request.form["email"]
        password_input = request.form["password"]
        user = users.find_one({"email": email, "role": "manager"})
        if user:
            if check_password_hash(user["password"], password_input) or password_input == user["password"]:
                session["user_id"] = str(user["_id"])
                session["role"] = "manager"
                session["name"] = user.get("name", "manager")
                return redirect("/")
            else:
                return "Invalid password. Please try again."
        else:
            return "Email not found. Please register first."
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
        dept = request.form["department"]
        available_slots = ["09:00 AM", "10:00 AM", "11:00 AM", "01:00 PM", "02:00 PM"]
        today_date = datetime.now().strftime("%Y-%m-%d")
       
        doctor = doctors.find_one({"mainSpecialty": {"$regex": dept, "$options": "i"}})
       
        if not doctor:
            return "No doctor available in this department currently."

        booked_slots = appointments.distinct("time", {"doctor_id": str(doctor["_id"]), "date": today_date})
       
        assigned_time = None
        for slot in available_slots:
            if slot not in booked_slots:
                assigned_time = slot
                break
       
        if not assigned_time:
            return "All slots for today are fully booked. Please try tomorrow."

        # 3. تنفيذ الحجز في كولكشن appointments
        appointments.insert_one({
            "patient_id": session["user_id"],
            "doctor_id": str(doctor["_id"]),
            "doctor_name": doctor["fullName"],
            "department": dept,
            "date": today_date,
            "time": assigned_time,
            "status": "pending",
            "created_at": datetime.now()
        })
        return redirect("/dashboard/patient")

    return render_template("book_appointment.html")


# ================= DEPARTMENTS =================
@app.route("/department/cardiology")
def cardiology():
    query = {  "mainSpecialty": {'$in':[
      "Interventional Cardiologist",'Heart Failure Specialist',
  'Interventional Cardiologist',  ] }}
    
    page = int(request.args.get('page',1))
    skip_among=(page-1)*6
    cardiology_doctors = list(doctors.find(query).skip(skip_among).limit(6))
    total=doctors.count_documents({})
    has_next =total>(page*6)
    return render_template("departments/cardiology.html", cDoctors=cardiology_doctors,current=page,has_next= has_next)

@app.route("/department/neurology")
def neurology():
    query = {  'mainSpecialty': {
    '$in': ['Neurologist', 'Epileptologist']                    }            }
    
    page = int(request.args.get('page',1))
    skip_among=(page-1)*6
    neurology_doctors = list(doctors.find(query).skip(skip_among).limit(6))
    total=doctors.count_documents({})
    has_next =total>(page*6)

    return render_template("departments/neurology.html", cDoctors=neurology_doctors,current=page,has_next= has_next)

@app.route("/department/orthopedics")
def orthopedic():
    query = {    'mainSpecialty': {
        '$in': [
            'Spine Surgeon',  'Orthopedic Surgeon',        ]    }}
    
    page = int(request.args.get('page',1))
    skip_among=(page-1)*6
    orthopedics_doctors = list(doctors.find(query).skip(skip_among).limit(6))
    total=doctors.count_documents({})
    has_next =total>(page*6)
    return render_template("departments/orthopedics.html", cDoctors=orthopedics_doctors,current=page,has_next= has_next)

@app.route("/department/dentistry")
def dental():
    query = { 'mainSpecialty': {
    '$in': [
        'Periodontist', 'Dentist', ]}}

    page = int(request.args.get('page',1))
    skip_among=(page-1)*6
    dentistry_doctors = list(doctors.find(query).skip(skip_among).limit(6))
    total=doctors.count_documents({})
    has_next =total>(page*6)
    return render_template("departments/dentistry.html", cDoctors=dentistry_doctors,current=page,has_next= has_next)

@app.route("/department/pediatrics")
def pediatrics():
    query = {  'mainSpecialty': {
    '$in': [
        'Pediatrician', 'Pediatric Cardiologist',
  'Pediatric Neurologist'    ]}}
    page = int(request.args.get('page',1))
    skip_among=(page-1)*6
    pediatrics_doctors = list(doctors.find(query).skip(skip_among).limit(6))
    total=doctors.count_documents({})
    has_next =total>(page*6)
    return render_template("departments/pediatrics.html", cDoctors=pediatrics_doctors,current=page,has_next= has_next)


# ================= DASHBOARDS =================
@app.route("/dashboard/patient")
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
    app.run(debug=True, port=5000)
