from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime


Base = declarative_base()

class DirectoryStats(Base):
    __tablename__ = "directorystats"

    datetime = Column("datetime", DateTime, primary_key=True)
    hostname = Column("hostname", String)
    target_path = Column("target_path", String)
    total_file_size = Column("total_file_size", Integer)
    disk_use_percent = Column("disk_use_percent", Float)
    disk_use_change = Column("disk_use_change", Float)
    average_file_age = Column("average_file_age", Float)
    average_file_age_change = Column("average_file_age_change", Float)

class UserStats(Base):
    __tablename__ = "userstats"

    datetime = Column("datetime", DateTime, primary_key=True)
    hostname = Column("hostname", String)
    username = Column("username", String)
    target_path = Column("target_path", String)
    total_file_size = Column("total_file_size", Integer)
    disk_use_percent = Column("disk_use_percent", Float)
    disk_use_change = Column("disk_use_change", Float)
    average_file_age = Column("average_file_age", Float)
    average_file_age_change = Column("average_file_age_change", Float)

class UserStats2(UserStats):
    def a():
        print(1+1)

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
    email_data_altercations = Column("email_data_altercations", Boolean)
    email_top_percent = Column("email_top_percent", Integer)


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
        #print(self.db.table_names())

    def store_row(self, table_row):
        Session = sessionmaker(bind=self.db)
        ses = Session()
        ses.add(table_row)
        ses.commit()



if __name__ == '__main__':
    db = DataBase(hostname='pgsql.rc.pdx.edu', database='diskspace_monitor', username='diskspace_monitor_l', password='')
    #u = UserStats(datetime=datetime.datetime.now(),username="will")
    db.store_row(u)
