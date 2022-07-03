from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from calendar import monthrange

from sqlalchemy import true

# Create the app
app = Flask(__name__)
# create the database if it is not already created
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///period_tracking_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Get the current date
current_date = datetime.now()
# current month and year, given in name of month and full year
current_month_and_year = current_date.strftime("%B %Y")
# current year as an int
current_year = int(current_date.strftime("%Y"))
# current month as an int
current_month = int(current_date.strftime("%m"))
# Current date in the month as an int
date_of_month = int(current_date.strftime("%d"))
# Current day of week
weekday = current_date.strftime("%A")
# Number of days in current month
days_in_month = monthrange(year=current_year, month=current_month)[1]
# Weekday that the first of the month is on
first_of_the_month_weekday = current_date.replace(day=1).strftime("%A")


# create a new table for the month
class New_Table(db.Model):

    __tablename__ = current_month_and_year
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.String(250), nullable=False)
    period_started = db.Column(db.String(250), nullable=True)
    cramps = db.Column(db.String(250), nullable=True)
    headache = db.Column(db.String(250), nullable=True)
    fatigue = db.Column(db.String(250), nullable=True)
    acne = db.Column(db.String(250), nullable=True)


def add_days_to_table():
    """Add a row for each day of the month along with columns listed below to the data table."""
    for day in range(1, (days_in_month + 1)):
        # add day of month to the table in the database
        add_day = New_Table(
            date=day,
            day_of_week=weekday,
            period_started="No",
            cramps="No",
            headache="No",
            fatigue="No",
            acne="No",
        )
        db.session.add(add_day)
        db.session.commit()


# -----------------------------------------------------------------------------------------------------------------------------#

# List of table names in the database
table_names = db.engine.table_names()

# If there is not already a table in the database with the name of the current month and year, create a new table
if current_month_and_year not in table_names:
    # this executes the creation of the new table
    db.create_all()
    add_days_to_table()


# TODO: Notification center
# When should period be starting (assume 28 day cycle until learn from individual's pattern)
# allow users to choose how far in advance they want to be notified
# Notification by text/emal?


# TODO: Create interface
# How user can track their period
# Input info about symptoms (headache, cramps, fatigue, etc.)


@app.route("/")
def home():
    # Get all entries for each day from the database and set equal to 'Month'
    month_days = db.session.query(New_Table).all()
    return render_template(
        "index.html",
        days=month_days,
        weekday=first_of_the_month_weekday,
        month=current_month_and_year,
    )


@app.route("/details", methods=["post", "get"])
def day_details():
    if request.method == "POST":
        # Get the day 'id' from the form
        day_id = request.form["id"]
        # Choose the day to update based off of the id above
        update_day = New_Table.query.get(day_id)
        # Update the period_started in the database
        update_day.period_started = request.form["period_start"]
        # Update cramps in the database
        update_day.cramps = request.form["cramps"]
        # Update headache in the database
        update_day.headache = request.form["headache"]
        # Update acne in the database
        update_day.acne = request.form["acne"]
        # Update fatigue in the database
        update_day.fatigue = request.form["fatigue"]
        # Commit the update to the database
        db.session.commit()
        # Bring back the homepage
        return redirect(url_for("home"))
    # Get the id from the url (after the /edit?)
    day_id = request.args.get("id")
    # Get the day from the New_Table table with the chosen id
    selected_day = New_Table.query.get(day_id)

    return render_template("day_details.html", day=selected_day)


if __name__ == "__main__":
    app.run(debug=True)
