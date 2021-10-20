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
            if len(top_list) == 10 and length > top_list[-1][1]:
                top_list.pop()
                top_list.append((user["_id"], len(user["activities"])))
                top_list.sort(key=second, reverse=True)
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
                ac_start = ac["start_date_time"] + timedelta(days=1)
                ac_end = ac["end_date_time"]
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
                if u1["_id"] == u2["_id"] or (u1["_id"], u2["_id"]) in checked:
                    continue
                ac1 = u1["activities"]
                ac2 = u2["activities"]
                for a1 in ac1:
                    for a2 in ac2:
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

        possible_activities = {}
        result = []

        for user in users:
            ac_list = user["activities"]
            for ac in ac_list:
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

        transportation_modes = {}

        for user in users:
            ac_list = user["activities"]
            for ac in ac_list:
                mode = ac["transportation_mode"]
                if not mode:
                    continue
                if mode in transportation_modes:
                    transportation_modes[mode].add(user["_id"])
                else:
                    transportation_modes[mode] = set(user["_id"])
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
        years = {}

        for user in users:
            ac = user["activities"]
            year = str(ac["start_date_time"].year)
            month = str(ac["start_date_time"].month)
            key = "%s-%s" % (year, month)
            if key in years: years[key] += 1
            else: years[key] = 1
        years = list(sorted(years.items(), key=lambda item: item[1], reverse=True))
        
        top = years[0]
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
        result = {}

        for user in users:
            ac = user["activities"]
            if ac["start_date_time"].year == YEAR and ac["start_date_time"].month == MONTH:
                if user["_id"] in result:
                    result[user["_id"]] += 1
                else:
                    result[user["_id"]] = 1
        result = list(sorted(result.items(), key=lambda item: item[1], reverse=True))[0]

        print("User %s has the most activities in %s-%s, with %s activities" % (result[0], MONTH, YEAR, result[1]))
        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))

    # TASK 10
    def user_112_walk_2008(self):
        start = time.time()
        print("\nTASK 10 \n \n")
        users = self.db["users"]
        user = list(users.find({"_id": "112"}))[0]
        ac_list = user["activities"]
        ac_list = list(filter(lambda ac: ac["transportation_mode"] == "walk", ac_list))
        ac_ids = [ac["_id"] for ac in ac_list]
        trackpoints = self.db["trackpoints"]
        trackpoints = list(trackpoints.find({"activity_id": {"$in": ac_ids}}))
        current_activity = None
        total_distance = 0
        part_distance = 0
        for i in range(len(trackpoints) - 1):
            loc1 = trackpoints[i]["location"]["coordinates"]
            loc2 = trackpoints[i+1]["location"]["coordinates"]
            next_id = trackpoints[i+1]["activity_id"]
            # If we are not on the same activity anymore, update the current_activity and 
            # add the calculated distance to the total
            if(next_id != current_activity):
                current_activity = next_id
                total_distance += part_distance
                part_distance = 0
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
            print("User", user["_id"])
            ac_list = user["activities"]
            total_user_alt = 0
            total_ac_alt = 0
            for ac in ac_list:
                tp_list = list(trackpoints.find({"altitude": {"$ne": -777}, "activity_id": ac["_id"]}, {"activity_id": 1, "altitude": 1, "_id": 0}))
                for i in range(len(tp_list) - 1):
                    diff = tp_list[i+1]["altitude"] - tp_list[i]["altitude"]
                    if diff > 0:
                        total_ac_alt += diff
                total_user_alt += total_ac_alt * 0.3048
                total_ac_alt = 0
            result.append((user["_id"], total_user_alt))
            
        
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
            print("User", user["_id"])
            ac_list = user["activities"]
            ac_count = 0
            for ac in ac_list:
                tp_list = list(trackpoints.find({"activity_id": ac["_id"]}, {"activity_id": 1, "date_time": 1, "_id": 0}))
                for i in range(len(tp_list) - 1):
                    time1 = tp_list[i]["date_time"]
                    time2 = tp_list[i+1]["date_time"] 
                    if (time2 - time1).total_seconds() > 300:
                        ac_count += 1
                        break
            result.append((user["_id"], ac_count))
                      
        df = pd.DataFrame(list(sorted(result, key=lambda item: item[1], reverse=True)[:20]), columns=["UserID", "AMount of invalid activities"])
        pd.set_option('display.max_rows', df.shape[0]+1)
        print(df.to_string(index=False))

        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))

    

def distance(loc1, loc2):
    return hs.haversine(loc1, loc2)


def main():
    q = Queries()

    # TASK 1
    q.count_all_entries()

    # TASK 2
    q.average_max_min()

    # TASK 3
    q.top_10_users()

    # TASK 4
    q.started_one_day_ended_next()

    # TASK 5
    q.duplicate_activities()

    # TASK 6
    q.covid_19_tracking()

    # TASK 7
    q.users_no_taxi()

    # TASK 8
    q.transportation_mode_usage()

    # TASK 9a
    q.year_month_most_activities()

    # TASK 9b
    q.user_with_most_activities_11_2008()

    # TASK 10
    q.user_112_walk_2008()

    #Task 11
    q.top_20_users_altitude()

    #Task 12
    q.invalid_activities()


main()
