"""
Creates Database for dk_monitor
"""
import psycopg2

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities.db_interface import DataBase

def create_db(user_name, password, host):
    database = DataBase("postgres", user_name, password, host)
    with database.connect() as cursor:
        cursor.execute("CREATE DATABASE dkmonitor OWNER {user}".format(user=user_name))
        create_tables(cursor)

def connect_and_create_tables(db_name, user_name, password, host):
    database = DataBase(db_name, user_name, password, host)
    with database.connect() as cursor:
        create_tables(cursor)

def create_tables(cursor):
    table_defs = load_sql_file("../../sql_table_init.sql")
    cursor.execute(table_defs)

def load_sql_file(sql_file_name):
    try:
        with open(sql_file_name, "r") as sql:
            table_defs = sql.read()
    except FileNotFoundError as err:
        raise err

    return table_defs




