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

    history = db.execute("SELECT date, height, weight, bmi FROM profile WHERE user_id = ?", session["user_id"])
    for x in range(len(history)):
        if history[x]["bmi"] < 18.5:
            history[x].update(category = 'underweight')
        elif history[x]["bmi"] >= 18.5 and history[x]["bmi"] < 23:
            history[x].update(category = 'normal')
        elif history[x]["bmi"] >= 23 and history[x]['bmi'] < 25:
            history[x].update(category = 'overweight')
        elif history[x]["bmi"] >= 25 and history[x]['bmi'] < 30:
            history[x].update(category = 'pre-obese')
        elif history[x]["bmi"] >= 30:
            history[x].update(category = 'obese')

    return render_template('index.html', user=rows[0]["username"], details=history)


@app.route('/bmi')
@login_required
def bmi():
    return render_template('bmi.html')


@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():

    # user reached via 'post'
    if request.method == 'POST':

        # using imperial units
        if 'updateIm' in request.form:

            # checking for name
            name = request.form.get('Name')
            if not name:
                flash("You must enter a name!")
                return redirect('/update')

            # checking for height
            feet = request.form.get("feet")
            inch = request.form.get("inch")
            if not feet and not inch:
                flash("Height cannot be left blank!")
                return redirect('/update')

            # checking for weight
            lbs = request.form.get("lbs")
            if not lbs:
                flash("Weight cannot be left blank!")
                return redirect('/update')

            # calculating bmi, height in cms, weight in kgs
            bmi = round(703 * int(lbs) / pow((int(feet) * 12 + int(inch)), 2), 2)
            kgs = round(int(lbs) * 0.453592, 2)
            cms = round((int(feet) * 12 + int(inch)) * 2.54, 2)

            # updating family table
            db.execute("UPDATE family SET height = ?, weight = ?, bmi = ? WHERE user_id = ? and name = ?", cms, kgs, bmi, session["user_id"], name)

        # using metric units
        if 'updateMe' in request.form:

            # checking for name
            name = request.form.get('Name')
            if not name:
                flash("You must choose a name!")
                return redirect('/update')

            # checking for height
            cms = request.form.get("cms")
            if not cms:
                flash("Height cannot be left blank!")
                return redirect('/update')

            # checking for weight
            kgs = request.form.get("kgs")
            if not kgs:
                flash("Weight cannot be left blank!")
                return redirect('/update')

            # calculating bmi, height in cms, weight in kgs
            bmi = round(int(kgs) * 10000 / pow(int(cms), 2), 2)

            # updating family table
            db.execute("UPDATE family SET height = ?, weight = ?, bmi = ? WHERE user_id = ? and name = ?", cms, kgs, bmi, session["user_id"], name)

        flash('Family details updated successfully!')
        return redirect('/family')

    # user reached via 'get'
    else:

        # finding family members
        members = db.execute("SELECT name FROM family WHERE user_id = ?", session['user_id'])

        # query database for username
        user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])

        # removing user's name from members list
        for i in range(len(members)):
            if members[i]['name'] == user[0]['username']:
                del members[i]
                break

        # checking members list
        if not members:
            flash('You have not yet added any family members!')
            return redirect('/add')

        return render_template('update.html', members=members)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():

    # user reached via 'post'
    if request.method =='POST':

        # using imperial units
        if 'addIm' in request.form:

            # checking for name
            name = request.form.get('Name')
            if not name:
                flash("You must enter a name!")
                return redirect('/add')

            # checking for height
            feet = request.form.get("feet")
            inch = request.form.get("inch")
            if not feet and not inch:
                flash("Height cannot be left blank!")
                return redirect('/add')

            # checking for weight
            lbs = request.form.get("lbs")
            if not lbs:
                flash("Weight cannot be left blank!")
                return redirect('/add')

            # calculating bmi, height in cms, weight in kgs
            bmi = round(703 * int(lbs) / pow((int(feet) * 12 + int(inch)), 2), 2)
            kgs = round(int(lbs) * 0.453592, 2)
            cms = round((int(feet) * 12 + int(inch)) * 2.54, 2)

            # adding new entry in family table
            db.execute("INSERT INTO family (user_id, name, weight, height, bmi) VALUES (?, ?, ?, ?, ?)", session["user_id"], name, kgs, cms, bmi)

        # using metric units
        if 'addMe' in request.form:

            # checking for name
            name = request.form.get('Name')
            if not name:
                flash("You must enter a name!")
                return redirect('/add')

            # checking for height
            cms = request.form.get("cms")
            if not cms:
                flash("Height cannot be left blank!")
                return redirect('/add')

            # checking for weight
            kgs = request.form.get("kgs")
            if not kgs:
                flash("Weight cannot be left blank!")
                return redirect('/add')

            # calculating bmi, height in cms, weight in kgs
            bmi = round(int(kgs) * 10000 / pow(int(cms), 2), 2)

            # adding new entry in family table
            db.execute("INSERT INTO family (user_id, name, weight, height, bmi) VALUES (?, ?, ?, ?, ?)", session["user_id"], name, kgs, cms, bmi)

        flash('New family member added successfully!')
        return redirect('/family')

    # user reached via 'get'
    else:
        return render_template('add.html')


@app.route('/remove', methods=['GET', 'POST'])
@login_required
def remove():

    # user reached via 'post'
    if request.method == 'POST':

        # checking for name
        name = request.form.get('del-member')
        if not name:
            flash('No member was selected!')
            return redirect('/remove')

        # deleting the reqested entry from family table
        db.execute('DELETE FROM family WHERE name = ? and user_id = ?', name, session['user_id'])

        flash('Member was removed successfully!')
        return redirect('/family')

    # user reached via 'get'
    else:

        # finding family members
        members = db.execute("SELECT name FROM family WHERE user_id = ?", session['user_id'])# checking members list

        # query database for username
        user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])

        # removing user's name from members list
        for i in range(len(members)):
            if members[i]['name'] == user[0]['username']:
                del members[i]
                break

        # checking members list
        if not members:
            flash('You have not yet added any family members!')
            return redirect('/add')

        return render_template('remove.html', members=members)


@app.route('/family')
@login_required
def family():
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    history = db.execute("SELECT name, height, weight, bmi FROM family WHERE user_id = ?", session["user_id"])
    for x in range(len(history)):
        if history[x]["bmi"] < 18.5:
            history[x].update(category = 'Underweight')
        elif history[x]["bmi"] >= 18.5 and history[x]["bmi"] < 23:
            history[x].update(category = 'Normal')
        elif history[x]["bmi"] >= 23 and history[x]['bmi'] < 25:
            history[x].update(category = 'Overweight')
        elif history[x]["bmi"] >= 25 and history[x]['bmi'] < 30:
            history[x].update(category = 'Pre-obese')
        elif history[x]["bmi"] >= 30:
            history[x].update(category = 'Obese')

    return render_template('family.html', details=history)


@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():

    if request.method == "POST":

        # imperial units were chosen
        if 'updateIm' in request.form:

            # checking for height
            feet = request.form.get("feet")
            inch = request.form.get("inch")
            if not feet and not inch:
                flash("Height cannot be left blank!")
                return redirect('/profile')

            # checking for weight
            lbs = request.form.get("lbs")
            if not lbs:
                flash("Weight cannot be left blank!")
                return redirect('/profile')

            # calculating bmi, height in cms, weight in kgs
            bmi = round(703 * int(lbs) / pow((int(feet) * 12 + int(inch)), 2), 2)
            kgs = round(int(lbs) * 0.453592, 2)
            cms = round((int(feet) * 12 + int(inch)) * 2.54, 2)

            # updating profile table
            db.execute("UPDATE profile SET weight = ?, height = ?, bmi = ? WHERE user_id = ?", kgs, cms, bmi, session["user_id"])

            # updating family table
            user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
            db.execute("UPDATE family SET weight= ?, height = ?, bmi = ? WHERE user_id = ? and name = ?", kgs, cms, bmi, session["user_id"], user[0]["username"])

        # metric units were chosen
        elif 'updateMe' in request.form:

            # checking for height
            cms = request.form.get("cms")
            if not cms:
                flash("Height cannot be left blank!")
                return redirect('/profile')

            # checking for weight
            kgs = request.form.get("kgs")
            if not kgs:
                flash("Weight cannot be left blank!")
                return redirect('/profile')

            # calculating bmi, height in cms, weight in kgs
            bmi = round(int(kgs) * 10000 / pow(int(cms), 2), 2)

            # updating profile table
            db.execute("UPDATE profile SET weight = ?, height = ?, bmi = ? WHERE user_id = ?", kgs, cms, bmi, session["user_id"])

            # updating family table
            user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
            db.execute("UPDATE family SET weight= ?, height = ?, bmi = ? WHERE user_id = ? and name = ?", kgs, cms, bmi, session["user_id"], user[0]["username"])

        else:
            print("ERRRORRR ERRRORRR ERRRORRR")

        flash("Profile details updated successfully!")
        return redirect("/")

    else:
        return render_template('profile.html')


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


        user = db.execute("SELECT id FROM users WHERE username = ?", username)

        # creating new entry for user in family and profile table
        db.execute("INSERT INTO family (user_id, name, height, weight, bmi) VALUES (?, ?, ?, ?, ?)", user[0]["id"], username, 0, 0, 0)
        db.execute("INSERT INTO profile (user_id, date, height, weight, bmi) VALUES (?, ?, ?, ?, ?)", user[0]["id"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 0, 0)

        """ Automatically log in new user """

        # query database for user's details
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # remember new user's session to log in
        session["user_id"] = rows[0]["id"]

        # redirect user to edit profile
        flash("Welcome to ProjectMota2. Please enter your personal details below.")
        return redirect("/profile")

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
