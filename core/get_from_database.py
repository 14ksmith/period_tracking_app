from core.initialize_database import initialize_engine, get_db_connection

# import core.time_variables as tv


def get_tables():
    # List of table names in the database
    engine = initialize_engine()
    table_names = engine.table_names()
    return table_names


def create_new_month_table(
    table_name,
):
    """For the table_name given, create a new table with the following columns."""
    engine = initialize_engine()
    engine.execute(
        f"CREATE TABLE {table_name} (id Integer, date String, period_started String, period_ended String, cramps String, headache String, fatigue String, acne String)"
    )


def add_days_to_month_table(
    num_days_in_month, table_name, month_name, month_number, year
):
    """Get the number of days in the month given and then for each day, add a row with the following column info into the table_name given inthe database."""
    engine = initialize_engine()
    num_days_in_month = num_days_in_month.get(month_name)
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
