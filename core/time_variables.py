from datetime import datetime
from calendar import weekday
from dateutil.relativedelta import *


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

# Get the current datetime object
current_date_time = datetime.now()
# Get only the current date from current_date_time
current_date = current_date_time.date()
# current year as an int
current_year = int(current_date.strftime("%Y"))
# current month as a name
current_month_name = current_date.strftime("%B")
# Current date in the month as an int
date_of_month = int(current_date.strftime("%d"))


def get_1st_day_in_month_weekday(year, month):
    """Get the day of week of the first of the month as a number (Monday=0) given year and month number. Returns weekday number."""
    first_of_month_weekday = weekday(year=year, month=month, day=1)
    return first_of_month_weekday


def get_6_months_ahead_list():
    """Get a list of year and month for 6 months ahead of the current month. Returns nested list (ex: [['2022', '07'], ['2022', '08']])"""
    # List that contains 6 months from the current month (gives ex: (datetime.date(2022, 7, 12)))
    six_months_ahead = []
    for month in range(0, 6):
        # If the list of six_months_ahead is empty, set next_month equal to the a month ahead of the current date and add it to the list
        if len(six_months_ahead) == 0:
            next_month = current_date + relativedelta(months=+1)
            six_months_ahead.append(next_month)
        # If the list is not empty, set next_month equal to a month ahead of the last datetime item in the list and add it to the list
        else:
            next_month = six_months_ahead[-1] + relativedelta(months=+1)
            six_months_ahead.append(next_month)

    # get the year and month of the dates in 'six_months_ahead' list (gives ex: ['2022', '07'] )
    six_months_ahead_string_list = [
        (str(month).split()[0]).split("-")[0:2] for month in six_months_ahead
    ]
    return six_months_ahead_string_list
