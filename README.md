# Book Reviews
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Overview

This web site features 5000 hand picked books allowing users to search, leave reviews for individual books, and see the reviews made by other people. It also uses a third-party API by Goodreads.com, another book review website, to pull ratings from a broader audience. In addition, users are able to query for book details and book reviews programmatically via website's API. Visit live version of the app in this heroku link: https://book-review-website-13032019.herokuapp.com/. 

## Overview Video

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/uu-D-DMLJMU/0.jpg)](https://www.youtube.com/watch?v=uu-D-DMLJMU)

# Installation

## Pre-requisites

Make sure you have the following installed on your machine:
* postgreSQL
* Python 3.7.2

## Proceed to download
1. Clone the repository
2. In your terminal window, navigate into the project
3. Run `pip3 install -r requirements.txt` to make sure all of the necessary Python packages (Flask, SQLAlchemy and others) are installed
4. Set the environment variables:
	  * `export FLASK_APP=application.py`. On Windows, the command is instead` set FLASK_APP=application.py`
    - `KEY` = is your API key, will give you the review and rating data for the book with the provided ISBN number (register at goodreads.com)
    - `DATABASE_URL` = URI for your local postgreSQL database (for example: `postgres://username:password@localhost:5432/databasename` )
5. Run `tables.sql` against your database to create the necessary tables
  ![Alt text](db-schema.png?raw=true "Title")
6. Run `python3 import.py` to import a spreadsheet in CSV format of 5000 different books to your database
7. Finally execute `flask run` command in your terminal to start the server

# Features of the applications

* *Registration*: Users are be able to register.
* *Login*: Users, once registered, should be able to log in to the website with their username and password.
* *Logout*: Logged in users should be able to log out of the site.
* *Search*: Once a user has logged in, they are taken to a page where they can search for a book. Users should be able to type in the ISBN number of a book, the title of a book, or the author of a book. After performing the search, the website displays a list of possible matching results, or some sort of message if there were no matches. If the user typed in only part of a title, ISBN, or author name, search page should find matches for those as well!
* *Book Page*: When users click on a book details from the results of the search page, they are taken to a book page, with details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on the website.
* *Review Submission*: On the book page, users are be able to submit a review: consisting of a rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book. Users won't be able to submit multiple reviews for the same book.
* *Goodreads Review Data*: On the book details page, users are able to see the average rating and number of ratings the work has received from Goodreads.

# API Access

Book Reviews API allows developers access to Book Reviews data in order to help other websites or applications that deal with books be more personalized, social and engaging.

## API methods

`/api/<isbn>` - where `<isbn>` is a 10 digit ISBN number. This GET request returns a JSON response containing the book's title, author, publication date, ISBN number, review count, and average score. Example format:
``` json
{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}
```
