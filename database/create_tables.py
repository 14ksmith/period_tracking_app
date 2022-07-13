from database.database import (
    get_tables,
    create_new_month_table,
    add_days_to_month_table,
)
from calendar import monthrange
import core.time_variables as tv


def create_initial_tables():
    # if there is not already a table in the db with current month and year, for each month in the year make a new table
    list_of_table_names = get_tables()
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
            total_days_in_month = monthrange(
                year=tv.current_year, month=(month_number)
            )[1]
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


def get_list_of_table_year_and_month():
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
        table_month = str((tv.list_of_months.index(split_table_name[2])) + 1).rjust(
            2, "0"
        )
        # set year_and_month equal to the combined table_year, and table_month as a new list
        year_and_month = [table_year, table_month]
        # Add this year_and_month list to the list_of_table_year_and_month
        list_of_table_year_and_month.append(year_and_month)
    return list_of_table_year_and_month


def create_tables_6_months_ahead(table_years_and_months):
    # Get the updated list of tablenames
    updated_list_of_table_names = get_tables()
    # Get the length of list_of_table_names
    table_names_list_length = len(updated_list_of_table_names)
    # the first table_number to be added will be the list length plus 1, after that, table_number increases by 1
    table_number = table_names_list_length + 1

    for month in tv.months_to_add_to_database:
        if month not in table_years_and_months:
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
