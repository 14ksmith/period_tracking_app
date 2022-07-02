from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from calendar import month, monthrange

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


# create a new table for the month
class New_Table(db.Model):

    __tablename__ = current_month_and_year
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.String(250), nullable=False)
    period_started = db.Column(db.String(250), nullable=True)
    period_ended = db.Column(db.String(250), nullable=True)
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
            period_started=None,
            period_ended=None,
            cramps=None,
            headache=None,
            fatigue=None,
            acne=None,
        )
        db.session.add(add_day)
        db.session.commit()


# TODO: create logic for adding info to tables


def update_period_start_date(
    whatever_day_user_wants_to_edit, bool_user_wants_to_change_to
):
    """Allow user to change whether their period started on a particular day."""
    day_id = whatever_day_user_wants_to_edit
    day_to_update = New_Table.query.get(day_id)
    day_to_update.period_started = bool_user_wants_to_change_to
    db.session.commit()


# -----------------------------------------------------------------------------------------------------------------------------#

# TODO: Crate logic that only executes the creation of a new table if one for that month does not already exist
# what i have below wont work
table_exists = False

# TODO: Change if date == back to 1
# If date equals 1, then create a new table in the db for that month
if date_of_month == 2 and table_exists == False:
    # this executes the creation of the new table
    db.create_all()
    add_days_to_table()
    table_exists = True

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
        "index.html", days=month_days, weekday=weekday, month=current_month_and_year
    )


@app.route("/edit", methods=["post", "get"])
def edit_day():
    if request.method == "POST":
        # Get the day 'id' from the form
        day_id = request.form["id"]
        # Choose the day to update based off of the id above
        update_day = New_Table.query.get(day_id)
        # Update the period_started in the database
        update_day.period_started = request.form["period_start"]
        # Update the period_ended in the database
        update_day.period_ended = request.form["period_end"]
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
    return render_template("edit.html", day=selected_day)


if __name__ == "__main__":
    app.run(debug=True)
