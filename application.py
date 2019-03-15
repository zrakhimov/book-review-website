import os

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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

    # if POST, validate and commit to database
    return render_template("register.html")

@app.route("/login")
def login():
    #if GET
        #if logged in, redirect to /search
        #else Get the login information
    #if POST
        #search database for credentials and allow/deny login
    return render_template("login.html")
