from DbConnector import DbConnector
from Preprocessor import Preprocessor
from tabulate import tabulate


class DbHandler:
    def __init__(self):
        self.connection = DbConnector()
        self.db_connection = self.connection.db_connection
        self.cursor = self.connection.cursor
        self.preprocessor = Preprocessor()

    def insert_data_user(self):
        for user in self.preprocessor.users:
            # Take note that the name is wrapped in '' --> '%s' because it is a string,
            # while an int would be %s etc
            query = "INSERT INTO %s (id, has_labels) VALUES ('%s', %s)"
            self.cursor.execute(
                query % ("user", user["id"], user["has_labels"]))
        self.db_connection.commit()

    def insert_data_activity(self):
        for activity in self.preprocessor.activities:
            print(activity)
            # Take note that the name is wrapped in '' --> '%s' because it is a string,
            # while an int would be %s etc
            query = "INSERT INTO %s (id, user_id, transportation_mode, start_date_time, end_date_time) VALUES (%d, '%s', '%s', '%s', '%s')"
            self.cursor.execute(query % ("activity", activity["id"], activity["user_id"],
                                         activity["transportation_mode"], activity["start_date_time"], activity["end_date_time"]))
            self.db_connection.commit()

    def fetch_data(self, table_name):
        query = "SELECT * FROM %s"
        self.cursor.execute(query % table_name)
        rows = self.cursor.fetchall()
        print("Data from table %s, raw format:" % table_name)
        print(rows)
        # Using tabulate to show the table in a nice way
        print("Data from table %s, tabulated:" % table_name)
        print(tabulate(rows, headers=self.cursor.column_names))
        return rows

    def show_tables(self):
        self.cursor.execute("SHOW TABLES")
        rows = self.cursor.fetchall()
        print(tabulate(rows, headers=self.cursor.column_names))


def main():
    program = None
    try:
        program = DbHandler()
        # program.insert_data_user() Already run
        program.insert_data_activity()
        _ = program.fetch_data(table_name="activity")
        program.show_tables()
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == "__main__":
    main()
