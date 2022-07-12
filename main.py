from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from core.time_variables import *
from core.period_prediction import (
    get_period_start_days,
    get_period_end_days,
    average_time_between_periods,
    average_menstruation_length,
    predict_future_period_days,
)
from sqlalchemy import create_engine, MetaData

# ------------------------------- Datetime Variables --------------------------------------#

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
        # Want to include leading zero for any month or day below 10, which is what "str().rjust(2, '0')" is for
        date = f"{year}-{str(month_number).rjust(2, '0')}-{str(day).rjust(2, '0')}"
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


# -----------------------------------------------------------------------------------------------------------------------------#

# List of table names in the database
table_names = engine.table_names()

# if there is not already a table in the db with current month and year, for each month in the year make a new table
if len(table_names) == 0:
    # Month table index
    i = 1
    for month in list_of_months:
        # Have to include a month table index or the tables will be ordered alphabetically, but I need them ordered by month/yea
        #   Also want to include leading zero for any month below 10, which is what "str(i).rjust(2, '0')" is for
        table_name = f"month_{str(i).rjust(2, '0')}_{month}_{current_year}"
        # Get the month number from the list_of_months + 1
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
        # Increase month table index by 1
        i += 1

# TODO: Create if statement that checks if, given the current month, there are tables for the next six months as well
#           If there are not, then create whatever tables are missing.

# set list of periods start days to 'period_start_days'
period_start_days = get_period_start_days()
# set list of periods end days to 'period_end_days'
period_end_days = get_period_end_days()

# if period_start_days and period_end_days are not empty, the below will work
try:
    # set calculated average time between periods to 'avg_time_between_periods'
    avg_time_between_periods = average_time_between_periods(
        period_start_days=period_start_days, period_end_days=period_end_days
    )
    # set calculated average length of period to 'avg_menstruation_length'
    avg_menstruation_length = average_menstruation_length(
        period_start_days=period_start_days, period_end_days=period_end_days
    )
    # set predicted future period days equal to 'predicted_period_days'
    predicted_period_days = predict_future_period_days(
        last_period_end_day=period_end_days[-1],
        avg_time_between_periods=avg_time_between_periods,
        avg_menstruation_length=avg_menstruation_length,
    )
except:
    pass


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
        tablename=f"month_{str((list_of_months.index(month_name)) + 1).rjust(2, '0')}_{month_name}_{year}"
    )
    try:
        # Get the name of the next month after the month currently viewing
        next_month = list_of_months[list_of_months.index(month_name) + 1]
    except IndexError:
        # if returns index error, means it is the last table, so just send back to the first table month (January)
        next_month = list_of_months[0]

    try:
        # Get the name of the previous month of the month currently viewing
        previous_month = list_of_months[list_of_months.index(month_name) - 1]
    except IndexError:
        # if returns an index error, means it is the first table, so set previous_month to None
        previous_month = None

    try:
        # set predicted_period_days to predicted_period_days
        predicted_days_of_period = predicted_period_days
    except NameError:
        # if gives a NameError, means there are no predicted days yet, so set predicted_period_days to None
        predicted_days_of_period = None

    # Send user to the homepage by rendering "index.html" with the following parameters
    return render_template(
        "calendar.html",
        predicted_period_days=predicted_days_of_period,
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
            f"UPDATE month_{str((list_of_months.index(month)) + 1).rjust(2, '0')}_{month}_{year} SET  period_started= ?, period_ended= ?, cramps = ?, headache = ?, acne = ?, fatigue = ?"
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
    table_name = (
        f"month_{str((list_of_months.index(month)) + 1).rjust(2, '0')}_{month}_{year}"
    )
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
