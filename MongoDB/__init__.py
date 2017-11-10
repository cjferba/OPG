from pymongo import MongoClient
import pandas as pd

class MongoDB:
    name = ""
    host = ""
    Port = 27017
    User = ""
    Pass = ""
    DataBase = ""
    Client = False
    db = ""
    collection = ""

    def __init__(self, name, host="", port=27017, user="", pasw=""):
        self.name = name
        self.host = host
        self.Port = port
        self.User = user
        self.Pass = pasw

    def connect(self):
        self.Client = MongoClient(self.host, self.Port, self.User, self.Pass)

    def connect_uri(self, uri):
        self.Client = MongoClient(uri, self.Port)

    def select_db(self, database="EiT"):
        self.db = self.Client[database]

    def select_collection(self, collect="PlatformData"):
        self.collection = self.db[collect]


    def find_2(self, query):
        cur = self.collection.find({"data.Parameter.values.2": "SanomataloBMS"})

    def read_mongo(self,query={}, no_id=True):
        """ Read from Mongo and Store into DataFrame """
        cursor = self.collection.find(query)
        # Expand the cursor and construct the DataFrame
        df =  pd.DataFrame(list(cursor))

        # Delete the _id
        if no_id:
            del df['_id']

        return df
