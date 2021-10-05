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
        user = None
        for activity in self.preprocessor.activities:
            if not user == activity["user_id"]:
                user = activity["user_id"]
                print("Inserting activities for user:", user)
            query = "INSERT INTO %s (id, user_id, transportation_mode, start_date_time, end_date_time) VALUES (%d, '%s', '%s', '%s', '%s')"
            self.cursor.execute(query % ("activity", activity["id"], activity["user_id"],
                                         activity["transportation_mode"], activity["start_date_time"], activity["end_date_time"]))
            self.db_connection.commit()
        print("Insertion finished without error!")

    def insert_data_trackpoint(self):
        activity = None
        for trackpoint in self.preprocessor.trackpoints:
            if not activity == trackpoint["activity_id"]:
                activity = trackpoint["activity_id"]
                print("Inserting trackpoints for activity:", activity)
            query = "INSERT INTO %s (activity_id, lat, lon, altitude, date_days, date_time) VALUES (%d, %s, %s, %d, %s, '%s')"
            self.cursor.execute(query % ("trackpoint", trackpoint["activity_id"],
                                         trackpoint["lat"], trackpoint["lon"], trackpoint["altitude"], trackpoint["date_days"], trackpoint["date_time"]))
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
        # program.insert_data_user()
        # program.insert_data_activity()
        # program.insert_data_trackpoint()
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == "__main__":
    main()
