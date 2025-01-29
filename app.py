import os

from datetime import datetime
from flask import Flask, flash, redirect, request, session, render_template
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from matplotlib import pyplot as plt

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
            return render_template("login.html")

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            flash("You must provide password!")
            return render_template("login.html")
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE user_name = ?", username)
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            flash("Invalid username and/or password!")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Remember which family_id user has logged in
        family_id = db.execute(f"SELECT family_id FROM family_user_mapping where user_id = {session['user_id']}")[0]["family_id"]
        session["family_id"] = family_id

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
    rows = db.execute("SELECT * FROM users WHERE user_id = ?", session["user_id"])

    history = db.execute("SELECT record_date, height, weight, bmi FROM records WHERE user_id = ? ORDER BY record_date DESC", session["user_id"])
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

    # Plotting graph for personal dashboard
    plt.style.use('dark_background')
    fig, ax = plt.subplots(1)
    bmis = list(map(lambda x: x['bmi'], history))
    record_dates = list(map(lambda x: datetime.strptime(x['record_date'],"%Y %m %d %H:%M:%S"), history))
    bmis.reverse()
    record_dates.reverse()
    ax.plot(record_dates, bmis, marker='o', color = 'r')
    ax.set(title="BMI over time", ylabel="BMI")
    plt.xticks(rotation=15, ha='right')
    fig.tight_layout()
    fig_path = "./static/plots/index_plot1.png"
    fig.savefig(fig_path)
    return render_template('index.html', user=rows[0]["user_name"], details=history, fig_path=fig_path)


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
            username = request.form.get('Name')
            if not username:
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

        # using metric units
        if 'updateMe' in request.form:

            # checking for name
            username = request.form.get('Name')
            if not username:
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

        # Insert into records
        user_id = db.execute("SELECT user_id FROM users WHERE user_name = ?", username)[0]['user_id']
        db.execute("INSERT INTO records(user_id, height, weight, bmi, record_date) VALUES(?,?,?,?,?)", user_id, cms, kgs, bmi, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        flash('Family details updated successfully!')
        return redirect('/family')

    # user reached via 'get'
    else:

        # finding family members
        members = db.execute("SELECT user_name FROM users LEFT JOIN family_user_mapping USING (user_id) WHERE family_id = ?", session['family_id'])

        # query database for username
        user = db.execute("SELECT user_name FROM users WHERE user_id = ?", session["user_id"])

        # removing user's name from members list
        for i in range(len(members)):
            if members[i]['user_name'] == user[0]['user_name']:
                del members[i]
                break

        # checking members dict.
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
        if 'add' in request.form:

            # checking for name
            username = request.form.get('Name')
            if not username:
                flash("You must enter a name!")
                return redirect('/add')

            # checking email
            email = request.form.get("email")
            if not email:
                flash("You must provide email id!")
                return redirect("/add")
            if '@' not in email or '.' not in email:
                flash("You must provide a valid email id!")
                return redirect("/add")

            # checking and confirming password
            password = request.form.get("password")
            if not password:
                flash("Missing password!")
                return redirect("/add")
            if password != request.form.get("confirm-pwd") or not request.form.get("confirm-pwd"):
                flash("Passwords do not match!")
                return redirect("/add")

            # inserting and hashing new user
            user_id = db.execute("INSERT INTO users (user_name, password, email) VALUES (?, ?, ?)", username, generate_password_hash(password, method='pbkdf2:sha256', salt_length=8), email)
            db.execute(f"INSERT INTO family_user_mapping (family_id, user_id) VALUES ({session['family_id']}, {user_id})")

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
        user_id = db.execute("SELECT user_id FROM users WHERE user_name = ?", name)[0]['user_id']
        db.execute('DELETE FROM records WHERE user_id = ?', user_id)

        flash('Member was removed successfully!')
        return redirect('/family')

    # user reached via 'get'
    else:

        # finding family members
        members = db.execute("SELECT user_name FROM users LEFT JOIN family_user_mapping USING (user_id) WHERE family_id = ?", session['family_id'])# checking members list
        
        # query database for username
        user = db.execute("SELECT user_name FROM users WHERE user_id = ?", session["user_id"])

        # removing user's name from members list
        for i in range(len(members)):
            if members[i]['user_name'] == user[0]['user_name']:
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
    user_ids = db.execute("SELECT user_id FROM family_user_mapping WHERE family_id = ?", session["family_id"])

    plt.style.use('dark_background')
    fig, ax = plt.subplots(1)

    details = list()
    for user_id in user_ids:
        user_id = user_id["user_id"]
        user_name = db.execute("SELECT user_name FROM users WHERE user_id = ?", user_id)[0]["user_name"]
        records = db.execute("SELECT height, weight, bmi, record_date FROM records WHERE user_id = ? ORDER BY record_date DESC", user_id)
        if not records:
            continue
        record = records[0]
        record["user_name"] = user_name
        if record["bmi"] < 18.5:
            record.update(category = 'Underweight')
        elif record["bmi"] >= 18.5 and record["bmi"] < 23:
            record.update(category = 'Normal')
        elif record["bmi"] >= 23 and record['bmi'] < 25:
            record.update(category = 'Overweight')
        elif record["bmi"] >= 25 and record['bmi'] < 30:
            record.update(category = 'Pre-obese')
        elif record["bmi"] >= 30:
            record.update(category = 'Obese')

        details.append(record)
        bmis = list(map(lambda x: x['bmi'], records))
        record_dates = list(map(lambda x: datetime.strptime(x['record_date'],"%Y %m %d %H:%M:%S"), records))
        bmis.reverse()
        record_dates.reverse()
        # Plotting graph of each family member
        ax.plot(record_dates, bmis, marker='o', label = user_name)
        plt.legend()

    ax.set(title="BMI over time", ylabel="BMI")
    plt.xticks(rotation=15, ha='right')
    fig.tight_layout()
    fig_path = "./static/plots/family_plot1.png"
    fig.savefig(fig_path)
    return render_template('family.html', details=details, fig_path=fig_path)


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

        else:
            raise Exception(f"Unknown Option provided.")

        # Insert into records
        db.execute("INSERT INTO records(user_id, height, weight, bmi, record_date) VALUES(?,?,?,?,?)", session["user_id"], cms, kgs, bmi, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

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
        user_exists = db.execute("SELECT user_name FROM users WHERE user_name = ?", username)
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
        user_id = db.execute("INSERT INTO users (user_name, password, email) VALUES (?, ?, ?)", username, generate_password_hash(password, method='pbkdf2:sha256', salt_length=8), email)

        # get selected Family Name
        selected_family_name = request.form.get("select_family_name")

        if selected_family_name is None:
            new_family_name = request.form.get("new_family_name")
            if new_family_name is None:
                flash("Please select a existing Family name, or provide a new family name.")
                return redirect("/register")

            family_name_exists = db.execute("SELECT family_name FROM family WHERE family_name = ?", new_family_name)
            if family_name_exists != []:
                flash("Family Name already exists! Please select from drop down.", category="warning")
                return redirect("/register")

            family_id = db.execute("INSERT INTO family(family_name) VALUES (?)", new_family_name)

        else:
            family_id = db.execute("SELECT family_id from family WHERE family_name = ?", selected_family_name)[0]['family_id']


        # Inserting user_id and respective family_id in family_user_mapping
        db.execute(f"INSERT INTO family_user_mapping (family_id, user_id) VALUES ({family_id}, {user_id})")

        """ Automatically log in new user """
        # remember new user's session to log in
        session["user_id"] = user_id
        session["family_id"] = family_id

        # redirect user to edit profile
        flash("Welcome to ProjectMota2. Please enter your personal details below.")
        return redirect("/profile")

    # User reached route via GET
    else:
        # Get all family members dict.
        members = db.execute("SELECT family_name FROM family")
        return render_template("register.html", members=members)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html", message=e)

for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
