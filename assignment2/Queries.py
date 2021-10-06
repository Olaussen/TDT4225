from DbConnector import DbConnector
from tabulate import tabulate
import haversine as hs
import datetime


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
        query = "SELECT a1.id, a2.id, a1.user_id, a2.user_id FROM activity AS a1, activity AS a2 WHERE (a2.start_date_time BETWEEN DATE_SUB(a1.start_date_time, interval 1 minute) AND DATE_ADD(a1.end_date_time, interval 1 minute) OR a2.end_date_time BETWEEN DATE_SUB(a1.start_date_time, interval 1 minute) AND DATE_ADD(a1.end_date_time, interval 1 minute)) AND a1.id != a2.id AND a1.user_id != a2.user_id"
        print("Fetching overlapping activities in time \n")
        self.cursor.execute(query)
        activities_within_60_sec = self.cursor.fetchall()
        print("Calculating times and distance")
        users = []
        for i in range(len(activities_within_60_sec)):
            print("Checking activity:", i+1)
            a1 = activities_within_60_sec[i][0]
            a2 = activities_within_60_sec[i][1]
            u1 = activities_within_60_sec[i][2]
            u2 = activities_within_60_sec[i][3]
            u1_already_in = u1 in users
            u2_already_in = u2 in users
            if u1_already_in and u2_already_in:
                continue
            self.cursor.execute("SELECT lat, lon, date_time FROM trackpoint WHERE activity_id = {}".format(a1))
            a1_trackpoints = self.cursor.fetchall()
            self.cursor.execute("SELECT lat, lon, date_time FROM trackpoint WHERE activity_id = {}".format(a2))
            a2_trackpoints = self.cursor.fetchall()
            for t1 in a1_trackpoints:
                for t2 in a2_trackpoints:
                    close_time = abs((t1[2]- t2[2]).total_seconds()) < 60
                    if not close_time:
                        continue
                    close_space = distance((t1[0], t1[1]), (t2[0], t2[1])) < 0.1
                    if close_space:
                        if not u1_already_in:
                            users.append(u1)
                        if not u2_already_in:
                            users.append(u2)
                        break
        print(users)



        trackpoints = self.cursor.fetchall()
        
        print(len(activities_within_60_sec))

    # TASK 7
    def never_taken_taxi(self):
        print("\n TASK 7 \n")
        query = "SELECT DISTINCT id FROM user WHERE id NOT IN (SELECT DISTINCT user_id FROM activity WHERE transportation_mode = 'taxi')"
        self.cursor.execute(query)
        result = [res[0] for res in self.cursor.fetchall()]
        print("Resturned a list of ids for all users having not taken a taxi")
        return result

     # TASK 8
    def transportation_mode_count(self):
        print("\n TASK 8 \n")
        query = "SELECT transportation_mode, COUNT(DISTINCT user_id) FROM activity WHERE transportation_mode IS NOT NULL GROUP BY transportation_mode"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        for tup in result:
            print("Transportation mode",
                  tup[0], "has been used by", tup[1], "discinct users")
        return result

    # TASK 9a
    def most_active_year(self):
        print("\n TASK 9a \n")
        query = "SELECT YEAR(start_date_time), MONTH(start_date_time), COUNT(1) FROM activity GROUP BY YEAR(start_date_time), MONTH(start_date_time) ORDER BY count(1) DESC LIMIT 1;"
        self.cursor.execute(query)
        result = self.cursor.fetchall()[0]
        print("Year and month with most activities:")
        print("Year:", result[0], "Month:", result[1], "Amount:", result[2])
        return result

     # TASK 9b
    def user_with_most_activities_from_9a(self):
        print("\n TASK 9b \n")
        # Found in 9a
        YEAR = 2008
        MONTH = 11
        query = "SELECT user_id, SUM(timestampdiff(SECOND, start_date_time, end_date_time))/3600 ,COUNT(1) FROM activity WHERE MONTH(start_date_time)= %s AND YEAR(start_date_time)= %s GROUP BY user_id ORDER BY COUNT(1) DESC LIMIT 2"
        self.cursor.execute(query % (MONTH, YEAR))
        result = self.cursor.fetchall()
        print("Top users with most activities in year", YEAR, "and month", MONTH)
        for i, user in enumerate(result):
            print(i+1, "| User", user[0], "had", user[2], "activities | A total of", user[1], "hours were used")
        return result

    # TASK 10
    def distance_walked_in_2008(self):
        print("\n TASK 10 \n")
        query = "SELECT activity_id, lat, lon FROM trackpoint JOIN (SELECT id FROM activity WHERE user_id = 112 AND transportation_mode = 'walk' AND YEAR(start_date_time)= 2008) AS activities WHERE YEAR(trackpoint.date_time) = 2008 AND trackpoint.activity_id = activities.id;"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        current_activity = None
        total_distance = 0
        part_distance = 0
        for i in range(len(result)-1):
            lat1 = result[i][1]
            lon1 = result[i][2]
            lat2 = result[i+1][1]
            lon2 = result[i+1][2]
            next_id = result[i+1][0]
            if(next_id != current_activity):
                current_activity = next_id
                total_distance += part_distance
                part_distance = 0
            part_distance += distance((lat1, lon1), (lat2, lon2))
        print("User 112 walked {}km in 2008".format(total_distance))
        return total_distance

    # TASK 11
    def most_altitude_gained(self):
        print("\n TASK 11 \n")
        query = "SELECT a1.user_id, SUM(altitude_gained) * 0.3048 FROM (SELECT t1.activity_id AS aid, SUM(t2.altitude - t1.altitude) AS altitude_gained FROM trackpoint AS t1 JOIN  trackpoint AS t2 ON  t1.id = t2.id - 1 WHERE t2.altitude > t1.altitude AND t1.altitude != -777 AND t2.altitude != -777 GROUP BY t1.activity_id) AS tab, activity AS a1 WHERE aid = a1.id GROUP BY a1.user_id ORDER BY SUM(altitude_gained) DESC LIMIT 20;"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        for i, tup in enumerate(result):
            print(i+1, "| User", tup[0], "has gained", tup[1], "total meters")
        return result

    # TASK 12
    def invalid_activities(self):
        print("\n TASK 12 \n")
        query = "SELECT activity.user_id, COUNT(DISTINCT(activity.id)) AS Invalid FROM activity JOIN activity AS a2 ON activity.user_id = a2.user_id JOIN trackpoint AS t1 ON t1.activity_id = activity.id JOIN trackpoint AS t2 ON t1.id = t2.id - 1 WHERE t1.activity_id = t2.activity_id AND timestampdiff(SECOND, t1.date_time, t2.date_time) >= 300 GROUP BY activity.user_id ORDER BY COUNT(DISTINCT activity.id) DESC"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        print("Top 3 users with most invalid activities")
        for i in range(3):
            print(i+1, "| User", result[i][0], "has", result[i][1], "invalid activities")
        return result # The function returns the full result

def distance(loc1, loc2):
    return hs.haversine(loc1, loc2)


def main():
    q = Queries()
    # TASK 1
    # q.total_amount_of_entries()

    # TASK 2
    # q.min_max_avg_activities()

    # TASK 3
    # q.top_10_users_by_activities()

    # TASK 4
    # q.users_start_on_one_day_end_the_next_day()

    # TASK 5
    # q.find_duplicate_activities()

    # TASK 6
    q.covid_19_tracking()

    # TASK 7
    # q.never_taken_taxi()

    # TASK 8
    # q.transportation_mode_count()

    # TASK 9a
    # q.most_active_year()

    # TASK 9b
    #q.user_with_most_activities_from_9a()

    # TASK 10
    #q.distance_walked_in_2008()

    # TASK 11
    #q.most_altitude_gained()

    # Task 12
    #q.invalid_activities()


main()
