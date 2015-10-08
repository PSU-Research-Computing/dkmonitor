"""
Creates Database for dk_monitor
"""

import argparse

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities.db_interface import DataBase

def create_db(user_name, password, host, db_name):
    """Creates database through pyscopg2"""

    database = DataBase(db_name, user_name, password, host)
    with database.connect() as cursor:
        cursor.execute("CREATE DATABASE {db} OWNER {user}".format(db=db_name, user=user_name))
        create_tables(cursor)

def connect_and_create_tables(db_name, user_name, password, host):
    """Connects to create tables in database"""

    database = DataBase(db_name, user_name, password, host)
    with database.connect() as cursor:
        create_tables(cursor)

def create_tables(cursor):
    """Creates tables in database once connected"""

    table_defs = load_sql_file("sql_table_init.sql")
    cursor.execute(table_defs)

def load_sql_file(sql_file_name):
    """Loads sql file in program"""

    try:
        with open(sql_file_name, "r") as sql:
            table_defs = sql.read()
    except FileNotFoundError as err:
        raise err

    return table_defs


def main():
    """Runs command line interface"""

    parser = argparse.ArgumentParser(description="")
    parser.add_argument('host', help="Host name for Database")
    parser.add_argument('-u', '--username', dest='user', default="postgres", help="User name for Database")
    parser.add_argument('-p', '--password', dest='passwd', default="", help="Password for Database account")
    parser.add_argument('-d', '--database', dest='db', default="dkmonitor", help="Name for database that will be created")
    args = parser.parse_args()
    create_db(args.user, args.passwd, args.host, args.db)

if __name__ == "__main__":
    main()



