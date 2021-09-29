from numpy.core.shape_base import atleast_1d
import pandas as pd
import os
from datetime import datetime


class Preprocessor:
    def __init__(self):
        self.root = "./dataset"
        #self.users = self.construct_user_list()
        #self.activities = self.construct_activity_list()
        self.trackpoints = self.construct_trackpoint_list()

    def line_count(self, path):
        return sum(1 for _ in open(path))

    def validated_activity(self, path):
        return self.line_count(path) < 2512

    def extract_date_times(self, activity):
        dates = activity["date"]
        times = activity["time"]
        return datetime.fromisoformat(dates[0] + " " + times[0]), datetime.fromisoformat(dates[len(dates) - 1] + " " + times[len(times) - 1])

    def construct_user(self, id, has_labels, activities=[]):
        return {"id": id, "has_labels": has_labels, "activities": activities}

    def construct_activity(self, id, user_id, transportation_mode, start_date_time, end_date_time):
        return {"id": id, "user_id": user_id, "transportation_mode": transportation_mode, "start_date_time": start_date_time, "end_date_time": end_date_time}

    def construct_trackpoint(self, activity_id, lat, lon, altitude, days, time):
        return {"activity_id": activity_id, "lat": lat, "lon": lon, "altitude": altitude, "date_days": days, "date_time": time}

    def format_path(self, root, sub_path):
        return "{root}/{sub}".format(root=root, sub=sub_path)

    def read_labeled_users(self):
        path = self.format_path(self.root, "labeled_ids.txt")
        return [res[0] for res in pd.read_csv(path, header=None).to_numpy()]

    def read_user_ids(self):
        path = self.format_path(self.root, "Data")
        return [os.path.join(path, file)[-3:] for file in os.listdir(path)]

    def user_has_labeled(self, id):
        labeled = self.read_labeled_users()
        return int(id) in labeled

    def construct_user_list(self):
        return [self.construct_user(id, self.user_has_labeled(id)) for id in self.read_user_ids()]

    def has_transportation_mode(self, labels, start, end):
        for _, label in labels.iterrows():
            date_start_string = label["start"].replace("/", "-")
            date_end_string = label["end"].replace("/", "-")
            label_start = datetime.fromisoformat(date_start_string)
            label_end = datetime.fromisoformat(date_end_string)
            time_match = label_start == start and label_end == end
            if time_match:
                print("Time match! : Mode:", label["mode"])
                return label["mode"]
        return None

    def construct_activity_list(self):
        activities = []
        root = self.format_path(self.root, "Data")
        for user in os.listdir(root):
            labeled_user = self.user_has_labeled(user)
            user_path = self.format_path(root, user + "/Trajectory")
            print("Constructing activities for user:", user)
            for activity in os.listdir(user_path):
                activity_path = self.format_path(user_path, activity)
                valid = self.validated_activity(activity_path)
                if not valid:
                    continue
                trackpoints = pd.read_csv(activity_path, names=[
                                          "lat", "lon", "piss", "alt", "days", "date", "time"], skiprows=6)
                start_date_time, end_date_time = self.extract_date_times(
                    trackpoints)
                id = int(activity[:-4] + user)
                if not labeled_user:
                    activities.append(self.construct_activity(id, user, None, start_date_time, end_date_time))
                else:
                    # TODO Check whether the labels correspond to this activity
                    labels_path = self.format_path(self.root, "Data/{}/labels.txt".format(user))
                    labels = pd.read_csv(labels_path, sep="\t", header=None, skiprows=1)
                    labels.columns = ["start", "end", "mode"]
                    mode = self.has_transportation_mode(labels, start_date_time, end_date_time)
                    activities.append(self.construct_activity(id, user, mode, start_date_time, end_date_time))
        return activities

    def construct_trackpoint_list(self):
        root = self.format_path(self.root, "Data")
        count = 0
        with open("trackpoints.csv", "w") as f:
            f.write("activity_id,lat,lon,altitude,date_days,date_time\n")
            for user in os.listdir(root):
                user_path = self.format_path(root, user + "/Trajectory")
                print("Currently on user:", user)
                print("Trackpoints so far: ", count)
                for activity in os.listdir(user_path):
                    activity_path = self.format_path(user_path, activity)
                    valid = self.validated_activity(activity_path)
                    if not valid:
                        continue
                    trackpoints = pd.read_csv(activity_path, names=[
                                            "lat", "lon", "ignore", "alt", "days", "date", "time"], skiprows=6)
                    activity_id = int(activity[:-4] + user)
                    for _, trackpoint in trackpoints.iterrows():
                        count += 1
                        lat = float(trackpoint["lat"])
                        lon = float(trackpoint["lon"])
                        alt = int(trackpoint["alt"])
                        days = float(trackpoint["days"])
                        time = datetime.fromisoformat(trackpoint["date"] + " " + trackpoint["time"]) 
                        #constructed = self.construct_trackpoint(activity_id, lat, lon, alt, days, time)
                        #constructed_trackpoints.append(constructed)
                        # Writing data to a file
                        f.write("{id},{lat},{lon},{alt},{days},{time}\n".format(id=activity_id, lat=lat, lon=lon, alt=alt, days=days, time=time))

def main():
    p = Preprocessor()
    #p.construct_trackpoint_list()

main()