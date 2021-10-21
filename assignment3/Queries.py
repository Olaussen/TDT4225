from typing import List

from numpy.testing._private.utils import tempdir
from DbConnector import DbConnector
import time
from datetime import datetime, timedelta
import haversine as hs
import pandas as pd

class Queries:
    def __init__(self):
        self.connection = DbConnector()
        self.client = self.connection.client
        self.db = self.connection.db

    # TASK 1

    def count_all_entries(self):
        start = time.time()
        print("\nTASK 1\n \n")
        users = self.db["users"]
        total_users = users.count_documents(filter={})
        total_activities = users.aggregate([
            {"$unwind": "$activities"},
            {"$count": "activities"}]).next()
        total_trackpoints = self.db["trackpoints"].count_documents({})
        print("Total amount of users:", total_users)
        print("Total amount of activities:", total_activities['activities'])
        print("Total amount of trackpoints:", total_trackpoints)
        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))

    # TASK 2

    def average_max_min(self):
        start = time.time()
        print("\nTASK 2 \n \n")
        users = self.db["users"]
        users = list(users.find({}))
        ac_total = 0
        ac_min = float("inf")
        ac_max = -float("inf")
        for user in users:
            length = len(user["activities"])
            ac_total += length
            if length > ac_max:
                ac_max = length

            if length < ac_min:
                ac_min = length
        ac_avg = ac_total / len(users)

        print("Minimum number of activitites:", ac_min)
        print("Maximum number of activitites:", ac_max)
        print("Average number of activitites:", ac_avg)
        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))

    # TASK 3

    def top_10_users(self):
        start = time.time()
        print("\nTASK 3 \n \n")

        def second(elem):
            return elem[1]

        users = self.db["users"]
        users = users.find({})
        top_list = []
        for user in users:
            length = len(user["activities"])
            # We sort the list for each time it is updated, leavig the worst of the top 10 at the back of the list
            # When we encounter a user with more activities than last one in the list, we pop it, and appends the
            # newly encountered user with the number of activities and sort the list again to find its position.
            if len(top_list) == 10 and length > top_list[-1][1]:
                top_list.pop()
                top_list.append((user["_id"], len(user["activities"])))
                top_list.sort(key=second, reverse=True)
            # If we have not yet gotten 10 users in the top 10 list, we can just add them
            elif len(top_list) < 10:
                top_list.append((user["_id"], len(user["activities"])))
        for i, top in enumerate(top_list):
            print("%s| User %s has %s stored activities" %
                  (i+1, top[0], top[1]))
        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))

    # TASK 4
    def started_one_day_ended_next(self):
        start = time.time()
        print("\nTASK 4 \n \n")
        users = self.db["users"]
        users = users.find({})
        result = set()
        for user in users:
            for ac in user["activities"]:
                # Adds one day to the start day
                ac_start = ac["start_date_time"] + timedelta(days=1)
                ac_end = ac["end_date_time"]
                # If the days are the same, the activity ended the day after the start date
                next_day = ac_start.day == ac_end.day
                if next_day:
                    result.add(user["_id"])
                    break
        amount = len(result)
        print("Amount of users with activities ending the day after starting:", amount)
        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))

    # TASK 5
    def duplicate_activities(self):
        start = time.time()
        print("\nTASK 5 \n \n")
        users = self.db["users"]
        users = list(users.find({}))
        checked = []
        result = []
        for u1 in users:
            for u2 in users:
                # One user does not have duplicates, so if we have the same user id, we just continue.
                # If we have already checked two users against eachothers activities, we just continue
                # as we do not need to check a1 against a2 and a2 against a1. They have already been counted.
                if u1["_id"] == u2["_id"] or (u1["_id"], u2["_id"]) in checked:
                    continue
                ac1 = u1["activities"]
                ac2 = u2["activities"]
                for a1 in ac1:
                    for a2 in ac2:
                        # If they have the same start, end and mode, we count it as duplicate
                        if a1["start_date_time"] == a2["start_date_time"] and a1["transportation_mode"] == a2["transportation_mode"] and a1["end_date_time"] == a2["end_date_time"]:
                            result.append((a1["_id"], a2["_id"]))
                checked.append((u1["_id"],  u2["_id"]))
                checked.append((u2["_id"],  u1["_id"]))
        print("Returned a list of lists containing id of activities with matching 'transportation_mode', 'start_date_time' and 'end_date_time'")
        print("It contains", len(result), "elements")

        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))
        return result

    # TASK 6
    def covid_19_tracking(self):
        start = time.time()
        print("\nTASK 6 \n \n")
        users = self.db["users"]
        trackpoints = self.db["trackpoints"]
        users = list(users.find({}))

        ground_zero = (116.33031, 39.97548)
        infected_time = datetime.fromisoformat('2008-08-24 15:38:00')

        # Will hold the list of users with activities whos time overlaps with the infected time within 1 min
        possible_activities = {}
        result = []

        for user in users:
            ac_list = user["activities"]
            for ac in ac_list:
                # Extends the start and end times with 1 minute and checks whether or not to add the activity to the
                # possible_activities list
                if (ac["start_date_time"] - timedelta(minutes=1) < infected_time) and (ac["end_date_time"] + timedelta(seconds=60)) > infected_time:
                    if user["_id"] in possible_activities:
                        possible_activities[user["_id"]].append(ac["_id"])
                    else:
                        possible_activities[user["_id"]] = [ac["_id"]]

        for user in possible_activities:
            ac_list = possible_activities[user]
            for ac in ac_list:
                tp_list = list(trackpoints.find({"activity_id": ac}))
                for trackpoint in tp_list:
                    # Checks time and distance to find out if the user should be contacted
                    if (trackpoint["date_time"] - timedelta(minutes=1) < infected_time) or (trackpoint["date_time"] + timedelta(minutes=1) < infected_time):
                        if distance(ground_zero, trackpoint["location"]["coordinates"]) < 0.1:
                            result.append(user)
                            break

        for res in result:
            print("User %s has been within 100m and one minute" % res)

        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))

    # TASK 7
    def users_no_taxi(self):
        start = time.time()
        print("\nTASK 7 \n \n")
        users = self.db["users"]
        users = list(users.aggregate(
            [{"$match": {"activities.transportation_mode": {"$ne": "taxi"}}}]))

        print("Returned a list containing %s user ids" % len(users))
        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))
        return users

    # TASK 8
    def transportation_mode_usage(self):
        start = time.time()
        print("\nTASK 8 \n \n")
        users = self.db["users"]
        users = list(users.find({}))

        # Dict on the form {mode: set(user_ids)}
        transportation_modes = {}

        for user in users:
            ac_list = user["activities"]
            for ac in ac_list:
                mode = ac["transportation_mode"]
                # Checks if mode is None
                if not mode:
                    continue
                # If the mode exists in the dict, we add the user id to the set
                # If not, we initialize the set
                if mode in transportation_modes:
                    transportation_modes[mode].add(user["_id"])
                else:
                    transportation_modes[mode] = set(user["_id"])
        # Translates the dict to {mode: amount} by counting the set of distinct user ids
        # who have used the transportation mode
        for tm in transportation_modes:
            transportation_modes[tm] = len(transportation_modes[tm])
            print("%s has been used by %s users" %
                  (tm, transportation_modes[tm]))

        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))
        return transportation_modes

    # TASK 9a
    def year_month_most_activities(self):
        start = time.time()
        print("\nTASK 9a \n \n")
        users = self.db["users"]
        users = list(users.aggregate([{"$unwind": "$activities"}]))

        # Dict on the form {yyyy-mm: amount}
        years = {}

        for user in users:
            ac = user["activities"]
            year = str(ac["start_date_time"].year)
            month = str(ac["start_date_time"].month)
            key = "%s-%s" % (year, month)
            # Adds one to the dict entry when year and month is encountered again
            # Initializes it if it is the first
            if key in years: years[key] += 1
            else: years[key] = 1
        # Sorts and reverses the list to get the top year and month
        years = list(sorted(years.items(), key=lambda item: item[1], reverse=True))
        
        top = years[0]
        # Extracts the year and month from the key
        top_y, top_m = top[0].split("-")
        amount = top[1]
        print("The year and month with most activities was month number %s in year %s with a total of %s activities" % (top_m, top_y, amount))
        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))
        return top_y, top_m

    # TASK 9b
    def user_with_most_activities_11_2008(self):
        start = time.time()
        print("\nTASK 9b \n \n")
        # From TASK 9a
        YEAR = 2008
        MONTH = 11 
        users = self.db["users"]
        users = list(users.aggregate([{"$unwind": "$activities"}]))

        # Dict on form {userid: {amount: amount, hours: hours}}
        result = {}

        for user in users:
            ac = user["activities"]
            # Finds all activities with the same year and month
            if ac["start_date_time"].year == YEAR and ac["start_date_time"].month == MONTH:
                # If the user id has beed encountered, adds 1 to the amount and total hours to the hours
                if user["_id"] in result:
                    result[user["_id"]]["amount"] += 1
                    result[user["_id"]]["hours"] += (ac["end_date_time"] - ac["start_date_time"]).total_seconds()/3600
                else:
                    # Initializes the first dict for a user id
                    result[user["_id"]] = {"amount": 1, "hours":(ac["end_date_time"] - ac["start_date_time"]).total_seconds()/3600}

        # Sorts and limits the list to the top two users based on amount of activities
        result = list(sorted(result.items(), key=lambda item: item[1]["amount"], reverse=True))[:2]
        print("1| User %s has the most activities in %s-%s, with %s activities and a total of %s hours" % (result[0][0], MONTH, YEAR, result[0][1]["amount"], round(result[0][1]["hours"], 4)))
        print("2| User %s has the second most activities in %s-%s, with %s activities and a total of %s hours, which is more than number one" % (result[1][0], MONTH, YEAR, result[1][1]["amount"], round(result[1][1]["hours"], 4)))
        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))

    # TASK 10
    def user_112_walk_2008(self):
        start = time.time()
        print("\nTASK 10 \n \n")
        users = self.db["users"]
        user = list(users.find({"_id": "112"}))[0]
        ac_list = user["activities"]
        # Gets all the activities for user 112 with transportation mode walk
        ac_list = list(filter(lambda ac: ac["transportation_mode"] == "walk", ac_list))
        # Retrieves the activity ids
        ac_ids = [ac["_id"] for ac in ac_list]
        # Gets all the trackpoints for all the activities in the list
        trackpoints = self.db["trackpoints"]
        trackpoints = list(trackpoints.find({"activity_id": {"$in": ac_ids}}))

        current_activity = None
        total_distance = 0
        part_distance = 0
        for i in range(len(trackpoints) - 1):
            # Extracts the locations for the current trackpoint and the next
            # to calculate the distance further down
            loc1 = trackpoints[i]["location"]["coordinates"]
            loc2 = trackpoints[i+1]["location"]["coordinates"]
            # Checks if we for the next iteration should reset the part-data
            next_id = trackpoints[i+1]["activity_id"]
            # If we are not on the same activity anymore, update the current_activity and 
            # add the calculated distance to the total
            if(next_id != current_activity):
                current_activity = next_id
                total_distance += part_distance
                part_distance = 0
            # Adds the distance between the trackpoints to the part_distance
            part_distance += distance(loc1, loc2)

        print("User 112 walked %s km in 2008" % (total_distance))

        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))
 
    # TASK 11
    def top_20_users_altitude(self):
        start = time.time()
        print("\nTASK 11 \n \n")
        users = self.db["users"]
        users = users.find({})
        trackpoints = self.db["trackpoints"]

        result = []
        for user in users:
            ac_list = user["activities"]
            # Total user altitude
            total_user_alt = 0
            # Total activity altitude
            total_ac_alt = 0
            for ac in ac_list:
                # Gets the trackpoints for the current activity whos altitude is not -777
                tp_list = list(trackpoints.find({"altitude": {"$ne": -777}, "activity_id": ac["_id"]}, {"activity_id": 1, "altitude": 1, "_id": 0}))
                for i in range(len(tp_list) - 1):
                    # Finds the difference between this trackpoint and the next
                    diff = tp_list[i+1]["altitude"] - tp_list[i]["altitude"]
                    # If the difference is posivive we add it to the total activity altitude counter
                    if diff > 0:
                        total_ac_alt += diff
                # When the activity is done, we add the total multiplied with 0.3048 (1 foot) to the user total
                total_user_alt += total_ac_alt * 0.3048
                # Resets the total activity altitude for the next activity
                total_ac_alt = 0
            result.append((user["_id"], total_user_alt))
            
        # Using pandas to display the results in a nice manner
        df = pd.DataFrame(list(sorted(result, key=lambda item: item[1], reverse=True)[:20]), columns=["UserID", "Altitude gained in meters"])
        pd.set_option('display.max_rows', df.shape[0]+1)
        print(df.to_string(index=False))

        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))

    # TASK 12
    def invalid_activities(self):
        start = time.time()
        print("\nTASK 12 \n \n")
        users = self.db["users"]
        users = users.find({})
        trackpoints = self.db["trackpoints"]
        result = []
        for user in users:
            ac_list = user["activities"]
            # Count of invalid activities for this user
            ac_count = 0
            for ac in ac_list:
                # Gets all trackpoints with the given activity id
                tp_list = list(trackpoints.find({"activity_id": ac["_id"]}, {"activity_id": 1, "date_time": 1, "_id": 0}))
                for i in range(len(tp_list) - 1):
                    # Extracts the time for this trackpoint and the next
                    time1 = tp_list[i]["date_time"]
                    time2 = tp_list[i+1]["date_time"] 
                    # Checks if the time difference is more than 300 secs (5 min) and adds 1 
                    # to the count as the activity is then invalid.
                    if (time2 - time1).total_seconds() > 300:
                        ac_count += 1
                        break
            result.append((user["_id"], ac_count))
                      
        # Using pandas to display the results in a nice manner
        df = pd.DataFrame(list(sorted(result, key=lambda item: item[1], reverse=True)[:20]), columns=["UserID", "AMount of invalid activities"])
        pd.set_option('display.max_rows', df.shape[0]+1)
        print(df.to_string(index=False))

        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))

    
# Distance calculations - returns the distance in kilometers
def distance(loc1, loc2):
    return hs.haversine(loc1, loc2)


def main():
    q = Queries()

    # TASK 1
    #q.count_all_entries()

    # TASK 2
    #q.average_max_min()

    # TASK 3
    #q.top_10_users()

    # TASK 4
    #q.started_one_day_ended_next()

    # TASK 5
    #q.duplicate_activities()

    # TASK 6
    q.covid_19_tracking()

    # TASK 7
    #q.users_no_taxi()

    # TASK 8
    #q.transportation_mode_usage()

    # TASK 9a
    #q.year_month_most_activities()

    # TASK 9b
    #q.user_with_most_activities_11_2008()

    # TASK 10
    #q.user_112_walk_2008()

    #Task 11
    #q.top_20_users_altitude()

    #Task 12
    #q.invalid_activities()


main()
