import math
from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from datetime import timedelta
from bson import ObjectId
import matplotlib
matplotlib.use('Agg')  # مهم لبيئة الخادم
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import os,json
# 
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

client = MongoClient("mongodb://localhost:5000/")
db = client["healthcare_db"]
users_coll = db["users"]
appointments_coll = db["appointments"]
patients_coll = db["patients"]
operations_coll = db["operations"]
doctors_coll = db["doctors"]
news_coll = db["news"]
departments_coll = db["departments"]
admin_coll = db["admin"]
rooms_coll = db["rooms"]
emergency_rooms = db["rooms"]
notifications_coll = db["notifications"]


# ================= HOME =================
@app.route("/")
def home():
    current_role = session.get("role")
    
    total_patients = operations_coll.count_documents({}) 
    total_rooms = rooms_coll.count_documents({})
    total_er = rooms_coll.count_documents({"category": "Service/ER"})

    return render_template("index.html", 
                           patients_count=total_patients, 
                           rooms_count=total_rooms, 
                           er_count=total_er,
                           role=current_role)
    
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
    if session.get("role") != "doctor":
        return redirect("/")
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
    if session.get("role") != "doctor":
        return redirect("/")
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
@app.route("/EmergencyRooms")
def emergencyrooms():
    if session.get("role") != "doctor":
        return redirect("/")
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
        news_coll.find(query)
        .sort("publishDate", direction)
        .skip(skip_amount)
        .limit(per_page)
    )

    total = news_coll.count_documents(query)
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
# Login Page
@app.route("/login")
def choose_role():
    return render_template("auth/choose_role.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Patient Login Page
@app.route("/login/patient", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password_input = request.form.get("password")
        
        user = users_coll.find_one({"email": email, "role": "patient"})
        
        if user:
            stored_password = user.get("passwordHash") or user.get("password")
            
            if stored_password and (check_password_hash(stored_password, password_input) or password_input == stored_password):
                
                patient_profile = patients_coll.find_one({"email": email})
                
                if patient_profile:
                    session["user_id"] = str(patient_profile["_id"]) 
                    session["role"] = "patient"
                    session["name"] = patient_profile.get("fullName", "Patient")
                    return redirect("/dashboard/patient")
                else:
                    return "Error: Account exists, but no medical profile is associated with this email in patient records."
            else:
                return "Incorrect password."
        else:
            return "Email not found, please register first."
            
    return render_template("auth/patient_login.html")

#login doctor page
@app.route("/login/doctor", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        email_input = request.form.get("email").strip().lower()
        password_input = request.form.get("password")
        
        user = users_coll.find_one({"email": email_input, "role": "doctor"})
        
        if user:
            stored_hash = user.get("passwordHash")
            if check_password_hash(stored_hash, password_input) or stored_hash == password_input:
                
                doctor_profile = doctors_coll.find_one({"email": email_input})
                
                if doctor_profile:
                    session["user_id"] = str(doctor_profile["_id"]) 
                    session["role"] = "doctor"
                    session["name"] = doctor_profile.get("fullName", "Doctor")
                    
                    return redirect("/dashboard/doctor")
                else:
                    return "Error: Your account exists, but you do not have a medical profile in the doctors database."
            else:
                return "Password is not correct."
        else:
            return "This account not found in doctor "
            
    return render_template("auth/doctor_login.html")

#login manager page
@app.route("/login/manager", methods=["GET", "POST"])
def manager_login():
    if request.method == "POST":
        email_input = request.form.get("email").strip().lower()
        password_input = request.form.get("password")
        
        user = users_coll.find_one({"email": email_input, "role": "admin"})
        
        if user:
            if check_password_hash(user.get("passwordHash"), password_input):
                session["user_id"] = str(user["_id"])
                session["role"] = "admin"
                session["name"] = user.get("fullName", "Admin")
                return redirect("/dashboard/manager")
            else:
                return "Password is not correct."
        else:
            return "Manager account not found"
            
    return render_template("auth/manager_login.html")
#Signup Page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users_coll.insert_one({
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
    if "user_id" not in session: return redirect("/login/patient")

    if request.method == "POST":
        selected_dept_name = request.form.get("department", "").strip()
        
        # نأخذ أول 5 أحرف من اختيار المستخدم لزيادة مرونة البحث
        # مثلاً: Cardio بدلاً من Cardiology
        short_name = selected_dept_name[:5] 

        # 1. البحث المرن في تخصصات الأطباء
        # $regex مع options: 'i' تعني بحث غير حساس لحالة الأحرف ويقبل جزء من الكلمة
        dept_doctors = list(doctors_coll.find({
            "mainSpecialty": {"$regex": short_name, "$options": "i"}
        }))

        # 2. إذا لم نجد (احتياطاً)، نبحث في اسم القسم المربوط
        if not dept_doctors:
            search_pipeline = [
                {"$lookup": {"from": "departments", "localField": "departmentId", "foreignField": "_id", "as": "dept"}},
                {"$unwind": "$dept"},
                {"$match": {"dept.name": {"$regex": short_name, "$options": "i"}}}
            ]
            dept_doctors = list(doctors_coll.aggregate(search_pipeline))

        if not dept_doctors:
            return render_template("book_appointment.html", error=f"No specialist found for {selected_dept_name}")

        # نأخذ ID القسم من أول طبيب وجدناه لتوثيق الموعد
        dept_id = dept_doctors[0].get("departmentId")

        # 3. محرك البحث الزمني (60 يوم)
        found_slot = False
        available_hours = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]
        
        for day_offset in range(1, 61): 
            target_date = datetime.now() + timedelta(days=day_offset)
            target_day_name = target_date.strftime("%A")

            for hour in available_hours:
                target_datetime = datetime.strptime(f"{target_date.strftime('%Y-%m-%d')} {hour}", "%Y-%m-%d %H:%M")
                
                for doctor in dept_doctors:
                    # أ- فحص أيام العمل
                    if target_day_name not in doctor.get("workingDays", []): 
                        continue
                    
                    # ب- فحص تعارض المواعيد الحالية
                    existing_app = appointments_coll.find_one({
                        "doctorId": doctor["_id"],
                        "appointmentDate": target_datetime,
                        "status": {"$ne": "cancelled"}
                    })
                    if existing_app: continue

                    # ج- فحص تعارض العمليات الجراحية
                    existing_op = operations_coll.find_one({
                        "doctor.fullName": doctor["fullName"], 
                        "scheduling.startTime": {"$lte": target_datetime}, 
                        "scheduling.endTime": {"$gt": target_datetime}
                    })
                    if existing_op: continue

                    # 4. تنفيذ الحجز الفعلي عند إيجاد أول "فتحة" زمنية
                    new_appointment = {
                        "appointmentCode": f"APT-{datetime.now().strftime('%M%S%f')[:8]}",
                        "patientId": ObjectId(session["user_id"]),
                        "doctorId": doctor["_id"],
                        "departmentId": dept_id,
                        "appointmentDate": target_datetime,
                        "status": "scheduled",
                        "createdAt": datetime.now()
                    }
                    appointments_coll.insert_one(new_appointment)
                    found_slot = True
                    break
                if found_slot: break
            if found_slot: break

        if found_slot:
            return redirect("/dashboard/patient")
        
        return "Sorry, no available slots found in the next 60 days."

    return render_template("book_appointment.html")


# ================= DEPARTMENTS =================
@app.route("/department/cardiology")
def cardiology():
    specialties = ['Interventional Cardiologist', 'Heart Failure Specialist']
    query = {"mainSpecialty": {'$in': specialties}}
    
    page = int(request.args.get('page', 1))
    per_page = 6
    skip_among = (page - 1) * per_page
    
    cardiology_doctors = list(doctors_coll.find(query).skip(skip_among).limit(per_page))
    total = doctors_coll.count_documents(query)
    has_next = total > (page * per_page)
    
    return render_template("departments/cardiology.html", 
                           cDoctors=cardiology_doctors, 
                           current=page, 
                           has_next=has_next)

@app.route("/department/neurology")
def neurology():
    query = {'mainSpecialty': {'$in': ['Neurologist', 'Epileptologist']}}
    
    page = int(request.args.get('page', 1))
    per_page = 6
    skip_among = (page - 1) * per_page
    
    neurology_doctors = list(doctors_coll.find(query).skip(skip_among).limit(per_page))
    total = doctors_coll.count_documents(query)
    has_next = total > (page * per_page)
    
    return render_template("departments/neurology.html", 
                           cDoctors=neurology_doctors, 
                           current=page, 
                           has_next=has_next)

@app.route("/department/orthopedics")
def orthopedic():
    query = { 
        'mainSpecialty': {
            '$in': ['Spine Surgeon', 'Orthopedic Surgeon']
        }
    }
    
    page = int(request.args.get('page', 1))
    per_page = 6
    skip_among = (page - 1) * per_page
    
    orthopedics_doctors = list(doctors_coll.find(query).skip(skip_among).limit(per_page))
    total = doctors_coll.count_documents(query)
    has_next = total > (page * per_page)
    
    return render_template("departments/orthopedics.html", 
                           cDoctors=orthopedics_doctors, 
                           current=page, 
                           has_next=has_next)

@app.route("/department/dentistry")
def dental():
    query = {'mainSpecialty': {'$in': ['Periodontist', 'Dentist']}}

    page = int(request.args.get('page', 1))
    per_page = 6
    skip_among = (page - 1) * per_page
    
    dentistry_doctors = list(doctors_coll.find(query).skip(skip_among).limit(per_page))
    total = doctors_coll.count_documents(query)
    has_next = total > (page * per_page)
    
    return render_template("departments/dentistry.html", 
                           cDoctors=dentistry_doctors, 
                           current=page, 
                           has_next=has_next)

@app.route("/department/pediatrics")
def pediatrics():
    query = {
        'mainSpecialty': {
            '$in': ['Pediatrician', 'Pediatric Cardiologist', 'Pediatric Neurologist']
        }
    }
    
    page = int(request.args.get('page', 1))
    per_page = 6
    skip_among = (page - 1) * per_page
    
    pediatrics_doctors = list(doctors_coll.find(query).skip(skip_among).limit(per_page))
    total = doctors_coll.count_documents(query)
    has_next = total > (page * per_page)
    
    return render_template("departments/pediatrics.html", 
                           cDoctors=pediatrics_doctors, 
                           current=page, 
                           has_next=has_next)


# ================= DASHBOARDS =================
# Patient Dashboard
# ================= DASHBOARD =================
@app.route("/dashboard/patient")
def patient_dashboard():
    if "user_id" not in session or session.get("role") != "patient":
        return redirect("/login/patient")
        
    patient_id = ObjectId(session["user_id"])
    now = datetime.now()
    
    pipeline = [
        {"$match": {"patientId": patient_id}},
        {
            "$lookup": {
                "from": "doctors",
                "localField": "doctorId",
                "foreignField": "_id",
                "as": "doctor_info"
            }
        },
        {"$unwind": "$doctor_info"},
        {
            "$lookup": {
                "from": "departments",
                "localField": "doctor_info.departmentId", # تأكد من المسار الصحيح للـ ID
                "foreignField": "_id",
                "as": "dept_info"
            }
        },
        {"$unwind": {"path": "$dept_info", "preserveNullAndEmptyArrays": True}},
        {"$sort": {"appointmentDate": 1}}
    ]
    
    raw_appointments = list(appointments_coll.aggregate(pipeline))
    upcoming, history = [], []

    for appt in raw_appointments:
        data = {
            "appointmentCode": appt.get("appointmentCode", "N/A"),
            "doctor_name": appt["doctor_info"].get("fullName"),
            "department": appt["dept_info"].get("name") if appt.get("dept_info") else appt["doctor_info"].get("mainSpecialty"),
            "date": appt["appointmentDate"].strftime("%Y-%m-%d"),
            "time": appt["appointmentDate"].strftime("%I:%M %p"),
            "status": appt.get("status", "scheduled"),
            "floor": "Main Clinic" 
        }
        
        if appt["appointmentDate"] >= now and appt["status"] == "scheduled":
            upcoming.append(data)
        else:
            history.append(data)

    return render_template("dashboards/patient_dashboard.html", 
                           upcoming=upcoming, history=history, 
                           p_name=session.get("name", "User"))


# Doctor Dashboard Route
@app.route("/dashboard/doctor")
def doctor_dashboard():
    if "user_id" not in session or session.get("role") != "doctor":
        return redirect("/login/doctor")
    try:
        doc_id = ObjectId(session["user_id"])
        sort_order = request.args.get('sort', 'asc')
        direction = 1 if sort_order == 'asc' else -1

        appts = list(appointments_coll.find({"doctorId": doc_id}).sort("appointmentDate", direction))
        
        doctor_appointments = []
        for appt in appts:
            patient = patients_coll.find_one({"_id": appt.get("patientId")})
            doctor_appointments.append({
                "id": str(appt["_id"]),
                "code": appt.get("appointmentCode"),
                "patient_name": patient.get("fullName") if patient else "Unknown",
                "date": appt["appointmentDate"].strftime("%Y-%m-%d"),
                "time": appt["appointmentDate"].strftime("%I:%M %p"),
                "status": appt.get("status")
            })
        return render_template("dashboards/doctor_dashboard.html", appointments=doctor_appointments, current_sort=sort_order)
    except Exception as e:
        return f"Error: {e}"
    
# ================= ADMIN =================
@app.route("/admin/dashboard")
def dashboard():    
    patientscount = len(list(patients_coll.find({})))
    doctorscount = len(list(doctors_coll.find({})))
    roomscount = len(list(rooms_coll.find({})))
    operationscount = len(list(operations_coll.find({})))
    appointmentscount =len(list(appointments_coll.find({})))
    return render_template("admin/dashboard.html",
                           patientscount=patientscount,
                           doctorscount=doctorscount,
                           roomscount=roomscount,
                           operationscount=operationscount,
                           appointmentscount=appointmentscount)
@app.route("/admin/users")
def view_users():
    all_users = list(users_coll.find())
    return render_template("/admin/users.html", results=all_users)


@app.route("/admin/delete-user/<user_id>", methods=["POST"])
def delete_user(user_id):
    users_coll.delete_one({"_id": ObjectId(user_id)})
    return redirect(url_for('view_users'))


@app.route("/admin/edit-user/<user_id>", methods=["POST"])
def edit_user(user_id):
    users_coll.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "fullName": request.form.get("fullName"),
            "email": request.form.get("email"),
            "role": request.form.get("role")
        }}
    )
    return redirect(url_for('view_users'))
@app.route("/admin/database")
def database_page():
    return render_template("/admin/database.html",db=db)

@app.route("/admin/add-user", methods=["POST"])
def add_user():
    users_coll.insert_one({
        "name": request.form["name"],
        "email": request.form["email"],
        "role": request.form["role"]
    })
    return redirect("/admin/user")

@app.route("/admin/create-db", methods=["POST"])
def create_new_db():
    db_name = request.form.get("db_name")
    temp_client = MongoClient("mongodb://localhost:27017/")
    new_db = temp_client[db_name]
    new_db["init_collection"].insert_one({"message": "Database Created"})
    return redirect(url_for('database_page'))

@app.route("/admin/create-collection", methods=["POST"])
def create_new_collection():
    col_name = request.form.get("collection_name")
    if col_name:
        db[col_name].insert_one({"init": True})
    return redirect(url_for('database_page'))

@app.route("/admin/reports")
def reports():
    
    u_labels, u_values = get_users_stats()
    user_chart = generate_chart(u_labels, u_values, "Users by Role", 'pie')
   
    a_labels, a_values = get_appointments_stats()
    appt_chart = generate_chart(a_labels, a_values, "Appointments Status", 'bar')
   
    return render_template("reports.html", user_chart=user_chart, appt_chart=appt_chart)

def generate_chart(labels, values, title, chart_type='bar'):
    plt.figure(figsize=(6, 4))
    if chart_type == 'pie':
        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=['#7BA4D0', '#2E5E99', '#0D2440'])
    else:
        plt.bar(labels, values, color='#2E5E99')
 
    plt.title(title)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return f"data:image/png;base64,{chart_url}"

def get_users_stats():
    # مثال: جلب عدد المستخدمين حسب الرول
    roles = ["Admin", "Doctor", "Patient"]
    counts = [users_coll.count_documents({"role": r}) for r in roles]
    return roles, counts

def get_appointments_stats():
    # مثال: جلب عدد المواعيد حسب الحالة
    statuses = ["pending", "scheduled", "completed"]
    counts = [appointments_coll.count_documents({"status": s}) for s in statuses]
    return statuses, counts
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
