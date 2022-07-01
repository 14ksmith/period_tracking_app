from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# Create the app
app = Flask(__name__)
# create the database if it is not already created
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///period_tracking_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Get the current date of the current month
date_of_month = datetime.now().strftime("%d")

# Turn date into int and if it equals 1, then create a new table in the db for that month
if int(date_of_month) == 1:
    # How to create a new table
    class Month(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        Date = db.Column(db.Date, unique=True, nullable=False)
        Period_Started = db.Column(db.Boolean, nullable=False)
        Period_ended = db.Column(db.Boolean, nullable=False)

        # def __repr__(self):
        #     """This allows each book object to be identified by its title when printed"""
        #     return f"<Book {self.title}>"

    # this executes the creation of the new table
    db.create_all()

# TODO: Notification center
# When should period be starting (assume 28 day cycle until learn from individual's pattern)
# allow users to choose how far in advance they want to be notified
# Notification by text/emal?


# TODO: Create interface
# How user can track their period
# Input info about symptoms (headache, cramps, fatigue, etc.)


if __name__ == "__main__":
    app.run(debug=True)
