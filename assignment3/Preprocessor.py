from numpy.core.shape_base import atleast_1d
import pandas as pd
import os
from datetime import datetime
from json import dump


"""
    Class for all preprocessing of data in assignment 3
"""


class Preprocessor:
    def __init__(self):
        self.users = []
        self.trackpoints = []
        self.labeled_users = self.read_labeled_users()

    """
        Function for finding the start and end time of an activity.

        input: pd.DataFrame - Pandas DataFrame with the trackpoint data in the activity file
        returns: (start: DateTime, end: DateTime) - Tuple with the two dates
    """

    def extract_date_times(self, activity):
        dates = activity["date"]
        times = activity["time"]
        return datetime.fromisoformat(dates[0] + " " + times[0]), datetime.fromisoformat(dates[len(dates) - 1] + " " + times[len(times) - 1])

    """
        Function for getting the ids of all users with labels.

        returns: list(string) - A python list with all the user ids in the "labeled_ids.txt" file
    """

    def read_labeled_users(self):
        path = "./dataset/labeled_ids.txt"
        return ['{:03}'.format(res[0]) for res in pd.read_csv(path, header=None).to_numpy()]

    """
        Function for getting the ids of all users.

        returns: list(string) - A python list with all the user ids
    """

    def read_user_ids(self):
        path = "./dataset/Data"
        return [os.path.join(path, file)[-3:] for file in os.listdir(path)]

    """
        Function for checking whether or not a user has labels.

        input: string - User id
        returns: boolean - True if the user with the given id has labels, else False
    """

    def user_has_labeled(self, id):
        return id in self.labeled_users

    """
        Function for checking if the start and endtime of an activity matches with one in the users "labels.txt" file.

        input:
            opened: pd.DataFrame - Labels file for user
            start: DateTime - Starting date of activity
            end: DateTime - End date of activity
        returns: boolean - True if the start AND end times of a label matches with the parametes, else False
    """

    def has_transportation_mode(self, opened, start, end):
        for _, label in opened.iterrows():
            date_start_string = label["start"].replace("/", "-")
            date_end_string = label["end"].replace("/", "-")
            label_start = datetime.fromisoformat(date_start_string)
            label_end = datetime.fromisoformat(date_end_string)
            # If the parameters matches with one of the labels we return the label
            time_match = label_start == start and label_end == end
            if time_match:
                print("Found match:", label["mode"])
                return label["mode"]
        return None


    

    """
        Main function that will read all the data from the dataset folder and dump the preprocessed data
        into three separate files for users, activities and trackpoints to be used in DbHandler.py
    """

    def preprocess(self):
        current_user = {"_id": "000", "has_labeled": False}
        current_activities = []
        for root, _, files in os.walk("./dataset/Data"):
            user_id = root.split("./dataset/Data")[1][1:4]
            is_trajectory = root.split("./dataset/Data")[1][5:] != ""
            if not is_trajectory or user_id != "181":
                continue

            if user_id != current_user["_id"]:
                current_user["activities"] = current_activities
                #self.users.append(current_user)
                has_labeled = self.user_has_labeled(user_id)
                current_user = {"_id": user_id,
                                "has_labeled": has_labeled}
                current_activities = []
                print("Currently on user:", user_id)
            for file in files:
                path = os.path.join(root, file)
                activity_id = file[:-4] + user_id
                opened = pd.read_csv(
                    path, names=["lat", "lon", "skip", "alt", "days", "date", "time"], skiprows=6)
                if len(opened) > 2500:
                    continue
                start, end = self.extract_date_times(opened)
                if current_user["has_labeled"]:
                    labels_file = pd.read_csv(
                        "./dataset/Data/%s/labels.txt" % (user_id), sep="\t", header=None, skiprows=1)
                    labels_file.columns = ["start", "end", "mode"]
                    mode = self.has_transportation_mode(
                        labels_file, start, end)
                    activity = {"_id": activity_id, "transportation_mode": mode,
                                "start_date_time": start, "end_date_time": end}
                else:
                    activity = {"_id": activity_id, "transportation_mode": None,
                                "start_date_time": start, "end_date_time": end}
                for _, trackpoint in opened.iterrows():
                    date = datetime.fromisoformat("{} {}".format(trackpoint["date"], trackpoint["time"]))
                    self.trackpoints.append({"activity_id": activity_id, "location": {"type": "Point", "coordinates": [trackpoint["lon"], trackpoint["lat"]]},
                                        "altitude": trackpoint["alt"], "date_days": trackpoint["days"], "date_time": date})
                current_activities.append(activity)
        current_user["activities"] = current_activities
        self.users.append(current_user)

        print(self.users)

        """
        with open("users.json", "w") as f:
            dump(self.users, f)
        
        with open("trackpoints.json", "w") as f:
            dump(self.trackpoints, f)
        """


def main():
    p = Preprocessor()
    p.preprocess()


#main()
