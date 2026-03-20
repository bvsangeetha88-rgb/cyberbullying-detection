from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, session, request, render_template, redirect, flash
from functools import wraps
from cs50 import SQL
import re

auth = Blueprint("auth", __name__, static_folder="static", template_folder="templates")
db = SQL("sqlite:///src/main.db")

# -----------------------------
# Registration
# -----------------------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username").strip()
    password = request.form.get("password")
    confirm = request.form.get("confirm")

    # -----------------------------
    # Validations
    # -----------------------------
    if not username:
        return render_template("register.html", msg="You must provide a username")

    if not re.match(r'^[A-Za-z0-9_]+$', username) or not re.search(r'[A-Za-z]', username):
        return render_template("register.html", msg="Please enter a valid username")

    if not password:
        return render_template("register.html", msg="You must provide a password")

    if password != confirm:
        return render_template("register.html", msg="Your passwords do not match")

    if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[^A-Za-z0-9]', password):
        return render_template("register.html", msg="Password must be at least 8 characters long, contain uppercase, lowercase, and a symbol")

    # -----------------------------
    # Check if username already exists
    # -----------------------------
    existing_user = db.execute("SELECT * FROM users WHERE username = :username", username=username)
    if existing_user:
        return render_template("register.html", msg="Username already taken")

    # -----------------------------
    # Hash password
    # -----------------------------
    hashed_password = generate_password_hash(password)

    # -----------------------------
    # Insert user into users table
    # -----------------------------
    try:
        user_id = db.execute(
            "INSERT INTO users (username, hash) VALUES (:username, :hash)",
            username=username, hash=hashed_password
        )
    except Exception as e:
        print("Registration DB error:", e)
        return render_template("register.html", msg="Registration failed. Try another username.")

    # -----------------------------
    # Create user-specific tables (use username as table name to match app expectations)
    # -----------------------------
    # Username already validated above (alphanumeric + underscore and contains a letter)
    user_table = username
    social_table = username + 'Social'

    try:
        db.execute(f"CREATE TABLE IF NOT EXISTS \"{user_table}\" (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, nature TEXT, image TEXT, timestamp DATETIME DEFAULT (datetime('now','localtime')), likes INTEGER DEFAULT 0)")

        db.execute(f"CREATE TABLE IF NOT EXISTS \"{social_table}\" (id INTEGER PRIMARY KEY AUTOINCREMENT, following TEXT)")

    except Exception as e:
        print("User table creation error:", e)
        return render_template("register.html", msg="Registration failed while creating user data.")

    # -----------------------------
    # Success
    # -----------------------------
    session['reg_success'] = "Registration successful. Please log in."
    flash("Registration successful. Please log in.", "success")
    return redirect("/login")


# -----------------------------
# Login
# -----------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    reg_msg = session.pop('reg_success', None)

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        if not username:
            return render_template("login.html", msg="You must provide username")

        if username.isdigit():
            return render_template("login.html", msg="Invalid username")

        if not password:
            return render_template("login.html", msg="You must provide password")

        account_exists = db.execute(
            "SELECT * FROM users WHERE username = :username",
            username=username
        )

        if len(account_exists) != 1 or not check_password_hash(account_exists[0]["hash"], password):
            return render_template("login.html", msg="Invalid username and/or password")

        # Login successful — keep session
        session["user_id"] = account_exists[0]["id"]
        return redirect("/")

    return render_template("login.html", msg=reg_msg if reg_msg else "")


# -----------------------------
# Logout
# -----------------------------
@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# -----------------------------
# Login required decorator
# -----------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function