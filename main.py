from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from calendar import monthrange, weekday
from requests import get
import sqlite3
import statistics

from sqlalchemy import create_engine, MetaData

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
current_month_and_year = current_date.strftime("%B_%Y")
# current year as an int
current_year = int(current_date.strftime("%Y"))
# current month as an int
current_month = int(current_date.strftime("%m"))
# current month as a name
current_month_name = current_date.strftime("%B")
# Current date in the month as an int
date_of_month = int(current_date.strftime("%d"))
# Current day of week
# weekday = current_date.strftime("%A")
# Number of days in current month
days_in_month = monthrange(year=current_year, month=current_month)[1]
# Weekday that the first of the current month is on
first_of_the_month_weekday = current_date.replace(day=1).strftime("%A")
# Number of days in each month, given the current year
dict_number_of_days_in_each_month = {
    month: monthrange(year=current_year, month=(list_of_months.index(month) + 1))[1]
    for month in list_of_months
}
# Number weekday (Mon=0) that the first of the month falls on for each month in the given year
dict_1st_weekday_in_month = {
    month: weekday(year=current_year, month=(list_of_months.index(month) + 1), day=1)
    for month in list_of_months
}

# ----------------------------------------------------------------------------------------#
app = Flask(__name__)
engine = create_engine("sqlite:///period_tracking_app.db")
metadata = MetaData(bind=engine)


def get_db_connection():
    """Get a connection to the database that can be used with the Flask app"""
    conn = sqlite3.connect("period_tracking_app.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_new_month_table(
    table_name,
):
    """For the table_name given, create a new table with the following columns."""
    engine.execute(
        f"CREATE TABLE {table_name} (id Integer, date String, period_started String, period_ended String, cramps String, headache String, fatigue String, acne String)"
    )


def add_days_to_month_table(table_name, month_name, month_number, year):
    """Get the number of days in the month given and then for each day, add a row with the following column info into the table_name given inthe database."""
    num_days_in_month = dict_number_of_days_in_each_month.get(month_name)
    for day in range(1, num_days_in_month + 1):
        table_name = table_name
        id = day
        date = f"{year}/{month_number}/{day}"
        period_started = "No"
        period_ended = "No"
        cramps = "No"
        headache = "No"
        fatigue = "No"
        acne = "No"
        engine.execute(
            f"INSERT INTO {table_name} (id, date, period_started, period_ended, cramps, headache, fatigue, acne) VALUES ('{id}','{date}', '{period_started}', '{period_ended}','{cramps}', '{headache}', '{fatigue}', '{acne}');"
        )


def get_table_from_database(tablename):
    """Get all entries for each day in the month_table from the database and set equal to 'month_days', return 'month_days"""
    conn = get_db_connection()
    month_days = conn.execute(f"SELECT * FROM {tablename}").fetchall()
    conn.close()
    return month_days


def get_period_start_days():
    all_period_start_days = []
    for table in table_names:
        period_start_days = engine.execute(
            f"SELECT date FROM {table} WHERE period_started = ?",
            ("Yes",),
        ).fetchall()
        for i in range(0, len(period_start_days)):
            all_period_start_days.append(
                datetime.strptime((period_start_days[i][0]), "%Y/%m/%d")
            )
    return all_period_start_days


def get_period_end_days():
    all_period_end_days = []
    for table in table_names:
        period_end_days = engine.execute(
            f"SELECT date FROM {table} WHERE period_ended = ?",
            ("Yes",),
        ).fetchall()
        for i in range(0, len(period_end_days)):
            all_period_end_days.append(
                datetime.strptime((period_end_days[i][0]), "%Y/%m/%d")
            )
    return all_period_end_days


def average_time_between_menstruation():
    time_between_menstruation = []
    conn = get_db_connection()
    for table in table_names:
        # if period_started > 1:
        # take time between period_ended and second period_started
        # else:
        prev_month_post_period_days = conn.execute(
            f"SELECT day FROM {table - 1} WHERE period_ended = ?",
            ("Yes",),
        ).fetchall()
        pre_period = conn.execute(
            f"SELECT day FROM {table} WHERE period_started = ?",
            ("Yes",),
        ).fetchall()
        conn.close()


def average_menstruation_length():
    """Select all the days where period_started equals 'Yes' for each month table in the database, and return an average length of menstruation."""
    menstruation_length = []
    for table in table_names:
        conn = get_db_connection()
        period_days = conn.execute(
            f"SELECT period_started FROM {table} WHERE period_started = ?",
            ("Yes",),
        ).fetchall()
        conn.close()
        num_period_days = len(period_days)
        if num_period_days > 0:
            menstruation_length.append(num_period_days)
    return statistics.mean(menstruation_length)


# -----------------------------------------------------------------------------------------------------------------------------#

# List of table names in the database
table_names = engine.table_names()

# if there is not already a table in the db with current month and year, for each month in the year make a new table
if len(table_names) == 0:
    i = 1
    for month in list_of_months:
        table_name = f"month_{i}_{month}_{current_year}"
        month_number = list_of_months.index(month) + 1
        # create a new table for the month
        create_new_month_table(table_name=table_name)
        # add calendar days to the month table created above
        add_days_to_month_table(
            table_name=table_name,
            month_name=month,
            month_number=month_number,
            year=current_year,
        )
        i += 1

# TODO: Create if statement that checks if, given the current month, there are tables for the next six months as well
#           If there are not, then create whatever tables are missing.

period_start_days = get_period_start_days()
period_end_days = get_period_end_days()


@app.route("/")
def home():
    return render_template(
        "index.html", current_month=current_month_name, current_year=current_year
    )


@app.route("/calendar")
def calendar():
    """View the calendar for the given month and year. Can click on specific days to edit details and navigate to other months."""
    # Get the name of the month from the url arg 'month'
    month_name = request.args.get("month")
    # Get the name of the year from the url arg 'year'
    year = request.args.get("year")
    month_and_year_name = f"{month_name} {year}"
    # Get all day entries in the month given
    month_days = get_table_from_database(
        tablename=f"month_{(list_of_months.index(month_name)) + 1}_{month_name}_{year}"
    )
    try:
        # Get the name of the next month after the month currently viewing
        next_month = list_of_months[list_of_months.index(month_name) + 1]
    except IndexError:
        next_month = list_of_months[0]
    try:
        # Get the name of the previous month of the month currently viewing
        previous_month = list_of_months[list_of_months.index(month_name) - 1]
    except IndexError:
        previous_month = None
    # Send user to the homepage by rendering "index.html" with the following parameters
    return render_template(
        "calendar.html",
        days=month_days,
        weekday=dict_1st_weekday_in_month.get(month_name),
        month_and_year=month_and_year_name,
        year=year,
        current_month=current_month_name,
        month=month_name,
        next_month=next_month,
        last_month=previous_month,
    )


@app.route("/details", methods=["post", "get"])
def day_details():
    """Edit the details of a particular day on the calendar (i.e. period started, heachache, cramps, etc.) and commit the changes to the database."""
    # establish connection to the database
    conn = get_db_connection()
    if request.method == "POST":
        # Need to set 'day_of_month', 'month', and 'year' variables again but using the form,
        #   otherwise it returns 'None' when trying to update the db
        day_of_month = request.form["day"]
        month = request.form["month"]
        year = request.form["year"]
        # Update the period_started in the database
        update_period_started = request.form["period_start"]
        # Update the period_ended in the database
        update_period_ended = request.form["period_ended"]
        # Update cramps in the database
        update_cramps = request.form["cramps"]
        # Update headache in the database
        update_headache = request.form["headache"]
        # Update acne in the database
        update_acne = request.form["acne"]
        # Update fatigue in the database
        update_fatigue = request.form["fatigue"]
        conn.execute(
            f"UPDATE month_{(list_of_months.index(month)) + 1}_{month}_{year} SET  period_started= ?, period_ended= ?, cramps = ?, headache = ?, acne = ?, fatigue = ?"
            " WHERE id = ?",
            (
                update_period_started,
                update_period_ended,
                update_cramps,
                update_headache,
                update_acne,
                update_fatigue,
                day_of_month,
            ),
        )
        # Commit the update to the database
        conn.commit()
        # Close the connection to the database
        conn.close()
        # Bring back the calendar for the same month and year
        return redirect(url_for("calendar", month=month, year=year))
    # Get the day/month/year from the url (after the /edit?)
    day_of_month = request.args.get("date")
    month = request.args.get("month")
    year = request.args.get("year")
    # Create 'table_name' variable using index of 'month' from list of months, 'month', and 'year'
    table_name = f"month_{(list_of_months.index(month)) + 1}_{month}_{year}"
    # Select the day from the table with the given 'day_of_month'
    selected_day = conn.execute(
        f"SELECT * FROM {table_name} WHERE id = ?",
        (day_of_month,),
    ).fetchone()
    return render_template("day_details.html", day=selected_day, month=month, year=year)


if __name__ == "__main__":
    app.run(debug=True)


# TODO: Notification center
# When should period be starting (assume 28 day cycle until learn from individual's pattern)
# allow users to choose how far in advance they want to be notified
# Notification by text/emal?
