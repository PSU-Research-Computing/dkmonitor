
import psycopg2
from contextlib import contextmanager
from string import Formatter
from dk_stat import dk_stat

#User = namedtuple('User', 'tota_size use_percent average_access old_file_list')
#User_file = namedtuple('User_file', 'file_path file_size last_access')


class data_base:

    def __init__(self, db_name, user, password, host):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host

        with self.connect() as db_cursor:
            table_q = "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
            db_cursor.execute(table_q) #get table names
            self.tables = [table[0] for table in db_cursor.fetchall()]



    def test_connection(self):
        try:
            psycopg2.connect(database=self.db_name, user=self.user, password=self.password, host=self.host)
        except psycopg2.DatabaseError as db_error:
            print("Test Connection Error")
        print("Connection Successful")

    @contextmanager
    def connect(self): #connects with database using the contextmanager decorator
        try:
            with psycopg2.connect(database=self.db_name,
                                  user=self.user,
                                  password=self.password,
                                  host=self.host) as connection:
                with connection.cursor() as cursor:
                    yield cursor
        except psycopg2.DatabaseError as db_error:
            print(db_error)
            print("Connection Error")

    #TODO Test this again. Not sure if this function is used

    #This function gets the most recent row with certain collumn values
    def query_date_compare(self, table_name, query_str, compare_str):
        #table: table name to be queried
        #query_str: String of items to query FORMAT: "collumn_name1 = value AND collumn_name2 = value2 ...
        #compare_str: string of collumn names to retrieve separated by commas FORMAT "collumn_name1, collumn_name2 ..."

        with self.connect() as db_cursor:
            query = "SELECT {compares} FROM {tab} WHERE {querys} ORDER BY datetime DESC LIMIT 1;"
            query = query.format(compares=compare_str, tab=table_name, querys=query_str)
            db_cursor.execute(query)
            return db_cursor.fetchone()


    def store_row(self, table, data_list): #data_list is a list with joined collumn names as index 0 and values as index 1
        with self.connect() as db_cursor:
            #deleted all of the formatting here and moved it to formate stat_tuple in dk_stat.py
            #print(data_list[0])
            #print(data_list[1])
            #print()
            in_str = "INSERT INTO {table_name} ({joined_collumn_list}) VALUES ({joined_value_list})"
            in_str = in_str.format(table_name=table, #Add values to string
                                   joined_collumn_list=data_list[0],
                                   joined_value_list=data_list[1])
            db_cursor.execute(in_str)

if __name__ == '__main__':
    data = data_base('dkmonitor', 'root', '')
    #data.store_row(data.tables[1], ["searched_directory", "asdfasdf"])
    #data_base.store_row(
    compares = ["total_file_size"]
    table = "user_stats"
    querys = [["user_name", "'nametest'"]]
    data.query_date_compare(table, querys, compares)
