from DbConnector import DbConnector
import time
import datetime


class Queries:
    def __init__(self):
        self.connection = DbConnector()
        self.client = self.connection.client
        self.db = self.connection.db

    # TASK 1
    def count_all_entries(self):
        start = time.time()
        print("\nTASK 1 \n \n")
        users = self.db["users"]
        users = users.find({})
        total_users = 0
        total_activities = 0
        total_trackpoints = self.db["trackpoints"].count_documents({})
        for user in users:
            total_users += 1
            total_activities += len(user["activities"])

        print("Total amount of users:", total_users)
        print("Total amount of activities:", total_activities)
        print("Total amount of trackpoints:", total_trackpoints)
        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))

    # TASK 2
    def average_max_min(self):
        start = time.time()
        print("\nTASK 2 \n \n")
        users = self.db["users"]
        users = users.find({})
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
        ac_avg = ac_total / users.count()

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
                ac_start = ac["start_date_time"] + datetime.timedelta(days=1)
                ac_end = ac["end_date_time"]
                next_day = ac_start.day == ac_end.day
                if next_day:
                    result.add(user["_id"])
                    break
        amount = len(result)
        print("Amount of users with activities ending the day after starting:", amount)
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
                ac_start = ac["start_date_time"] + datetime.timedelta(days=1)
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
            print(u1["_id"])
            for u2 in users:
                if u1["_id"] == u2["_id"] or (u1["_id"], u2["_id"]) in checked:
                    continue
                ac1 = u1["activities"]
                ac2 = u2["activities"]
                for a1 in ac1:
                    for a2 in ac2:
                        if  a1["start_date_time"] == a2["start_date_time"] and a1["transportation_mode"] == a2["transportation_mode"] and a1["end_date_time"] == a2["end_date_time"]:
                            result.append((a1["_id"], a2["_id"]))
                checked.append((u1["_id"],  u2["_id"]))
                checked.append((u2["_id"],  u1["_id"]))
        print("Returned a list of lists containing id of activities with matching 'transportation_mode', 'start_date_time' and 'end_date_time'")
        print("It contains", len(result), "elements")

        print("\nTime used: %s seconds" % (round(time.time() - start, 5)))
        return result


def main():
    q = Queries()

    # TASK 1
    # q.count_all_entries()

    # TASK 2
    # q.average_max_min()

    # TASK 3
    # q.top_10_users()

    # TASK 4
    # q.started_one_day_ended_next()

    # TASK 5
    q.duplicate_activities()


main()
