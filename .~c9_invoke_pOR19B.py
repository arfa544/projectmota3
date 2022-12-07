import os
from datetime import datetime

from flask import Flask, flash, redirect, request, session, render_template
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///project.db")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            flash("You must provide username!")
            return redirect("/login")

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            flash("You must provide password!")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["pwd"], password):
            flash("Invalid username and/or password!")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    flash('You have logged out successfully!')
    # Redirect user to login form
    return redirect("/")


@app.route('/')
@login_required
def index():
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    return render_template('index.html', user=rows[0]["username"])

@app.route('/bmi')
@login_required
def bmi():
    return render_template('bmi.html')

@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    if request.method == 'POST':
        print('ok')

    else:
        return render_template('update.html')

@app.route('/personal')
@login_required
def personal():
    return render_template('personal.html')

@app.route('/family')
@login_required
def family():
    return render_template('family.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # checking username
        username = request.form.get("username")
        if not username:
            flash("You must provide username!")
            return redirect("/register")
        user_exists = db.execute("SELECT username FROM users WHERE username = ?", username)
        if user_exists != []:
            flash("User already exists! Choose another username.")
            return redirect("/register")

        # checking email
        email = request.form.get("email")
        if not email:
            flash("You must provide email id!")
            return redirect("/register")
        if '@' not in email or '.' not in email:
            flash("You must provide a valid email id!")
            return redirect("/register")

        # checking and confirming password
        password = request.form.get("password")
        if not password:
            flash("Missing password!")
            return redirect("/register")
        if password != request.form.get("confirm-pwd") or not request.form.get("confirm-pwd"):
            flash("Passwords do not match!")
            return redirect("/register")

        # inserting and hashing new user
        db.execute("INSERT INTO users (username, pwd, email) VALUES (?, ?, ?)", username, generate_password_hash(password, method='pbkdf2:sha256', salt_length=8), email)

        # creating new entry for user in family and profile table
        db.execute("INSERT INTO family (user_id, name, height, weight, bmi) VALUES (?, ?, ?, ?, ?)", session["user_id"], username, 0, 0, 0)
        db.execute("INSERT INTO profile (user_id, date, height, weight, bmi) VALUES (?, ?, ?, ?, ?)", session["user_id"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 0, 0)

        """ Automatically log in new user """

        # query database for user's details
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # remember new user's session to log in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect("/personal", message="Welcome to ProjectMota2. Kindly enter your details below")

    # User reached route via GET
    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html", message=e)

for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
