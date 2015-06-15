
import psycopg2
from contextlib import contextmanager
from string import Formatter
from dk_stat import dk_stat

#User = namedtuple('User', 'tota_size use_percent average_access old_file_list')
#User_file = namedtuple('User_file', 'file_path file_size last_access')


class data_base:

    def __init__(self, db_name, user, password):
        self.db_name = db_name
        self.user = user
        self.password = password

        with self.connect() as db_cursor:
            db_cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
            self.tables = [table[0] for table in db_cursor.fetchall()]



    def test_connection(self):
        try:
            psycopg2.connect(database=self.db_name, user=self.user, password=self.password)
        except psycopg2.DatabaseError as db_error:
            print ("Test Connection Error")
        print ("Connection Successful")

    @contextmanager
    def connect(self): #connects with database using the contextmanager decorator
        try:
            with psycopg2.connect(database=self.db_name, user=self.user, password=self.password) as connection:
                with connection.cursor() as cursor:
                    yield cursor
        except psycopg2.DatabaseError as db_error:
            print (db_error)
            print ("Connection Error")

    #TODO Test this again. Not sure if this function is used
    """
    def query_date_compare(self, table, query_list, compare_list):
        #table: table name to be queried
        #query_list: nested list of items to query on. [[column_name, value], [...]]
        #compare_list: list of columns to return from query

        with self.connect() as db_cursor:

            print ("Connected")
            #Joining the nested lists in query_list
            joined_subsets = []
            for column in query_list:
                joined_subsets.append(" = ".join(column))
            joined_query_string = " AND ".join(joined_subsets)

            #Joining the column names in compare list
            compare_string = ", ".join(compare_list)

            db_cursor.execute("SELECT {compares} FROM {tab} WHERE {querys} ORDER BY datetime DESC LIMIT 1;".format(compares=compare_string, tab=table, querys=joined_query_string))
            return db_cursor.fetchone()
    """

    def query_date_compare(self, table, query_str, compare_str):
        #table: table name to be queried
        #query_str: String of items to query FORMAT: "collumn_name1 = value AND collumn_name2 = value2 ...
        #compare_str: string of collumn names to retrieve separated by commas FORMAT "collumn_name1, collumn_name2 ..."

        with self.connect() as db_cursor:
            db_cursor.execute("SELECT {compares} FROM {tab} WHERE {querys} ORDER BY datetime DESC LIMIT 1;".format(compares=compare_str, tab=table, querys=query_str))
            return db_cursor.fetchone()


    def store_row(self, table, data_list): #data_list is a list with joined collumn names as index 0 and values as index 1
        with self.connect() as db_cursor:
        #deleted all of the formatting here and moved it to formate stat_tuple in dk_stat.py
            db_cursor.execute("INSERT INTO {table_name} ({joined_collumn_list}) VALUES ({joined_value_list})".format(table_name=table, joined_collumn_list=data_list[0], joined_value_list=data_list[1]))

if __name__ == '__main__':
    data = data_base('dkmonitor', 'root', '')
    #data.store_row(data.tables[1], ["searched_directory", "asdfasdf"])
    #data_base.store_row(
    compares = ["total_file_size"]
    table = "user_stats"
    querys = [["user_name", "'nametest'"]]
    data.query_date_compare(table, querys, compares)
