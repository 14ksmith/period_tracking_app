from flask import Flask, render_template, request, redirect, url_for
import core.time_variables as tv
from calendar import monthrange
from database.database import (
    get_tables,
    create_new_month_table,
    add_days_to_month_table,
    get_db_connection,
    get_table_from_database,
)

from core.period_prediction import (
    get_period_start_days,
    get_period_end_days,
    average_time_between_periods,
    average_menstruation_length,
    predict_future_period_days,
)

app = Flask(__name__)

list_of_table_names = get_tables()

# if there is not already a table in the db with current month and year, for each month in the year make a new table
if len(list_of_table_names) == 0:
    # Month table index
    i = 1
    for month in tv.list_of_months:
        # Have to include a month table index or the tables will be ordered alphabetically, but I need them ordered by month/year
        #   Also want to include leading zero for any month below 10, which is what "str(i).rjust(2, '0')" is for
        table_name = f"table_{str(i).rjust(2, '0')}_{month}_{tv.current_year}"
        # Get the month number from the list_of_months + 1
        month_number = tv.list_of_months.index(month) + 1
        # Get the number of days in given month, given the current year
        total_days_in_month = monthrange(year=tv.current_year, month=(month_number))[1]
        # create a new table for the month
        create_new_month_table(table_name=table_name)
        # add calendar days to the month table created above
        add_days_to_month_table(
            num_days_in_month=total_days_in_month,
            table_name=table_name,
            month_number=month_number,
            year=tv.current_year,
        )
        # Increase month table index by 1
        i += 1


updated_list_of_table_names = get_tables()
# List of already created table's year and month as string lists (ex: ['2022', '08'])
list_of_table_year_and_month = []
# For each tablename in list_of_table_names that are already present in the database...
for tablename in updated_list_of_table_names:
    # Split the string at each '_'
    split_table_name = tablename.split("_")
    # Set table_year equal to index 3 in split_table_name, which gives the year
    table_year = split_table_name[3]
    # Set table_month equal the index in list_of_months (plus 1) that contains the month name given by index 2 in split_table_name,
    #        then turned into a string and add a leading '0' if the number is below 10
    table_month = str((tv.list_of_months.index(split_table_name[2])) + 1).rjust(2, "0")
    # set year_and_month equal to the combined table_year, and table_month as a new list
    year_and_month = [table_year, table_month]
    # Add this year_and_month list to the list_of_table_year_and_month
    list_of_table_year_and_month.append(year_and_month)

# Get the length of list_of_table_names
table_names_list_length = len(updated_list_of_table_names)
# the first table_number to be added will be the list length plus 1, after that, table_number increases by 1
table_number = table_names_list_length + 1

for month in tv.months_to_add_to_database:
    if month not in list_of_table_year_and_month:
        print("This table is not currently in the database")
        # Get the name of the given month by turning the timedate object at index 1 into a int, then subtracting 1, and getting the month name from list_of_months at that index
        month_name = tv.list_of_months[int(month[1]) - 1]
        # Get the number month in the calendar year at index 1 of the datetime object 'month'
        month_number = int(month[1])
        # Get the year at index 0 of the datetime object 'month'
        year = month[0]
        # Create the table name for this future month using table_number, month_name and the year
        future_table_name = f"table_{table_number}_{month_name}_{year}"
        # increase the table_number by 1
        table_number += 1
        # Create a new table for this month in the database
        create_new_month_table(table_name=future_table_name)
        # Get the number of days in given month's year and number. Need to specify the return to be index 1, as monthrange gives a tuple
        total_days_in_month = monthrange(year=int(year), month=month_number)[1]
        # add calendar days to the month table created above
        add_days_to_month_table(
            num_days_in_month=total_days_in_month,
            table_name=future_table_name,
            month_number=month_number,
            year=year,
        )

final_list_of_months = get_tables()

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
        "index.html", current_month=tv.current_month_name, current_year=tv.current_year
    )


@app.route("/calendar")
def calendar():
    """View the calendar for the given month and year. Can click on specific days to edit details and navigate to other months."""
    # Get the name of the month from the url arg 'month'
    month_name = request.args.get("month")
    # Get the name of the year from the url arg 'year'
    year = request.args.get("year")
    month_and_year_name = f"{month_name} {year}"
    # Get the table month number of the given month
    table_number = tv.list_of_months.index(month_name)
    # Get all day entries in the month given
    month_days = get_table_from_database(
        tablename=f"table_{str((table_number) + 1).rjust(2, '0')}_{month_name}_{year}"
    )
    # TODO: change next_month and previous_month to next_table and previous_table by getting the table number rather than the month number
    try:
        # Get the name of the next month after the month currently viewing
        next_month = tv.list_of_months[table_number + 1]
    except IndexError:
        # if returns index error, means it is the last table, so just send back to the first table month (January)
        next_month = tv.list_of_months[0]

    try:
        # Get the name of the previous month of the month currently viewing
        previous_month = tv.list_of_months[table_number - 1]
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
        weekday=tv.dict_1st_weekday_in_month.get(month_name),
        month_and_year=month_and_year_name,
        year=year,
        current_month=tv.current_month_name,
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
            f"UPDATE table_{str((tv.list_of_months.index(month)) + 1).rjust(2, '0')}_{month}_{year} SET  period_started= ?, period_ended= ?, cramps = ?, headache = ?, acne = ?, fatigue = ?"
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
    table_name = f"table_{str((tv.list_of_months.index(month)) + 1).rjust(2, '0')}_{month}_{year}"
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
