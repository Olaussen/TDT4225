from re import A
from DbConnector import DbConnector
from tabulate import tabulate
import mysql.connector
from mysql.connector import errorcode
from pickle import load


class DbHandler:
    def __init__(self):
        self.connection = DbConnector()
        self.db_connection = self.connection.db_connection
        self.cursor = self.connection.cursor
        self.users = []
        self.activities = []
        self.trackpoints = []
        self.load_preprocessed_data()

    def load_preprocessed_data(self, users = True, activities = True, trackpoints = True):
        if users:
            print("Loading users")
            with open('users.pickle', 'rb') as file:
                self.users = load(file)

        if activities:
            print("Loading activities")
            with open('activities.pickle', 'rb') as file:
                self.activities = load(file)

        if trackpoints:
            print("Loading trackpoints")
            with open('trackpoints.pickle', 'rb') as file:
                self.trackpoints = load(file)

    def create_all_tables(self):
        TABLES = {}
        TABLES['user'] = (
            "CREATE TABLE `user` ("
            " `id` varchar(10) NOT NULL,"
            " `has_labels` tinyint DEFAULT NULL,"
            " PRIMARY KEY (`id`),"
            " UNIQUE KEY `id_UNIQUE` (`id`)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
        )
        TABLES['activity'] = (
            "CREATE TABLE `activity` ("
            " `id` bigint NOT NULL AUTO_INCREMENT,"
            " `user_id` varchar(10) NOT NULL,"
            " `transportation_mode` varchar(45) DEFAULT NULL,"
            " `start_date_time` datetime DEFAULT NULL,"
            " `end_date_time` datetime DEFAULT NULL,"
            " PRIMARY KEY (`id`),"
            " UNIQUE KEY `id_UNIQUE` (`id`),"
            " KEY `user_id_idx` (`user_id`),"
            " CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE"
            ") ENGINE=InnoDB AUTO_INCREMENT=21080101093115105 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")

        TABLES['trackpoint'] = (
            "CREATE TABLE `trackpoint` ("
            " `id` int NOT NULL AUTO_INCREMENT,"
            " `activity_id` bigint NOT NULL,"
            " `lat` double DEFAULT NULL,"
            " `lon` double DEFAULT NULL,"
            " `altitude` int DEFAULT NULL,"
            " `date_days` double DEFAULT NULL,"
            " `date_time` datetime DEFAULT NULL,"
            " PRIMARY KEY (`id`),"
            " UNIQUE KEY `id_UNIQUE` (`id`),"
            " KEY `activity_id_idx` (`activity_id`),"
            " CONSTRAINT `activity_id` FOREIGN KEY (`activity_id`) REFERENCES `activity` (`id`) ON DELETE CASCADE ON UPDATE CASCADE"
            ") ENGINE=InnoDB AUTO_INCREMENT=9704049 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
            )
        for table_name in TABLES:
            table_description = TABLES[table_name]
            try:
                print("Creating table {}: ".format(table_name), end='')
                self.cursor.execute(table_description)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")
    
    def drop_table(self, table_name):
        print("Dropping table %s..." % table_name)
        query = "DROP TABLE %s"
        self.cursor.execute(query % table_name)

    def insert_data_user(self):
        query = "INSERT INTO user (id, has_labels) VALUES (%s, %s)"
        self.cursor.executemany(query, self.users)
        self.db_connection.commit()

    def insert_data_activity(self):
        query = "INSERT INTO activity (id,user_id,transportation_mode,start_date_time,end_date_time) VALUES (%s,%s,%s,%s,%s)"
        self.cursor.executemany(query, self.activities)
        self.db_connection.commit()

    def insert_data_trackpoint(self):
        query = "INSERT INTO trackpoint (activity_id,lat,lon,altitude,date_days,date_time) VALUES (%s,%s,%s,%s,%s,%s)"
        chunks = [self.trackpoints[i:10000+i] for i in range(0, len(self.trackpoints), 10000)]
        for chunk in chunks:
            self.cursor.executemany(query, chunk)
            self.db_connection.commit()
        print("Insertion finished without error!")

    def fetch_data(self, table_name):
        query = "SELECT * FROM trackpoint WHERE activity_id = %s"
        self.cursor.execute(query % table_name)
        rows = self.cursor.fetchall()
        # Using tabulate to show the table in a nice way
        return rows
        
    def show_tables(self):
        self.cursor.execute("SHOW TABLES")
        rows = self.cursor.fetchall()
        print(tabulate(rows, headers=self.cursor.column_names))


def main():
    program = None
    try:
        
        program = DbHandler()
        #program.create_all_tables()
        #program.drop_table('trackpoint')
        #program.drop_table('activity')
        #program.drop_table('user')
        #program.insert_data_user()
        #program.insert_data_activity()
        #program.insert_data_trackpoint()
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == "__main__":
    main()
