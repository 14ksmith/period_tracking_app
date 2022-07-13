from datetime import datetime
from calendar import monthrange, weekday
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
# Number of days in current month
days_in_month = monthrange(year=current_year, month=current_month)[1]
# Weekday that the first of the current month is on
first_of_the_month_weekday = current_date.replace(day=1).strftime("%A")
# Number weekday (Mon=0) that the first of the month falls on for each month in the given year
dict_1st_weekday_in_month = {
    month: weekday(year=current_year, month=(list_of_months.index(month) + 1), day=1)
    for month in list_of_months
}
# List that contains a year and a half of months from the current month (gives ex: (datetime.date(2022, 7, 12)))

year_and_half_of_months = []
for month in range(0, 9):
    if len(year_and_half_of_months) == 0:
        next_month = current_date + relativedelta(months=+1)
        year_and_half_of_months.append(next_month)
    else:
        next_month = year_and_half_of_months[-1] + relativedelta(months=+1)
        year_and_half_of_months.append(next_month)

# get the year and month of the dates in 'year_and_half_of_months' list (gives ex: ['2022', '07'] )
months_to_add_to_database = [
    (str(month).split()[0]).split("-")[0:2] for month in year_and_half_of_months
]

# print(months_to_add_to_database)
