## "MEDOC" - Patient's Medical History Management Platform
### Video Demo:  <https://youtu.be/5w0lru3fXgQ>

### Description:

#### General Information:

    MEDOC" is a platform created to conveniently store, edit and share patient's medical
    history.

Created for the convenience of both Patient and Provider, the platform prioritizes patient’s privacy allowing them to choose which parts of the medical history they want to share with each Provider.

##### For Patients:
It alowes Patient to create and store a complete medical history file, including personal medical history, family medical history and medications that the patient currently taking with simple and convenient templates, thus saving time and paper at the doctor's office.

    The personal medical history file can be shared with a registered Provider or used as a template when the Patient needs to fill out a paper form at the doctor's office - conveniently storing information like medication names, dosage and schedules at Patient's fingertips.

##### For Providers:


    A complete list of medications the Patient is taking is extremely valuable for Provider to avoid any prescribed medication interference.

##### The goal:
The main goal of this platform is to create a centralized system for all Patients to securely store, edit and share their medical data with any Provider they choose to share it with and in form they want to share it.


### Files included in this project:

#### app.py and templates:


    Patient's Homepage.
##### route("/")
When this route is requested by a registered and logged in Patient, they will see their homepage ("index.html") with the main platform's functions at their fingertips.

The route retrieves the user id from the current session and displays user's name and a welcome banner.


    Provider adds a diagnosis to the patient's file.
##### route("/add_diagnosis")

When request method is GET:
 this route renders a template "add_diagnosis".html that contains a form where the Provider can select a Patient from their patients list and add a diagnosis by selecting one of the conditions from the provided list or adding a different condition by selecting option "Other" and adding a name of the condition in the "Details" field.

When request method is POST: the route gets the information submitted in the form and inserts it into the "Records" table in the "medoc.db" that stores all the conditions of Patients and their family members. The route then redirects to the "/patients" route.

    Provider adds a prescription to Patient's file.
##### route("/add_prescription")

When request method is GET:
the route retrieves current user's id and gets a list of all the patients that the Provider has from the "Connections" table in the data base. The data is then loaded into a form in the add_prescription.html where Provider can select one of their patients they want to issue a prescription and fill out the form.

When request method is POST:
Once the Provider submits the prescription form, the information submitted will be inserted into the "Meds" table in the data base where each row contains information of patient's id, medication name, dosage, schedule and who prescribed the medication. Provider is then redirected to the "/patients" route.

    Patient adds a Provider to their list.
##### route("/add_provider")

When this route is requested via POST method by submitting a form from "providers.html" page, the route retrieves the user's id, then checks whether this user already has a "connection" with the provider selected in the "Connections" table in the data base.
If the provider was not yet added, a new "connection" is created in the "Connections" table where information about Patient and Provider is stored. The route then redirects user to the "/providers" route.

    Return to medical history page.
##### route("/back_to_history")

This route can be reached via POST from the "info.html", "history.html" and "medications.html". It returns user to the "/summary" route when "Back to History" button is clicked.


    Patient deletes medication from their list.
##### route("/delete_from_meds")

When this route is reached via POST by clicking "delete" button next to a medication in "medications.html", the medication's id is retrieved from the form and then a row with that id is deleted from the "Meds" table in the database.
User is then redirected back to the "/medications" route

    Patient deletes a condition from their medical history.
##### route("/delete_from_record")

When this route is reached via POST by clicking "delete" button next to a condition in "history.html", the condition's id is retrieved from the form and then a row with that id is deleted from the "Records" table in the database.
User is then redirected back to the "/history" route.

    Provider deletes a condition they added to the Patient's file.
##### route("/delete_from_patient_record")

When this route is reached via POST by clicking "delete" button next to a condition in "patient_file.html", the condition's id is retrieved from the form and then a row with that id is deleted from the "Records" table in the database.
User is then redirected back to the "/patients" route.

    Provider deletes a prescription they added from Patient's file.
##### route("/delete_from_patient_meds")
When this route is reached via POST by clicking "delete" button next to a medication in "patient_file.html", the medication's id is retrieved from the form and then a row with that id is deleted from the "Meds" table in the database.
User is then redirected back to the "/patients" route

    Patient deletes a condition from the family history.
##### route("/delete_from_fam")
When this route is reached via POST by clicking "delete" button next to a condition in "family_history.html", the condition's id is retrieved from the form and then a row with that id is deleted from the "Records" table in the database.
User is then redirected back to the "/family_history" route.

    Patient edits family history page.
##### route("/family_history")

The route retrieves user's id from session and with it's help data of user's family from the "Records" table and a list of default conditions from the "Conditions" table.

When the route is reached via GET, a template "family_history.html" is rendered where a user can find a table with all of the family members and their conditions the Patient already added to the file. As well as a form for submitting other family conditions.

When the route is reached via POST, data from the form is submitted and a new row is inserted in to the "Records" table in the database where condition details, user id and family member relation to the user are stored. User is then redirected to the "/family_history" route where the table is updated with newly added information.

    Patient finds provider:
##### route("/find_provider")

The route retrieves a list of default specialties from the "Specialties" table

When the route is reached via GET, route renders a template "find_provider.html" that contains a form where user can input a name of the provider they are looking for and/or choose a specialty.

When the route is reached via POST, the data from the form is retrieved and data is selected from the "Users" table where user type is Provider. The search can be done by name only, by name and specialty and by specialty only. The route then renders a template "find_provider.html" that now displays a table with search results along with buttons allowing user to add a provider of their choice to their providers list.

    Patient edits their medical history.
##### route("/history")

When the route is reached via GET, a template "history.html" is rendered and displays a table with all the medical conditions Patient added to their file with options to delete each condition by clicking "Delete" button (redirects to "/delete_from_record"). Below Patient can add another condition to their history by submitting a form.

When the route is reached via POST, data submitted via form is retrieved and inserted as a new row to the "Records" table where relation is set as "self".

    Patient edits their personal information.
##### oute("/info")

User's id is retrieved from session and then used to load data about this user from the database.

When the route is reached via GET, a template "info.html" is rendered where user will see a form to input their personal information where default values are set to the values the user submitted to their file previously.

When the route is reached via POST, the data from the form is retrieved and values are updated in the row with user's id to reflect the new input information. The user is then redirected to the "/summary" route.

    Login Page.
##### route("/login")

The route first "forgets" any information stored in session.

If the route is reached via GET, a template "login.html" is rendered where user will find a form to input their login and password and click "Submit" to log in.

If the route is reached via POST, data from the form is analyzed and if the username is in the users table and password matches, the user is redirected to their homepage which, depending on the user type will be redirected to "/" for Patients and "/provider_portal" for Providers.
If data inputted was not found in the database, an error message is displayed.

    Log user out.
##### route("/logout"

Route deletes any data stored in session and redirects to ("/"),

    Patient edits their medication list.
##### route("/medications")

When the route is reached via GET, a template "medications.html" is rendered and displays a table with all the medications Patient added to their file with options to delete each medication by clicking "Delete" button (redirects to "/delete_from_meds"). Below Patient can add another medication to their history by submitting a form.

When the route is reached via POST, data submitted from form is retrieved and inserted as a new row to the "Meds" table where user's id is retrived from session. User is then redirected back to the "/medications" route.

    Provider's list of patients.
##### route("/patients")

When the route is reached via POST, a template "patients.html" is rendered. Id displays a list of patients that added the provider to their list, retrieved from the "Connections" table via Provider's id. Provider can open each patient's file by clicking "Open" button next to the Patient's name (user get's redirected to the "/patient_file" route).
User also has an option to add diagnosis and prescription for one of their patients here by clicking on the buttons ( redirects to "/add_diagnosis" or "/add_prescription")

    Patient's file as seen by a provider.
##### route("/patient_file")

When reached via POST by clicking "Open" button on the "patients.html", patient's id is retrieved from the form and loads data from the "Connections" table where connection is between this Provider and requested Patient.
From the "Records" we retrieve data for conditions that were added for the Patient by this Provider. On the rendered template "patient_file" Provider will see a table of all conditions, family history and medications that Patient gave them permission to see as well as conditions that were added by the Provider, which they can also delete from file.

    Patient's list of Providers.
##### route("/providers")

When the route is reached via GET, a template "providers.html" is rendered which displays a list of all providers Patient added by retrieving the data from the "Connections" table.
Patient has an option to delete a provider from their list by clicking "Delete" button and to share medical information with one of the providers in the list by clicking "Share records" button (redirects to "/share")

When the route is reached via POST, a provider's id is retrieved from the form with action "Delete" and a row is deleted from the "Connections" table. User is then redirected back to the "/providers".

    Provider's Homepage.
##### route("/provider_portal"

Template "provider_portal.html" is rendered and user's id is retrieved from the session.Provider's title, first and last name are displayed welcoming him to the Provider's Portal. Here Provider can also find all the key links to access data they need.\


    Provider edits their profile.
##### route("/provider_profile")

User's id is retrieved from session and then used to load data about this user from the database.

When the route is reached via GET, a template "provider_profile.html" is rendered where user will see a form to input their personal information where default values are set to the values the user submitted to their file previously.

When the route is reached via POST, the data from the form is retrieved and values are updated in the row with user's id to reflect the new imput information. The user is then redirected back to the "/provider_profile" route.


    Register page with two account options.
##### oute("/register_patient")

When user clicks on the Register link, they are redirected to the page where they can select what type of profile they want to register for.
Patients are redirected to "/register_patient" and Providers are redirected to route("/register_provider".


    Register as Patient:
##### route("/register_patient")

When reached via GET, a template "patient_register.html" is rendered where user will see a form to input their username, password and confirm password.

When reached via POST, data from the form is retrieved. If all requirements are met, the user's data is saved into "Users" table in the database with user type "Patient", their id is saved in the session and they are redirected to the homepage ("/"). If any errors accrued, an error message will appear.

    Register as Provider.
##### route("/register_provider")
When reached via GET, a template "provider_register.html" is rendered where user will see a form to input their username, password and confirm password.

When reached via POST, data from the form is retrieved. If all requirements are met, the user's data is saved into "Users" table in the database with user type "Provider", their id is saved in the session and they are redirected to the homepage ("/provider_portal"). If any errors accured, an error message will appear.

    Patient shares data with Provider.
##### route("/share")

A template "share.html" is rendered and displays a set of tables. Each table displays either personal information retrieved from the "Users" table, medical history or family history retrieved from the "Records" table, or medications retrieved from the "Meds" table.

Every element of each table has a corresponding checkbox type input selected by default. All selected elements will be submitted to the Provider once "Submit to Provider" button is clicked (redirects to "/shared")

    Patient sees records they shared with Provider.
##### route("/shared")

When this route is reached via POST when user clicks "Submit to Provider" in the "share.html", All the inputs from the same table where the checkbox was checked are converted into a string and added to the main string. Once all submitted data pieces are added to the string, it gets inserted into the "Connections" table in the corresponding column (conditions, family_history or meds).
The "shared.html" template is then rendered.
The data is retrieved from the database and inserted into corresponding tables in the rendered template. User can make sure they submitted all the data they wanted the provider to see.

    Patient's medical history
##### route("/summary")
When  the route is reached, template "summary.html" is rendered. The template displays tables that contain user's personal information, medical history, family history and Medications retrived from the database tables "Users", "Records" and "Meds" via patient's id stored in session.
User can follow links that will take him to the routs that allow editing each part of the information displayed.

#### helpers.py:

    Require user to log in to access platform.
##### def login_required(f):

Check if session stores a user_id before allowing them to access the route.
If not- redirect to the login page.

    Apology
##### def apology(message, code=400):
If function is called, an error message is generated.

























































