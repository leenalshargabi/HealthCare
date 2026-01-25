from flask import Flask, render_template, redirect, url_for, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.mongo import mongo

app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config["MONGO_URI"] = "mongodb://localhost:27017/hospitalDB"

mongo.init_app(app)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- AUTH ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = mongo.db.users.find_one({"email": email})

        if user and check_password_hash(user["password"], password):
            session["user"] = email
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        if mongo.db.users.find_one({"email": email}):
            return render_template("register.html", error="Email already exists")

        mongo.db.users.insert_one({
            "email": email,
            "password": password,
            "role": "patient"
        })

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------- APPOINTMENT ----------------
@app.route("/appointment")
def appointment():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("appointment.html")

# ---------------- PAGES ----------------
@app.route("/specialities")
def specialities():
    return render_template("specialities.html")

@app.route("/speciality/<name>")
def speciality(name):
    return render_template(f"specialities/{name}.html")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
