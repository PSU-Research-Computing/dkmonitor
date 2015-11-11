from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime, os


Base = declarative_base()

class StatObj(object):
    datetime = Column("datetime", DateTime, primary_key=True)
    hostname = Column("hostname", String)
    target_path = Column("target_path", String)
    total_file_size = Column("total_file_size", BigInteger)
    disk_use_percent = Column("disk_use_percent", Float)
    average_file_age = Column("average_file_age", Float)
    #disk_use_change = Column("disk_use_change", Float)
    #average_file_age_change = Column("average_file_age_change", Float)

    stats = {'total_file_size': 0,
                 'number_of_files': 0,
                 'number_of_old_files' : 0,
                 'total_old_file_size' : 0,
                 'total_access_time': 0}

    def add_file(self, file_to_add, last_access_threshold):
        """Adds stats of a file to the stat dictionary"""
        self.stats["total_file_size"] += file_to_add.file_size
        self.stats["number_of_files"] += 1
        self.stats["total_access_time"] += file_to_add.last_access
        if file_to_add.last_access > last_access_threshold:
            self.stats["number_of_old_files"] += 1
            self.stats["total_old_file_size"] += file_to_add.file_size

    def get_total_space(self):
        """Calculates total file size of all files in file_list"""

        self.total_file_size = self.stats["total_file_size"]

    def get_disk_use_percentage(self):
        """Calculates the disk use percentage of all files"""

        stat_tup = os.statvfs(self.target_path) #TODO try except
        total = stat_tup.f_blocks * stat_tup.f_frsize

        user_percentage = 100 * float(self.stats["total_file_size"])/float(total)
        self.disk_use_percent = user_percentage


    def get_access_average(self):
        """Calculates the last access average for all stored files"""

        try: #possibly change this to an if statement
            average_last_access = self.stats["total_access_time"] / self.stats["number_of_old_files"]
        except ZeroDivisionError:
            average_last_access = self.stats["total_access_time"]

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
    
    #TODO: Add eception for duplicate column value error
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

class DataBaseViewer(DataBase):

    def __init__(self,
                 db_type='postgresql',
                 hostname='127.0.0.1',
                 database='postgres',
                 username='postgres',
                 password=''):
        super().__init__(db_type=db_type,
                         hostname=hostname,
                         database=database,
                         username=username,
                         password=password)

    def get_all_users(self):
        session = self.create_session()
        return [username for username in session.query(UserStats.username).distinct()]

    def get_users_on_system(self, hostname):
        session = self.create_session()
        return [username for username in session.query(UserStats.username).filter(UserStats.hostname==hostname).distinct()]

    def get_users_on_system_disk(self, hostname, diskname):
        session = self.create_session()
        return [username for username in session.query(UserStats.username).filter(UserStats.hostname==hostname).filter(UserStats.target_path==diskname).distinct()]

    def get_user_stats(self, username):
        pass

    def get_all_systems(self):
        session = self.create_session()
        return [hostname for hostname in session.query(DirectoryStats.hostname).distinct()]

    def get_all_disks_on_system(self, hostname):
        session = self.create_session()
        return [disk for disk in session.query(DirectoryStats.target_path).filter(DirectoryStats.hostname==hostname).distinct()]

    def get_all_disks_on_all_systems(self):
        session = self.create_session()
        return [disk for disk in session.query(DirectoryStats.target_path).distinct()]

    def get_agregate_system_stats(self):
        disks = self.get_all_disks_on_all_systems()






if __name__ == '__main__':
    db = DataBaseViewer(hostname='pgsql.rc.pdx.edu', database='diskspace_monitor', username='diskspace_monitor_l', password='9JgN7pwNbB')
    print(db.get_all_users())
    print(db.get_users_on_system("circe.rc.pdx.edu"))
