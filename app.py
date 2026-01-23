from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client.healthcare_db

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# Dynamic department pages
@app.route("/department/<name>")
def department(name):
    return render_template(f"{name}.html")

# About page
@app.route("/about")
def about():
    return render_template("about.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = db.users.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["user"] = email
            return redirect(url_for("index"))

    return render_template("login.html")

# Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        db.users.insert_one({
            "name": request.form["name"],
            "email": request.form["email"],
            "password": generate_password_hash(request.form["password"])
        })
        return redirect(url_for("login"))

    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)
