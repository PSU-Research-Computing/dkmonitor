"""
This module outlines the table objects and raw database interfaces for dkmonitor
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy import Column, String, DateTime, BigInteger, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import datetime
import argparse

import os, sys
sys.path.append(os.path.abspath("../.."))

from dkmonitor.emailer.email_obj import Email
from dkmonitor.config.settings_manager import export_settings


Base = declarative_base()

class StatObj(object):
    """Object used to keep disk usage stats"""
    datetime = Column("datetime", DateTime, primary_key=True)
    hostname = Column("hostname", String)
    target_path = Column("target_path", String)
    total_file_size = Column("total_file_size", BigInteger)
    disk_use_percent = Column("disk_use_percent", Float)
    average_file_age = Column("average_file_age", Float)

    total_file_size_count = 0
    total_old_file_size_count = 0
    number_of_files_count = 0
    number_of_old_files_count = 0
    total_access_time_count = 0

    def add_file(self, file_to_add, last_access_threshold):
        """Adds stats of a file to the stat dictionary"""
        self.total_file_size_count += file_to_add.file_size
        self.number_of_files_count += 1
        self.total_access_time_count += file_to_add.last_access
        if file_to_add.last_access > last_access_threshold:
            self.number_of_old_files_count += 1
            self.total_old_file_size_count += file_to_add.file_size

    def get_total_space(self):
        """Calculates total file size of all files in file_list"""

        self.total_file_size = self.total_file_size_count

    def get_disk_use_percentage(self):
        """Calculates the disk use percentage of all files"""

        stat_tup = os.statvfs(self.target_path)
        total = stat_tup.f_blocks * stat_tup.f_frsize

        user_percentage = 100 * float(self.total_file_size_count)/float(total)
        self.disk_use_percent = user_percentage


    def get_access_average(self):
        """Calculates the last access average for all stored files"""

        try: #possibly change this to an if statement
            average_last_access = self.total_access_time_count / self.number_of_old_files_count
        except ZeroDivisionError:
            average_last_access = self.total_access_time_count

        self.average_file_age = average_last_access

    def calculate_stats(self):
        """Caclutes all stats and returns the object"""

        self.get_total_space()
        self.get_disk_use_percentage()
        self.get_access_average()

        return self

class DirectoryStats(StatObj, Base):
    """extention of StatObj used for storing directory stats"""
    __tablename__ = "directorystats"

class UserStats(StatObj, Base):
    """Extention of StatObj that is used for storing a user's stats"""
    __tablename__ = "userstats"

    username = Column("username", String)

    def email_user(self, postfix, problem_lists, task, current_use):
        """Emails the user associated with the object if they are flagged"""

        email_info = self.build_email_stats(task)
        if current_use > task["usage_warning_threshold"]:
            send_flag = False
            if task["email_usage_warnings"] is True:

                address = email_info["username"] + "@" + postfix
                message = Email(address, email_info)

                if self.username in problem_lists[0]:
                    message.add_message("top_use_warning.txt", email_info)
                if self.username in problem_lists[1]:
                    message.add_message("top_old_warning.txt", email_info)
                send_flag = True

            if task["email_data_alterations"] is True:
                if self.number_of_old_files_count > 0:
                    if current_use > task["usage_critical_threshold"]:
                        message.add_message("file_move_notice.txt", email_info)
                    else:
                        message.add_message("file_move_warning.txt", email_info)

                    send_flag = True

            if send_flag is True:
                message.build_and_send_message()
                print("Sending Message")


    def build_email_stats(self, task):
        """builds a dictionary with all of the stats needed for emailing the user"""
        email_info = {}
        for column in self.__table__.columns:
            email_info[column.name] = getattr(self, column.name)

        stats_vars = {"total_old_file_size": self.total_file_size_count,
                      "number_of_old_files": self.number_of_old_files_count,
                      "usage_warning_threshold": task["usage_warning_threshold"],
                      "usage_critical_threshold": task["usage_critical_threshold"],
                      "old_file_threshold": task["old_file_threshold"],
                      "relocation_path": task["relocation_path"]}

        email_info.update(stats_vars)
        return email_info


class Tasks(Base):
    """Table object for tasks"""
    __tablename__ = "tasks"

    taskname = Column("taskname", String, primary_key=True)
    hostname = Column("hostname", String)
    target_path = Column("target_path", String)
    relocation_path = Column("relocation_path", String)
    delete_old_files = Column("delete_old_files", Boolean)
    delete_when_full = Column("delete_when_full", Boolean)
    usage_warning_threshold = Column("usage_warning_threshold", Integer)
    usage_critical_threshold = Column("usage_critical_threshold", Integer)
    old_file_threshold = Column("old_file_threshold", Integer)
    email_usage_warnings = Column("email_usage_warnings", Boolean)
    email_data_alterations = Column("email_data_alterations", Boolean)
    email_top_percent = Column("email_top_percent", Integer)
    enabled = Column("enabled", Boolean)


class DataBase:
    """The Base class for dealing with the dkmonitor database"""

    def __init__(self,
                 db_type='postgresql',
                 hostname='127.0.0.1',
                 database='postgres',
                 username='postgres',
                 password=''):

        eng_str = '{db_type}://{user}:{passwd}@{host}/{dbname}'.format(db_type=db_type,
                                                                       user=username,
                                                                       passwd=password,
                                                                       host=hostname,
                                                                       dbname=database)

        self.db_engine = create_engine(eng_str)
        Base.metadata.bind = self.db_engine
        Base.metadata.create_all()

    def store(self, data):
        """Stores rows in database"""
        session = self.create_session()
        if isinstance(data, list) is True:
            session.add_all(data)
        else:
            session.add(data)
        session.commit()


    def create_session(self):
        """Short hand for creating database sessions"""
        session = sessionmaker(bind=self.db_engine)
        return session()


class DataBaseCleaner(DataBase):
    """A class used to modify the database from the commandline/clean when running tasks"""
    def __init__(self, db_settings):
        super().__init__(hostname=db_settings["hostname"],
                         database=db_settings["database"],
                         password=db_settings["password"],
                         username=db_settings["username"],
                         db_type=db_settings["db_type"])

    def drop_table(self, tablename):
        """Drops a table specied by string"""
        meta_data = MetaData()
        meta_data.reflect(self.db_engine)
        found_flag = False
        for table in meta_data.tables.values():
            if table.name == tablename:
                table.drop(self.db_engine)
                found_flag = True
                print("Table: '{}' dropped".format(table.name))
        if found_flag is False:
            print("Table: '{}' not found".format(tablename), file=sys.stderr)

    def drop_all(self):
        """Drops all tables in database"""
        meta_data = MetaData()
        meta_data.reflect(self.db_engine)
        for table in meta_data.tables.values():
            table.drop(self.db_engine)
            print("Table: '{}' dropped".format(table.name))

    def list_tables(self):
        """Prints list of all tables"""
        meta_data = MetaData()
        meta_data.reflect(self.db_engine)
        for table in meta_data.tables.values():
            print(table.name)

    def clean_table(self, days, tablename):
        """Deletes all rows older than days in tablename"""
        meta_data = MetaData()
        meta_data.reflect(self.db_engine)
        too_old = datetime.datetime.now() - datetime.timedelta(days=days)
        found_flag = False
        try:
            for table in reversed(meta_data.sorted_tables):
                if table.name == tablename:
                    self.db_engine.execute(table.delete().where(table.columns.datetime <= too_old))
                    print("Table '{}' was successfully cleaned".format(table.name))
                    found_flag = True
        except AttributeError:
            print("Table '{}' does not have a date column".format(tablename), file=sys.stderr)

        if found_flag is False:
            print("Table '{}' was not found".format(tablename), file=sys.stderr)

def clean_database(days):
    """Deletes all rows older than days databases userstats and directorystats"""
    database_settings = export_settings()["DataBase_Settings"]
    database_cleaner = DataBaseCleaner(database_settings)
    database_cleaner.clean_table(days, "userstats")
    database_cleaner.clean_table(days, "directorystats")

def get_args(args):
    """Sets arguements for argparse"""
    description = ("The database command line interface is used to list, clean, and drop tables",
                   " in dkmonitor's database space manually")
    parser = argparse.ArgumentParser(description=description)
    subparser = parser.add_subparsers()

    list_parser = subparser.add_parser("list")
    list_parser.set_defaults(which="list")

    clean_parser = subparser.add_parser("clean")
    clean_parser.set_defaults(which="clean")
    clean_parser.add_argument("days",
                              type=int,
                              help="Delete database entries older than days")
    clean_name_group = clean_parser.add_mutually_exclusive_group()
    clean_name_group.add_argument("--all",
                                  dest="all",
                                  action="store_true",
                                  help="Delete entries older than days in all tables")
    clean_name_group.add_argument("--table",
                                  dest="table_name",
                                  type=str,
                                  help="Table to clean")

    clear_parser = subparser.add_parser("drop")
    clear_parser.set_defaults(which="drop")
    clear_name_group = clear_parser.add_mutually_exclusive_group()
    clear_name_group.add_argument("--all",
                                  dest="all",
                                  action="store_true",
                                  default=False,
                                  help="Clear all tables")
    clear_name_group.add_argument("--table",
                                  dest="table_name",
                                  type=str,
                                  help="Name of table to clear")

    return parser.parse_args(args)

def main(args=None):
    """Command line interface for database cleaner"""
    if args is None:
        args = sys.argv[1:]

    args = get_args(args)
    db_settings = export_settings()["DataBase_Settings"]
    database_cleaner = DataBaseCleaner(db_settings)

    if args.which == "list":
        database_cleaner.list_tables()
    if args.which == "drop":
        if args.all is True:
            database_cleaner.drop_all()
        elif args.table_name != None:
            database_cleaner.drop_table(args.table_name)
    if args.which == "clean":
        if args.all is True:
            database_cleaner.clean_table(args.days, "userstats")
            database_cleaner.clean_table(args.days, "directorystats")
        elif args.table_name != None:
            database_cleaner.clean_table(args.days, args.table_name)

if __name__ == '__main__':
    main()
