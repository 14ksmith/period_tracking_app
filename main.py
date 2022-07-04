from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from calendar import monthrange
from requests import get

from sqlalchemy import table, true

# ------------------------------- Datetime Variables --------------------------------------#
list_of_months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

# Get the current date
current_date = datetime.now()
# current month and year, given in name of month and full year
current_month_and_year = current_date.strftime("%B %Y")
# current year as an int
current_year = int(current_date.strftime("%Y"))
# current month as an int
current_month = int(current_date.strftime("%m"))
# current month as a name
current_month_name = current_date.strftime("%B")
# Current date in the month as an int
date_of_month = int(current_date.strftime("%d"))
# Current day of week
weekday = current_date.strftime("%A")
# Number of days in current month
days_in_month = monthrange(year=current_year, month=current_month)[1]
# Weekday that the first of the current month is on
first_of_the_month_weekday = current_date.replace(day=1).strftime("%A")
# Number of days in each month, given the current year
dict_number_of_days_in_each_month = {
    month: monthrange(year=current_year, month=(list_of_months.index(month) + 1))[1]
    for month in list_of_months
}
# ----------------------------------------------------------------------------------------#

# Create the app
app = Flask(__name__)
# create the database if it is not already created
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///period_tracking_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


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


def get_class_from_tablename(tablename):
    """Get the specific class given the table name, and return that class."""
    for c in db.Model.__subclasses__():
        if c.__tablename__ == tablename:
            return c


def add_days_to_table(month):
    """Add a row for each day of the month along with columns listed below to the data table."""
    num_days_in_month = dict_number_of_days_in_each_month.get(month)
    for day in range(1, num_days_in_month + 1):
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

# if there is not already a table in the db with current month and year, for each month in the year make a new table
if current_month_and_year not in table_names:
    for month in list_of_months:
        # create a new table for the month
        class New_Table(db.Model):

            __tablename__ = f"{month} {current_year}"
            __table_args__ = {"extend_existing": True}
            id = db.Column(db.Integer, primary_key=True)
            date = db.Column(db.Integer, nullable=False)
            day_of_week = db.Column(db.String(250), nullable=False)
            period_started = db.Column(db.String(250), nullable=True)
            cramps = db.Column(db.String(250), nullable=True)
            headache = db.Column(db.String(250), nullable=True)
            fatigue = db.Column(db.String(250), nullable=True)
            acne = db.Column(db.String(250), nullable=True)

        db.create_all()

        add_days_to_table(month=month)


@app.route("/")
def home():
    return render_template(
        "index.html", current_month=current_month_name, current_year=current_year
    )


@app.route("/calendar")
def calendar():

    # Get the name of the month from the url arg 'month'
    month_name = request.args.get("month")
    year = request.args.get("year")
    month_and_year_name = f"{month_name} {year}"
    # Get the table from the database associated with the name of the month above
    month_table = get_class_from_tablename(tablename=f"{month_name} {year}")
    # Get all entries for each day in the month_table from the database and set equal to 'month_days'
    month_days = db.session.query(month_table).all()

    # Send user to the homepage by rendering "index.html" with the following parameters
    return render_template(
        "calendar.html",
        days=month_days,
        weekday=first_of_the_month_weekday,
        month_and_year=month_and_year_name,
        year=year,
        month=month_name,
        next_month=list_of_months[list_of_months.index(month_name) + 1],
        last_month=list_of_months[list_of_months.index(month_name) - 1],
    )


# TODO: When I try to go to the previous or next calendar, the month shows up but not the days. Has something to do with the above logic


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


# TODO: Notification center
# When should period be starting (assume 28 day cycle until learn from individual's pattern)
# allow users to choose how far in advance they want to be notified
# Notification by text/emal?
