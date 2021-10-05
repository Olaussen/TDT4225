from DbConnector import DbConnector
from tabulate import tabulate
import haversine as hs


class Queries:
    def __init__(self):
        self.connection = DbConnector()
        self.db_connection = self.connection.db_connection
        self.cursor = self.connection.cursor

    # TASK 1
    def total_amount_of_entries(self):
        print("\n TASK 1 \n")
        query = "SELECT (SELECT COUNT(id) FROM user) AS user_sum, (SELECT COUNT(id) FROM activity) AS activity_sum, (SELECT COUNT(id) FROM trackpoint) AS trackpoint_sum"
        self.cursor.execute(query)
        result = self.cursor.fetchall()[0]
        print("Amount of users:", result[0])
        print("Amount of activities:", result[1])
        print("Amount of trackpoints:", result[2])
        print("Total amount of entries in database:", sum(result))
        return result

    # TASK 2
    def min_max_avg_activities(self):
        print("\n TASK 2 \n")
        min_max_query = "SELECT user_id,COUNT(*) FROM activity GROUP BY activity.user_id ORDER BY COUNT(*) ASC"
        average_query = "SELECT COUNT(activity.id)/COUNT(DISTINCT(activity.user_id)) FROM activity"
        self.cursor.execute(min_max_query)
        min_max = self.cursor.fetchall()
        min = min_max[0][1]
        max = min_max[-1][1]
        self.cursor.execute(average_query)
        average = self.cursor.fetchall()[0][0]
        print("The minimal number of activities per user is:", min)
        print("The maximal number of activities per user is:", max)
        print("The average number of activities per user is:", average)
        return (min, max, average)

    # TASK 3
    def top_10_users_by_activities(self):
        print("\n TASK 3 \n")
        query = "SELECT user_id,COUNT(*) FROM activity GROUP BY activity.user_id ORDER BY COUNT(*) DESC"
        self.cursor.execute(query)
        result = self.cursor.fetchall()[:10]
        for i, user in enumerate(result):
            print(i+1, " User: ", user[0], "has", user[1], "activities")

        # List of tuples with format [(user_id, amount_of_activitues), ]
        return result

    # TASK 4
    def users_start_on_one_day_end_the_next_day(self):
        print("\n TASK 4 \n")
        query = "SELECT COUNT(DISTINCT(activity.user_id)) FROM activity WHERE DATEDIFF(DATE_ADD(start_date_time, interval 1 day), end_date_time) = 0;"
        self.cursor.execute(query)
        result = self.cursor.fetchall()[0][0]
        print("Number of users who started an activity one day, and ended it the next:", result)
        return result

    # TASK 5
    def find_duplicate_activities(self):
        print("\n TASK 5 \n")
        query = "SELECT GROUP_CONCAT(id ORDER BY id) AS duplicate_ids FROM activity GROUP BY transportation_mode, start_date_time, end_date_time HAVING COUNT(*) > 1"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        result = [res[0].split(",") for res in result]
        print("Returned a list of lists containing id of activities with matching 'transportation_mode', 'start_date_time' and 'end_date_time'")
        return result

    # TASK 6
    def covid_19_tracking(self):
        print("\n TASK 6 \n")
        query = "SELECT t1.id, t2.id, t1.user_id, t2.user_id FROM activity AS t1 JOIN activity AS t2 ON (t1.transportation_mode = NULL OR t2.transportation_mode = NULL OR t1.transportation_mode = t2.transportation_mode AND(DATE_SUB(t1.start_date_time, INTERVAL 30 second) > t2.start_date_time AND DATE_SUB(t1.start_date_time, INTERVAL 30 second) < t2.end_date_time) OR (DATE_ADD(t1.end_date_time, INTERVAL 30 second) > t2.start_date_time AND DATE_ADD(t1.end_date_time, INTERVAL 30 second) < t2.start_date_time) OR (DATE_ADD(t1.end_date_time, INTERVAL 30 second) > t2.end_date_time AND DATE_SUB(t1.start_date_time, INTERVAL 30 second) < t2.start_date_time))"
        self.cursor.execute(query)
        activities_within_60_sec = self.cursor.fetchall()
        users = []
        for i, res in enumerate(activities_within_60_sec):
            print("Activity number:", i)
            self.cursor.execute("SELECT * FROM trackpoint WHERE activity_id = {}".format(res[0]))
            a1_trackpoints = self.cursor.fetchall()
            self.cursor.execute("SELECT * FROM trackpoint WHERE activity_id = {}".format(res[1]))
            a2_trackpoints = self.cursor.fetchall()
            for t1 in a1_trackpoints:
                for t2 in a2_trackpoints:
                    distance_between = distance((t1[2], t1[3]), (t2[2], t2[3]))
                    if distance_between <= 100:
                        users.append(res[2])
                        users.append(res[3])
                        break
        user_ids = len(set(users))
        print("The users who have been close to another both in time and space are:", user_ids)
        print("There are", len(user_ids),"users in the list")
        return user_ids



def distance(loc1, loc2):
    return hs.haversine(loc1, loc2, unit=hs.Unit.METERS)


def main():
    q = Queries()
    # TASK 1
    #q.total_amount_of_entries()

    # TASK 2
    #q.min_max_avg_activities()

    # TASK 3
    #q.top_10_users_by_activities()

    # TASK 4
    #q.users_start_on_one_day_end_the_next_day()

    # TASK 5
    #q.find_duplicate_activities()

    # TASK 6
    q.covid_19_tracking()



main()
