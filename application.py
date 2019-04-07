import os, requests

from flask import Flask, session, render_template, redirect, request, flash, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
elif not os.getenv("KEY"):
    raise RuntimeError("API KEY is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
key = os.getenv("KEY")

## Helper
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    # if GET, show the registration form
    if request.method == "GET":
        return render_template("register.html")

    # if POST, validate and commit to database

    else:
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
                               {"firstname": first_name, "lastname": last_name, "email":email, "password": generate_password_hash(password)})
            except Exception as e:
                return render_template("error.html", message=e)

            #success - redirect to login
            db.commit()
            return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        form_email = request.form.get("email")
        form_password = request.form.get("password")

        # Ensure username and password was submitted
        if not form_email:
            return render_template("error.html", message="must provide username")
        elif not form_password:
            return render_template("error.html", message="must provide password")

        # Query database for email and password
        Q = db.execute("SELECT * FROM users WHERE email LIKE :email", {"email": form_email}).fetchone()

        # User exists ?
        if Q is None:
            return render_template("error.html", message="User doesn't exists")
        # Valid password ?
        if not check_password_hash( Q.password, form_password):
            return  render_template("error.html", message = "Invalid password")

        # Remember which user has logged in
        session["user_id"] = Q.userid
        session["email"] = Q.email
        session["firstname"] = Q.firstname
        session["logged_in"] = True
        return redirect(url_for("search"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login index
    return redirect(url_for("index"))


@app.route("/search", methods=["GET","POST"])
@login_required
def search():
    if request.method == "GET":
        return render_template("search.html")
    else:
        query = request.form.get("input-search")
        if query is None:
            return render_template("error.html", message="Search field can not be empty!")
        try:
            result = db.execute("SELECT * FROM books WHERE LOWER(isbn) LIKE :query OR LOWER(title) LIKE :query OR LOWER(author) LIKE :query", {"query": "%" + query.lower() + "%"}).fetchall()
        except Exception as e:
            return render_template("error.html", message=e)
        if not result:
            return render_template("error.html", message="Your query did not match any documents")
        return render_template("list.html", result=result)


@app.route("/details/<int:bookid>", methods=["GET","POST"])
@login_required
def details(bookid):
    if request.method == "GET":
        #Get book details
        result = db.execute("SELECT * from books WHERE bookid = :bookid", {"bookid": bookid}).fetchone()

        #Get API data from GoodReads
        try:
            goodreads = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": result.isbn})
        except Exception as e:
            return render_template("error.html", message = e)

        # Get comments particular to one book
        comment_list = db.execute("SELECT u.firstname, u.lastname, u.email, r.rating, r.comment from reviews r JOIN users u ON u.userid=r.user_id WHERE book_id = :id", {"id": bookid}).fetchall()
        if not result:
            return render_template("error.html", message="Invalid book id")

        return render_template("details.html", result=result, comment_list=comment_list , bookid=bookid, goodreads=goodreads.json()["books"][0])
    else:
        ######## Check if the user commented on this particular book before ###########
        user_reviewed_before = db.execute("SELECT * from reviews WHERE user_id = :user_id AND book_id = :book_id",  {"user_id": session["user_id"], "book_id": bookid}).fetchone()
        if user_reviewed_before:
            return render_template("error.html", message = "You reviewed this book before!")
        ######## Proceed to get user comment ###########
        user_comment = request.form.get("comments")
        user_rating = request.form.get("rating")

        if not user_comment:
            return render_template("error.html", message="Comment section cannot be empty")

        # try to commit to database, raise error if any
        try:
            db.execute("INSERT INTO reviews (user_id, book_id, rating, comment) VALUES (:user_id, :book_id, :rating, :comment)",
                           {"user_id": session["user_id"], "book_id": bookid, "rating":user_rating, "comment": user_comment})
        except Exception as e:
            return render_template("error.html", message=e)

        #success - redirect to details page
        db.commit()
        return redirect(url_for("details", bookid=bookid))


# Create app's API
@app.route("/api/<string:isbn>")
@login_required
def api(isbn):
    """Return details about a single book in json format"""

    # Make sure ISBN exists in the database
    try:
        book = db.execute("SELECT * from books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    except Exception as e:
        return render_template("error.html", message=e)
    if book is None:
        return jsonify({"error": "Not Found"}), 404
    # Get GoodReads API datad
    goodreads = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
    goodreads_book = goodreads.json()["books"][0]
    # Return book details in JSON
    return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": goodreads_book["work_reviews_count"],
            "average_score": goodreads_book["average_rating"]
          })
