"""
db_interface.py is a script that connects to a database and can store
remove and query data in that database
"""

import psycopg2
from contextlib import contextmanager

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities import log_setup

class DataBase:
    """
    DataBase is a class that connects to a specified remote or local database
    DataBase can be used to store rows and clean the database
    DataBase can also be used to do specail queries on the data as well
    """

    def __init__(self, db_name, user, password, host):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host

        self.logger = log_setup.setup_logger("database_log.log")


    @contextmanager
    def connect(self):
        """connects with database using the contextmanager decorator"""

        try:
            with psycopg2.connect(database=self.db_name,
                                  user=self.user,
                                  password=self.password,
                                  host=self.host) as connection:
                with connection.cursor() as cursor:
                    yield cursor
        except psycopg2.DatabaseError as db_error:
            self.logger.error("Database Connection Error")
            self.logger.error(db_error)

    def query_date_compare(self, table_name, query_str, compare_str):
        """
        This function gets the most recent row with certain collumn values
        table: table name to be queried
        query_str: String of items to query FORMAT:
            "collumn_name1 = value AND collumn_name2 = value2 ...
        compare_str: String of collumn names to retrieve separated by commas FORMAT:
            "collumn_name1, collumn_name2 ..."
        """

        with self.connect() as db_cursor:
            query = "SELECT {compares} FROM {tab} WHERE {querys} ORDER BY datetime DESC LIMIT 1;"
            query = query.format(compares=compare_str, tab=table_name, querys=query_str)
            db_cursor.execute(query)
            return db_cursor.fetchone()

    def store_row(self, table, data_list):
        """
        Stores a row in the database
        data_list is a list with joined collumn names as index 0 and values as index 1
        """

        with self.connect() as db_cursor:
            in_str = "INSERT INTO {table_name} ({joined_collumn_list}) VALUES ({joined_value_list})"
            in_str = in_str.format(table_name=table, #Add values to string
                                   joined_collumn_list=data_list[0],
                                   joined_value_list=data_list[1])
            db_cursor.execute(in_str)

    def clean_data_base(self, days):
        """Deletes rows older than 'days' in all tables"""

        with self.connect() as db_cursor:
            table_q = "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
            db_cursor.execute(table_q) #get table names
            tables = [table[0] for table in db_cursor.fetchall()]

        for table_name in tables:
            clean_statment = "DELETE FROM {tab} WHERE datetime < NOW() - INTERVAL '{day} days';"
            clean_statment = clean_statment.format(tab=table_name, day=days)
            with self.connect() as db_cursor:
                db_cursor.execute(clean_statment)

if __name__ == '__main__':
    pass
