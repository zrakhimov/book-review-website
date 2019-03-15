import os

from flask import Flask, session, render_template, redirect, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    # if Logged in, redirect to /search
    #else index.html
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    # if GET, show the registration form
    if request.method == "GET":
        return render_template("register.html")

    # if POST, validate and commit to database

    if request.method == "POST":
        #if form values are empty show error
        if not request.form.get("first_name"):
            return render_template("error.html", message="Must provide First Name")
        elif not request.form.get("last_name"):
            return render_template("error.html", message="Must provide Last Name")
        elif  not request.form.get("email"):
            return render_template("error.html", message="Must provide E-mail")
        elif not request.form.get("password1") or not request.form.get("password2"):
            return render_template("error.html", message="Must provide password")
        elif request.form.get("password1") != request.form.get("password2"):
            return render_template("error.html", message="Password does not match")
        ## end validation
        else :
            ## assign to variables
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            email = request.form.get("email")
            password = request.form.get("password1")
            # try to commit to database, raise error if any
            try:
                db.execute("INSERT INTO users (firstname, lastname, email, password) VALUES (:firstname, :lastname, :email, :password)",
                               {"firstname": email, "lastname": last_name, "email":email, "password": generate_password_hash(password)})
            except Exception as e:
                return render_template("error.html", message=e)

            db.commit()

            #success - redirect to login
            return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    #if GET
        #if logged in, redirect to /search
        #else Get the login information
    #if POST
        #search database for credentials and allow/deny login
    return render_template("login.html")
