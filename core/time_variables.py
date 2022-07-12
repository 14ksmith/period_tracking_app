from datetime import datetime
from calendar import monthrange, weekday


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
