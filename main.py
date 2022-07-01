from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# Create the app
app = Flask(__name__)
# create the database if it is not already created
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///period_tracking_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Get the current date
current_date = datetime.now()
# current month and year, given in name of month and full year
current_month = current_date.strftime("%B %Y")
# Current date in the month
date_of_month = current_date.strftime("%d")


# Turn date into int and if it equals 1, then create a new table in the db for that month
if int(date_of_month) == 1:
    # How to create a new table
    class Month(db.Model):
        __tablename__ = current_month
        id = db.Column(db.Integer, primary_key=True)
        date = db.Column(db.Date, unique=True, nullable=False)
        period_started = db.Column(db.Boolean, nullable=False)
        period_ended = db.Column(db.Boolean, nullable=False)

        # def __repr__(self):
        #     """This allows each book object to be identified by its title when printed"""
        #     return f"<Book {self.title}>"

    # this executes the creation of the new table
    db.create_all()


@app.route("/")
def home():
    # Get all the books from the database and set list equal to all_books
    return render_template("index.html")


# TODO: create logic for adding info to tables


# TODO: Notification center
# When should period be starting (assume 28 day cycle until learn from individual's pattern)
# allow users to choose how far in advance they want to be notified
# Notification by text/emal?


# TODO: Create interface
# How user can track their period
# Input info about symptoms (headache, cramps, fatigue, etc.)


if __name__ == "__main__":
    app.run(debug=True)
