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

    def get_query_output(self, query_str):
        with self.connect() as db_cursor:
            db_cursor.execute(query_str)
            return db_cursor.fetchall()

    def query_date_compare(self, table_name, query_str, compare_str):
        """
        This function gets the most recent row with certain collumn values
        table: table name to be queried
        query_str: String of items to query FORMAT:
            "collumn_name1 = value AND collumn_name2 = value2 ...
        compare_str: String of collumn names to retrieve separated by commas FORMAT:
            "collumn_name1, collumn_name2 ..."
        """

        query = "SELECT {compares} FROM {tab} WHERE {querys} ORDER BY datetime DESC LIMIT 1;"
        query = query.format(compares=compare_str, tab=table_name, querys=query_str)
        query_out = self.get_query_output(query)
        if (query_out == []) or (query_out == None):
            return None
        return query_out


class DbEditor(DataBase):
    def __init__(self, db_name, user, password, host):
        super().__init__(db_name, user, password, host)

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

        print("Cleaning Database")

        with self.connect() as db_cursor:
            table_q = "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
            db_cursor.execute(table_q) #get table names
            tables = [table[0] for table in db_cursor.fetchall()]

        for table_name in tables:
            clean_statment = "DELETE FROM {tab} WHERE datetime < NOW() - INTERVAL '{day} days';"
            clean_statment = clean_statment.format(tab=table_name, day=days)
            with self.connect() as db_cursor:
                db_cursor.execute(clean_statment)


class DbViewer(DataBase):
    def __init__(self, db_name, user, password, host):
        super().__init__(db_name, user, password, host)

    def get_all_users(self):
        return [x[0] for x in self.get_unqiue_values('user_name', 'user_stats')]

    def get_user_systems(self, user_name):
        match_str = "user_name = '{}'".format(user_name)
        return [x[0] for x in self.get_unique_values_with_match('system', match_str, 'user_stats')]

    def get_user_disks_on_system(self, user_name, system_host_name):
        match_str = "user_name = '{user}' AND system = '{system}'".format(user=user_name, system=system_host_name)
        return [x[0] for x in self.get_unique_values_with_match('searched_directory', match_str, 'user_stats')]

    def get_all_systems(self):
        return [x[0] for x in self.get_unqiue_values('system', 'directory_stats')]

    def get_system_disks(self, system_host_name):
        match_str = "system = '{}'".format(system_host_name)
        return [x[0] for x in self.get_unique_values_with_match('searched_directory', match_str, 'directory_stats')]

    def get_users_on_system_disk(self, system_host_name, disk_name):
        match_str = "system = '{system}' AND searched_directory = '{sdir}'".format(system=system_host_name, sdir=disk_name)
        return [x[0] for x in self.get_unique_values_with_match('user_name', match_str, 'user_stats')]


    ###Utility query functions
    def get_unqiue_values(self, column_name, table_name):
        query_str = "SELECT DISTINCT {column} FROM {table};".format(column=column_name, table=table_name)
        return self.get_query_output(query_str)

    def get_unique_values_with_match(self, column_name, match_str, table_name):
        query_str = "SELECT DISTINCT {column} FROM {table} WHERE {match};"
        query_str = query_str.format(column=column_name,
                                     table=table_name,
                                     match=match_str)

        return self.get_query_output(query_str)


    def get_disks(self):
        pass

    def get_top_users(self):
        pass

    def get_user_stats(self, user_name):
        """Gets user stats for each disk on each system in database"""

        stats = {'user_name': user_name, 'systems': {}}
        user_systems = self.get_user_systems(user_name)
        for system in user_systems:
            stats['systems'][system] = {}
            user_system_disks = self.get_user_disks_on_system(user_name, system)
            for disk in user_system_disks:
                query_columns = "user_name = '{user}' AND system = '{system}' AND searched_directory = '{disk}'"
                query_columns = query_columns.format(user=user_name, system=system, disk=disk)
                compare_columns = "*"
                d_stats = self.query_date_compare("user_stats", query_columns, compare_columns)
                stats['systems'][system][disk] = d_stats[0]

        return stats


    def get_system_stats(self, system_host_name):
        stats = {'system_host_name': system_host_name, 'disks': {}}
        disks = self.get_system_disks(system_host_name)
        for disk in disks:
            stats['disks'][disk] = {}
            users = self.get_users_on_system_disk(system_host_name, disk)
            stats['disks'][disk]['users'] = users

            query_columns = "searched_directory = '{disk}' AND system = '{system}'"
            query_columns = query_columns.format(system=system_host_name, disk=disk)
            compare_columns = "*"
            d_stats = self.query_date_compare("directory_stats", query_columns, compare_columns)
            stats['disks'][disk]['disk_stats'] = d_stats[0]

        return stats






    def get_disk_change(self, disk_name):
        pass


if __name__ == '__main__':
    dbv = DbViewer('diskspace_monitor', 'diskspace_monitor_l', '9JgN7pwNbB', 'pgsql.rc.pdx.edu')
    #dbv.get_all_users()
    dbv.get_system_disks("Circe")
    print(dbv.get_user_disks_on_system("wpatt2", 'Circe'))
    print(dbv.get_user_stats("wpatt2"))
    print(dbv.get_system_stats("Circe"))
    pass
