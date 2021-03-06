from numpy.core.shape_base import atleast_1d
import pandas as pd
import os
from datetime import datetime
from pickle import dump


"""
    Class for all preprocessing of data in assignment 2
"""


class Preprocessor:
    def __init__(self):
        self.users = []
        self.activities = []
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
                return label["mode"]
        return None


    """
        Main function that will read all the data from the dataset folder and dump the preprocessed data
        into three separate files for users, activities and trackpoints to be used in DbHandler.py
    """
    def preprocess(self):
        for root, dirs, files in os.walk("./dataset/Data"):
            for user in dirs:
                if user != "Trajectory":
                    self.users.append((str(user), self.user_has_labeled(user)))

            current_user = None
            # This will be used for finding the labels for activities if a user has labeled them
            user_label_file = None
            for file in files:
                if file.endswith(".plt"):
                    path = os.path.join(root, file)
                    user_id = path.split("./dataset/Data")[1][1:4]
                    # As some users have activities with the same id, this will ensure unique keys in the database
                    activity_id = file.replace(".plt", "") + user_id
                    opened = pd.read_csv(
                        path, names=["lat", "lon", "skip", "alt", "days", "date", "time"], skiprows=6)
                    
                    # Discard the activity if it is too large
                    if opened.size > 2500:
                        continue
                    start, end = self.extract_date_times(opened)
                    if self.user_has_labeled(user_id):
                        # If we are still on the same users activities, we have no need to read the labels.txt file
                        # again, as it will be the same. This snippet only changes this file when we are on a new user,
                        # hence having a different labels.txt file
                        if user_id != current_user:
                            current_user = user_id
                            print(current_user)
                            temp = pd.read_csv(
                                "./dataset/Data/%s/labels.txt" % (user_id), sep="\t", header=None, skiprows=1)
                            temp.columns = ["start", "end", "mode"]
                            user_label_file = temp
                        # Checks whether or not the activity is labeled by the user
                        mode = self.has_transportation_mode(
                            user_label_file, start, end)
                        self.activities.append(
                            (activity_id, user_id, mode, start, end))
                    else:
                        # If the user has not labeles any activity, it will be default None
                        self.activities.append(
                            (activity_id, user_id, None, start, end))

                    # Adding all the trackpoints for this activity to the list
                    for _, trackpoint in opened.iterrows():
                        self.trackpoints.append((activity_id, trackpoint["lat"], trackpoint["lon"],
                                                 trackpoint["alt"], trackpoint["days"], "{} {}".format(trackpoint["date"], trackpoint["time"])))

        print("Amount of users:", len(self.users))
        print("Amount of activities:", len(self.activities))
        print("Amount of trackpoints:", len(self.trackpoints))

        # Dumping the three lists in each their files using pickle
        print("Dumping users")
        with open('users.pickle', 'wb+') as file:
            dump(self.users, file)

        print("Dumping activities")
        with open('activities.pickle', 'wb+') as file:
            dump(self.activities, file)

        print("Dumping trackpoints")
        with open('trackpoints.pickle', 'wb+') as file:
            dump(self.trackpoints, file)


def main():
    p = Preprocessor()
    p.preprocess()


main()
