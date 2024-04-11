import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///medoc.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# PATIENT HOMEPAGE
@app.route("/")
@login_required
def index():
    id = session["user_id"][0]["id"]

    user = db.execute("SELECT * FROM users WHERE id = ?", id)
    return render_template("index.html", user=user)


# PROVIDER ADDS DIAGNOSIS TO PATIENT'S FILE


@app.route("/add_diagnosis", methods=["POST", "GET"])
@login_required
def add_diagnosis():
    conditions = db.execute("SELECT condition FROM conditions")
    if request.method == "GET":
        provider_id = session["user_id"][0]["id"]
        patients = db.execute("SELECT * FROM connections WHERE provider_id = ? ORDER BY patient_last ASC", provider_id)
        provider = db.execute("SELECT * FROM users WHERE id = ?", provider_id)
        return render_template("/add_diagnosis.html", patients=patients, conditions=conditions, provider=provider)

    else:
        user_id = request.form.get("patient_id")
        condition = request.form.get("condition")
        details = request.form.get("details")
        who_diagnosed = request.form.get("who_diagnosed")
        date_diagnosed = request.form.get("date_diagnosed")
        status = "existing"
        relation = 'self'
        provider_id = session["user_id"][0]["id"]
        db.execute("INSERT INTO records (user_id, condition, details, who_diagnosed, date_diagnosed, status, relation, provider_id) VALUES (?,?,?,?,?,?,?,?)",
                 user_id, condition, details, who_diagnosed, date_diagnosed, status, relation, provider_id)
        return redirect("/patients")


# PROVIDER ADDS PRESCRIPTION TO PATIENT'S FILE
@app.route("/add_prescription", methods=["POST", "GET"])
@login_required
def add_prescription():
    if request.method == "GET":
        provider_id = session["user_id"][0]["id"]
        patients = db.execute("SELECT * FROM connections WHERE provider_id = ? ORDER BY patient_last ASC", provider_id)
        provider = db.execute("SELECT * FROM users WHERE id = ?", provider_id)
        return render_template("/add_prescription.html", patients=patients, provider=provider)

    else:
        user_id = request.form.get("patient_id")
        medication = request.form.get("medication")
        dosage = request.form.get("dosage")
        schedule = request.form.get("schedule")
        prescriber = request.form.get("prescriber")
        provider_id = session["user_id"][0]["id"]
        db.execute("INSERT INTO meds (user_id, medication, dosage, schedule, prescriber, provider_id) VALUES (?,?,?,?,?,?)",
                    user_id, medication, dosage, schedule, prescriber, provider_id )
        return redirect("/patients")


# <action> ADD PROVIDER RO LIST
@app.route("/add_provider", methods=["POST"])
@login_required
def add_provider():
    patient = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"][0]["id"])
    # Check if the provider was already added
    was_added = db.execute("SELECT * FROM connections WHERE patient_id = ? AND  provider_id = ?", session["user_id"][0]["id"],
                            request.form.get("provider_id"))
    if was_added:
        return redirect("/providers")
    else:
        db.execute("INSERT INTO connections (patient_id, patient_title, patient_first, patient_last, provider_id, provider_title, provider_first, provider_last, specialty, dob) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    session["user_id"][0]["id"], patient[0]['title'], patient[0]['first'], patient[0]['last'], request.form.get("provider_id"), request.form.get("provider_title"), request.form.get("provider_first"), request.form.get("provider_last"), request.form.get("specialty"), patient[0]["dob"])
        return redirect("/providers")

# <action> RETURN TO MEDICAL HISTORY PAGE
@app.route("/back_to_history", methods=["POST"])
@login_required
def back_to_history():
    return redirect("/summary")


# <action> DELETE A MEDICATION FROM LIST
@app.route("/delete_from_meds", methods=["POST"])
@login_required
def delete_from_meds():
    iid = session["user_id"][0]["id"]
    med_id = request.form.get("med_id")
    if med_id:
        db.execute("DELETE FROM meds WHERE id = ? AND user_id = ?", med_id, iid)
        return redirect("/medications")

# <action> DELETE A CONDITION FROM USER'S MEDICAL HISTORY
@app.route("/delete_from_record", methods=["POST"])
@login_required
def delete_from_record():
    this_id = session["user_id"][0]["id"]
    condition_id = request.form.get("condition_id")
    if condition_id:
        db.execute("DELETE FROM records WHERE id = ? AND user_id = ?", condition_id, this_id)
        return redirect("/history")

# <action> DELETE A CONDITION FROM USER'S MEDICAL HISTORY
@app.route("/delete_from_patient_record", methods=["POST"])
@login_required
def delete_from_patient_record():
    condition_id = request.form.get("condition_id")
    if condition_id:
        db.execute("DELETE FROM records WHERE id = ?", condition_id)
        return redirect("/patients")


# <action> DELETE A PRESCRIPTION FROM USER'S MEDS
@app.route("/delete_from_patient_meds", methods=["POST"])
@login_required
def delete_from_patient_meds():
    prescription_id = request.form.get("prescription_id")
    if prescription_id:
        db.execute("DELETE FROM meds WHERE id = ?", prescription_id)
        return redirect("/patients")


# <action> DELETE A CONDITION FROM FAMILY MEMBER'S MEDICAL HISTORY
@app.route("/delete_from_fam", methods=["POST"])
@login_required
def delete_from_fam():
    idd = session["user_id"][0]["id"]
    condition_id = request.form.get("condition_id")
    if condition_id:
        db.execute("DELETE FROM records WHERE id = ? AND user_id = ?", condition_id, idd)
        return redirect("/family_history")

# EDIT FAMILY HISTORY PAGE
@app.route("/family_history", methods=["GET", "POST"])
@login_required
def family_history():
    id_u = session["user_id"][0]["id"]
    family = db.execute("SELECT DISTINCT relation FROM records WHERE user_id = ? AND relation != 'self' ", id_u)
    famhistory = db.execute("SELECT * FROM records WHERE user_id = ? AND relation != 'self'", id_u)
    conditions = db.execute("SELECT condition FROM conditions")

    if request.method == "POST":
        db.execute("INSERT INTO records (user_id, condition, details, relation, status) VALUES (?,?,?,?,?)",
                    id_u, request.form.get("condition"), request.form.get("details"), request.form.get("relation"), "N/A")
        return redirect("/family_history")

    else:
        conditions = db.execute("SELECT condition FROM conditions ORDER BY condition ASC")
        return render_template("family_history.html", family=family, famhistory=famhistory, conditions=conditions)

# FIND PROVIDER PAGE
@app.route("/find_provider", methods=["GET", "POST"])
@login_required
def find_providers():
    specialties = db.execute("SELECT specialty FROM specialties ORDER BY specialty ASC")
    if request.method == "POST":
        name = request.form.get("provider_name")
        specialty = request.form.get("specialty")
        if name and not specialty:
            search = db.execute(
                "SELECT * FROM users WHERE usertype = 'Provider' AND last LIKE ? ORDER BY specialty ASC", "%" + name + "%")
        elif specialty and not name:
            search = db.execute(
                "SELECT * FROM users WHERE usertype = 'Provider' AND specialty = ? ORDER BY specialty ASC", specialty)
        else:
            search = db.execute(
                "SELECT * FROM users WHERE usertype = 'Provider' AND last = ? AND specialty = ? ORDER BY specialty ASC", name, specialty)

        return render_template("find_provider.html", specialties=specialties, search=search)

    else:
        return render_template("find_provider.html", specialties=specialties)


# EDIT PATIENT'S MEDICAL HISTORY PAGE
@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    # save user's id in a variable
    user_id = session["user_id"][0]["id"]
    # save all user's records in a dictionary
    records = db.execute("SELECT * FROM records WHERE user_id = ? AND relation = ?", user_id, "self")

    # suggested list of conditions
    conditions = db.execute("SELECT condition FROM conditions WHERE condition != 'Early Death' ORDER BY condition ASC")

    if request.method == "POST":
        conditions = db.execute("SELECT condition FROM conditions")

        condition = request.form.get("condition")
        details = request.form.get("details")
        who_diagnosed = request.form.get("who_diagnosed")
        date_diagnosed = request.form.get("date_diagnosed")
        status = request.form.get("status")
        relation = "self"

        db.execute("INSERT INTO records (user_id, condition, details, who_diagnosed, date_diagnosed, status, relation) VALUES (?,?,?,?,?,?,?)",
                    user_id, condition, details, who_diagnosed, date_diagnosed, status, relation)
        return redirect("/history")

    if request.method == "GET":
        return render_template("history.html", records=records, conditions=conditions)


# EDIT USER'S PERSONAL INFO PAGE
@app.route("/info", methods=["GET", "POST"])
@login_required
def info():
    iiid = session["user_id"][0]["id"]
    current = db.execute("SELECT * FROM users WHERE id = ?", iiid)

    if request.method == "POST":
        title = request.form.get("title")
        first = request.form.get("first")
        last = request.form.get("last")
        sex = request.form.get("sex")
        marital_status = request.form.get("marital_status")
        race = request.form.get("race")
        employment_status = request.form.get("employment")
        ocupation = request.form.get("ocupation")
        employer = request.form.get("employer")
        db.execute("UPDATE users SET title = ?, first = ?, last = ?,sex = ?, marital_status = ?, race = ?, employment_status = ?, ocupation = ?, employer = ?  WHERE id = ?",
                    title, first, last, sex, marital_status, race, employment_status, ocupation, employer, iiid,)


        return redirect("/summary")
    else:
        return render_template("info.html", current=current)


# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check if username and password were provided
        if not request.form.get("password") and not request.form.get("username"):
            return apology("Enter login and password", 400)

        # Query database for username
        user_exists = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure user exists and password is correct
        if len(user_exists) != 1 or not check_password_hash(user_exists[0]["password"], request.form.get("password")):
            return apology("Invalid name and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?", request.form.get("username"))
        session["usertype"] = db.execute("SELECT usertype FROM users WHERE username = ?", request.form.get("username"))
        print(session["usertype"])

        # Redirect to the home page - WHAT TYPE OF USER IS IT?
        usertype = db.execute("SELECT usertype FROM users WHERE id = ?", session["user_id"][0]["id"])

        # Redirect patient to the patient portal
        if usertype[0]["usertype"] == "Patient":
            return redirect("/")

        if usertype[0]["usertype"] == "Provider":
            return redirect("/provider_portal")
    else:
        return render_template("login.html")


# <action> LOG OUT
@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# EDIT USER'S MEDICATIONS LIST
@app.route("/medications", methods=["GET", "POST"])
@login_required
def medications():
    # save user's id in a variable
    an_id = session["user_id"][0]["id"]
    # save all user's records in a dictionary
    meds = db.execute("SELECT * FROM meds WHERE user_id = ?" , an_id)

    if request.method == "POST":
        db.execute("INSERT INTO meds (user_id, medication, dosage, schedule, prescriber) VALUES (?, ?, ?, ?, ?)", an_id, request.form.get(
            "medication"), request.form.get("dosage"), request.form.get("schedule"), request.form.get("prescriber"))

        return redirect("/medications")

    else:
        return render_template("medications.html", meds=meds)

# PROVIDER'S LIST OF PATIENTS.
@app.route("/patients", methods=["GET", "POST"])
@login_required
def patients():
    id = session["user_id"][0]["id"]
    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        patient = db.execute("SELECT * FROM connections WHERE patient_id = ? and provider_id = ?", patient_id, id)
        return redirect("/patients", patient=patient)

    else:
        list = db.execute("SELECT * FROM connections WHERE provider_id = ? ORDER BY patient_last ASC", session["user_id"][0]["id"] )
        return render_template("patients.html", list=list)

# PATIENT'S FILE SEEN BY PROVIDER
@app.route("/patient_file", methods=["POST"])
@login_required
def patient_file():
    # retrive patient id from form:
    patientid = request.form.get("patient_id")
    provider_id = session["user_id"][0]["id"]
    # retrive connection data from the db
    connection = db.execute("SELECT * FROM connections WHERE patient_id = ? and provider_id = ?", patientid, provider_id)
    patient = db.execute("SELECT * FROM users WHERE id = ?", patientid)
    provider = db.execute("SELECT * FROM users WHERE id = ?", provider_id)
    diagnosed = db.execute("SELECT * FROM records WHERE user_id = ? AND provider_id = ?", patientid, provider_id )
    prescribed = db.execute("SELECT * FROM meds WHERE user_id = ? AND provider_id = ?", patientid, provider_id)

    return render_template("patient_file.html", patient=patient,provider=provider, connection=connection, diagnosed=diagnosed, prescribed=prescribed)




# USER'S PROVIDERS LIST PAGE
@app.route("/providers", methods=["GET", "POST"])
@login_required
def providers():
    if request.method == "POST":
        connection_id = request.form.get("id")
        db.execute("DELETE FROM connections WHERE id = ?", connection_id)
        return redirect("/providers")

    else:
        list = db.execute("SELECT * FROM connections WHERE patient_id = ?", session["user_id"][0]["id"] )
        return render_template("providers.html", list=list)

# PROVIDER'S HOME PAGE
@app.route("/provider_portal")
@login_required
def provider_portal():
    id = session["user_id"][0]["id"]

    user = db.execute("SELECT * FROM users WHERE id = ?", id)
    return render_template("index_provider.html", user=user)


# PROVIDER PROFILE
@app.route("/provider_profile", methods=["GET", "POST"])
@login_required
def provider_profile():
    id = session["user_id"][0]["id"]

    if request.method == "GET":
        provider = db.execute("SELECT * FROM users WHERE id = ?", id)
        specialties = db.execute("SELECT specialty FROM specialties ORDER BY specialty ASC")
        return render_template("provider_profile.html", provider=provider, specialties=specialties)
    else:
        title = request.form.get("title")
        first = request.form.get("first")
        last = request.form.get("last")
        sex = request.form.get("sex")
        specialty = request.form.get("specialty")
        if specialty == "Other" and request.form.get("add_specialty"):
            specialty = request.form.get("add_specialty")
            db.execute("INSERT INTO specialties (specialty) VALUES (?)", specialty)
        db.execute("UPDATE users SET title = ?, first = ?, last = ?, sex = ?, specialty = ? WHERE id = ?",
                    title, first, last, sex, specialty, id,)
        return redirect("/provider_profile")



# REGISTER PAGE WITH TWO ACCOUNT OPTIONS
@app.route("/register")
def register():
    return render_template("registeras.html")


# REGISTER AS A PATIENT PAGE
@app.route("/register_patient", methods=["GET", "POST"])
def register_patient():

    # When accessed via POST (Clicked REGISTER button)
    if request.method == "POST":

        # Make sure user completed all felids:
        if not request.form.get("firstname") or not request.form.get("lastname") or not request.form.get("dob") or not request.form.get("password") or not request.form.get("username") or not request.form.get("confirmation"):
            return apology("Please, complete all feilds in the registration form", 400)

        # Check if user entered the same password in confirmation field
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 403)

        # Look if the username is already in the database
        name_taken = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # If username is taken, display error message
        if len(name_taken) > 0:
            return apology("Sorry, this username is taken", 403)
        # If the username is available
        else:
            username = request.form.get("username")
            hash = generate_password_hash(request.form.get("password"))

            # Add credentials to the database
            db.execute("INSERT INTO users (username, password, title, first, last, dob, usertype) VALUES (?,?,?,?,?,?,?)", username, hash, request.form.get(
                "title"), request.form.get("firstname"), request.form.get("lastname"), request.form.get("dob"), request.form.get("usertype") )

            # Remember wich user logged in
            session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?", username)
            session["usertype"] = db.execute("SELECT usertype FROM users WHERE username = ?", username)

            # Redirect user to the home page
            return redirect("/")

    else:
        return render_template("patient_register.html")


# REGISTER AS A PROVIDER PAGE
@app.route("/register_provider", methods=["GET", "POST"])
def register_provider():
    # When accessed via POST (Clicked REGISTER button)
    if request.method == "POST":

        # Make sure user completed all felids:
        if not request.form.get("firstname") or not request.form.get("lastname") or not request.form.get("specialty") or not request.form.get("password") or not request.form.get("username") or not request.form.get("confirmation"):
            return apology("Please, complete all feilds in the registration form", 400)

        # Check if user entered the same password in confirmation field
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 403)

        # Look if the username is already in the database
        name_taken = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # If username is taken, display error message
        if len(name_taken) > 0:
            return apology("Sorry, this username is taken", 403)
        # If the username is available
        else:
            username = request.form.get("username")
            hash = generate_password_hash(request.form.get("password"))

            # Add credentials to the database
            db.execute("INSERT INTO users (username, password, title, first, last, usertype, specialty) VALUES (?,?,?,?,?,?,?)", username, hash, request.form.get(
                "title"), request.form.get("firstname"), request.form.get("lastname"), request.form.get("usertype"), request.form.get("specialty") )

            # Remember wich user logged in
            session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?", username)
            session["usertype"] = db.execute("SELECT usertype FROM users WHERE username = ?", username)

            # Redirect user to the home page
            return redirect("/provider_portal")

    else:
        specialties = db.execute("SELECT specialty FROM specialties")
        return render_template("provider_register.html", specialties=specialties)


# SHARE RECORD WITH PROVIDER PAGE
@app.route("/share", methods=["GET"])
@login_required
def share():
    id = session["user_id"][0]["id"]
    # Save all user's records in a dictionary
    info = db.execute("SELECT * FROM users WHERE id = ?", id)
    # Save all user's conditions
    records = db.execute("SELECT * FROM records WHERE user_id = ? AND relation = ?", id, "self")
    meds = db.execute("SELECT * FROM meds WHERE user_id = ?", id)
    family = db.execute("SELECT DISTINCT relation FROM records WHERE user_id = ? AND relation != 'self' ", id)
    famhistory = db.execute("SELECT * FROM records WHERE user_id = ? AND relation != 'self' ORDER BY relation ASC", id)
    connections = db.execute("SELECT * FROM connections WHERE patient_id = ?", session["user_id"][0]["id"] )

    return render_template("share.html", info=info, records=records, meds=meds, family=family, famhistory=famhistory, connections=connections)

# DISPLAY SHARED RECORDS PAGE
@app.route("/shared", methods=["POST"])
@login_required
def shared():
    if request.method == "POST":

        # retrive data from submitted form
        patient_id = request.form.get("patient_id")
        patient = db.execute("SELECT * FROM users WHERE id = ?", patient_id)
        provider_id = request.form.get("provider")
        provider = db.execute("SELECT * FROM users WHERE id = ?", provider_id)

        sex = ""
        if request.form.get("sex"):
            sex = request.form.get("sex")

        race = ""
        if request.form.get("race"):
            race = request.form.get("race")

        marital_status = ""
        if request.form.get("marital_status"):
            marital_status = request.form.get("marital_status")

        employment_status = ""
        if request.form.get("employment_status"):
            employment_status = request.form.get("employment_status")

        employer = ""
        if request.form.get("employer"):
            employer = request.form.get("employer")

        ocupation = ""
        if request.form.get("ocupation"):
            ocupation = request.form.get("ocupation")

        # Add data to the connections table
        db.execute("UPDATE connections SET sex = ?, race = ?, marital_status = ?, employment_status = ?, employer = ?, ocupation = ? WHERE patient_id = ? AND provider_id = ?",
                    sex, race, marital_status, employment_status, employer, ocupation, patient_id, provider_id)

        # PATIENT'S CONDITIONS:
        # Store a list of patient's condition records in a variable:
        list = db.execute("SELECT id FROM records WHERE user_id = ? AND relation != 'self' ", patient_id)

        # Find how long the list is:
        n = len(list) + 1

        patient_conditions = ""

        # Add the conditions submitted via form to the "patient_conditions" list
        for x in range(1, n):
            # Render  input 'name' by adding an incremented value of x to a string
            x = str(x)
            cond = "condition_" + x

            if request.form.get(cond):
                # Add the string stored in the input 'value' to the patient_conditions list:
                patient_conditions += str(request.form.get(cond))

        # PATIENT'S MEDS:
        # Store a number of patient's meds + 1 in a variable:
        num = len(db.execute("SELECT medication FROM meds WHERE user_id = ?", patient_id)) + 1

        meds = ""
        # Save all meds information submitted via form to the "meds" list
        for y in range(1, num):
            y = str(y)
            med = "med_" + y

            if request.form.get(med):
                # Add the string stored in the input med_y 'value' to meds list:
                meds += str(request.form.get(med))


        # FAMILY HISTORY:
        # Store a number of family conditions + 1 in a variable:
        numb = len(db.execute("SELECT condition FROM records WHERE user_id = ? AND relation !='self'", patient_id))+1
        family = ""
        # Save family conditions submitted via form to the "family" list:
        for f in range(1, numb):
            f = str(f)
            # create a variable holding the input name value:
            case = "case_" + f

            if request.form.get(case):
                # Add case to the family list:
                family += str(request.form.get(case))



        # Add data from the form to the connections db:
        db.execute("UPDATE connections SET conditions = ?, meds = ?, family = ? WHERE patient_id = ? AND provider_id = ?",
                    str(patient_conditions), str(meds), str(family), patient_id, provider_id )


        # Store patient-provider connection data
        connection = db.execute("SELECT * FROM connections WHERE patient_id = ? and provider_id = ?", patient_id, provider_id)

        return render_template("shared.html", patient=patient, provider=provider, connection=connection)

    else:
        return apology("TODO", 404)


# MEDICAL HISTORY PAGE
@app.route("/summary", methods=["GET", "POST"])
@login_required
def summary():
    if request.method == "POST":
        return apology("TODO", 404)

    else:
        # save user's id in a variable
        u_id = session["user_id"][0]["id"]
        # save all user's records in a dictionary
        info = db.execute("SELECT * FROM users WHERE id = ?", u_id)
        records = db.execute("SELECT * FROM records WHERE user_id = ? AND relation = ?", u_id, "self")
        meds = db.execute("SELECT * FROM meds WHERE user_id = ?", u_id)
        family = db.execute("SELECT DISTINCT relation FROM records WHERE user_id = ? AND relation != 'self' ", u_id)
        famhistory = db.execute("SELECT * FROM records WHERE user_id = ? AND relation != 'self'", u_id)
        return render_template("summary.html", records=records, meds=meds, info=info, family=family, famhistory=famhistory)



if __name__ == "__main__":
    app.run(port=4000)