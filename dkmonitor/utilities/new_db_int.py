from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import datetime

import os, sys
sys.path.append(os.path.abspath("../.."))

from dkmonitor.emailer.email_obj import Email


Base = declarative_base()

class StatObj(object):
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

        stat_tup = os.statvfs(self.target_path) #TODO try except
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
    __tablename__ = "directorystats"


class UserStats(StatObj, Base):
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
                if self.number_of_old_files > 0:
                    if current_use > task["usage_critical_threshold"]:
                        message.add_message("file_move_notice.txt", email_info)
                    else:
                        message.add_message("file_move_warning.txt", email_info)

                    send_flag = True

            if send_flag is True:
                message.build_and_send_message()
                print("Sending Message")


    def build_email_stats(self, task):
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

        self.db = create_engine(eng_str)
        Base.metadata.bind = self.db
        Base.metadata.create_all()

    #TODO: Add eception for duplicate column value error
    #TODO: Combine store_row and store_rows
    def store_row(self, table_row):
        Session = sessionmaker(bind=self.db)
        ses = Session()
        ses.add(table_row)
        ses.commit()

    def store_rows(self, table_rows):
        Session = sessionmaker(bind=self.db)
        ses = Session()
        ses.add_all(table_rows)
        ses.commit()

    def create_session(self):
        Session = sessionmaker(bind=self.db)
        return Session()


if __name__ == '__main__':
    pass
