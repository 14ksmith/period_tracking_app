from datetime import datetime, timedelta
import statistics
from main import table_names, engine


def get_period_start_days():
    """Get all dates from given table where period_started equals "Yes", turn into datetime object, and add to all_period_start_days list. Return the list."""
    all_period_start_days = []
    for table in table_names:
        # Get dates from given tablename that have period_started = "Yes"
        period_start_days = engine.execute(
            f"SELECT date FROM {table} WHERE period_started = ?",
            ("Yes",),
        ).fetchall()
        # For each index in 0 to len(period_start_days), append all_period_start_days with first index in period_start_days[index]
        #       and turn it into a datetime object
        for i in range(0, len(period_start_days)):
            all_period_start_days.append(
                datetime.strptime((period_start_days[i][0]), "%Y-%m-%d")
            )
    return all_period_start_days


def get_period_end_days():
    """Get all dates from given table where period_ended equals "Yes", turn into datetime object, and add to all_period_end_days list. Return the list."""
    all_period_end_days = []
    for table in table_names:
        # Get dates from given tablename that have period_ended = "Yes"
        period_end_days = engine.execute(
            f"SELECT date FROM {table} WHERE period_ended = ?",
            ("Yes",),
        ).fetchall()
        # For each index in 0 to len(period_ended_days), append all_period_end_days with first index in period_end_days[index]
        #       and turn it into a datetime object
        for i in range(0, len(period_end_days)):
            all_period_end_days.append(
                datetime.strptime((period_end_days[i][0]), "%Y-%m-%d")
            )
    return all_period_end_days


def average_time_between_periods(period_start_days, period_end_days):
    """Get the average time between periods, return the average."""
    time_between_periods_list = []
    # for each index number in a range of 0, len(period_start_day) - 1:
    for i in range(0, len(period_start_days) - 1):
        # set period_end_day to item at index i in period_end_days list
        period_end_day = period_end_days[i]
        # set next_period_start_day to the iten at index i+1 in period_start_days list
        next_period_start_day = period_start_days[i + 1]
        # Get the time between periods by subtracting the period_end_day from the next_period_start_day
        time_between_period = (next_period_start_day - period_end_day).days
        # add the day difference between periods and add it to the current average_time_between_periods
        time_between_periods_list.append(time_between_period)
    average_time_between_periods = round(statistics.mean(time_between_periods_list))
    return average_time_between_periods


def average_menstruation_length(period_start_days, period_end_days):
    """Get the average length of periods, return the average."""
    length_of_periods_list = []
    # for each index number in a range of 0, len(period_start_day) - 1:
    for i in range(0, len(period_start_days) - 1):
        # set the start_day to the item at index i of period_start_days
        start_day = period_start_days[i]
        # set the end_day to the item at index i of period_end_days
        end_day = period_end_days[i]
        # get the length of period by subrtracting start_day from end_day, then get the number of days difference and turn into an int.
        length_of_period = (end_day - start_day).days
        # add length_of_period to length_of_periods_list
        length_of_periods_list.append(length_of_period)
    # get the average from numbers in the list
    average_length_of_periods = round(statistics.mean(length_of_periods_list))
    return average_length_of_periods


def predict_future_period_days(
    last_period_end_day, avg_time_between_periods, avg_menstruation_length
):
    """Return a list of predicted future period dates given the average number of days period lasts and days between periods."""
    # Make new list of future period start dates
    future_period_dates = []

    # for each index in a range of 6 (this will predict 6 future menstrual cycles)
    for i in range(0, 6):

        if len(future_period_dates) == 0:
            # find the next period start date by taking the last_period_end_day and adding the days between periods
            next_period_start = last_period_end_day + timedelta(
                days=avg_time_between_periods
            )
            # add this new datetime to the list of future period start days
            future_period_dates.append(next_period_start)

            # Add another day to the future_period_dates for each expected day in avg_menstruation_length
            for i in range(1, avg_menstruation_length):
                next_period_date = next_period_start + timedelta(days=i)
                future_period_dates.append(next_period_date)
        else:
            # Get the next period start date by obtaining the last future_period_date then using timedelta to add
            #       the average period length plus 1 (because it avg_time_between_periods is from last end to start,
            #       and this is from last period day to start, so we need to add one more day to the timedelta).
            next_period_start = future_period_dates[-1] + timedelta(
                days=(avg_time_between_periods + 1)
            )
            # add this new datetime to the list of future period start days
            future_period_dates.append(next_period_start)

            # Add another day to the future_period_dates for each expected day in avg_menstruation_length
            for i in range(1, avg_menstruation_length):
                next_period_date = next_period_start + timedelta(days=i)
                future_period_dates.append(next_period_date)
    for i in range(0, len(future_period_dates)):
        string_date = str(future_period_dates[i]).split()[0]
        future_period_dates[i] = string_date
    return future_period_dates
