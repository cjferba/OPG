from pymongo import MongoClient
import pandas as pd
import datetime


class DRepositoryAPI:
    __user = ""
    __password = ""
    __conn = 0

    def __init__(self, User, Password):
        self.__user = User
        self.__password = Password

    def connect(self):
        self.__conn = MongoDB("conn", host="150.214.203.106", port=27017, user=self.__user, pasw=self.__password)
        self.__conn.connect()
        return True

    def disconnect(self):
        self.__conn.close()
        return True

    def GetDataMining(self, Building=[], Dates=[]):
        return 0

    def GetEitMetadata(self, Building=[], no_id=True):
        self.connect()
        self.__conn.select_db(database="EiT_V2")
        self.__conn.select_collection(collect="Metadata")
        if Building != []:
            cursor = self.__conn.collection.find({"Build_Name": Building})
        else:
            cursor = self.__conn.collection.find({})
        # Expand the cursor and construct the DataFrame
        df = pd.DataFrame(list(cursor))
        """ Read from Mongo and Store into DataFrame """
        # Delete the _id
        if no_id:
            del df['_id']
        return df

    def GetEitData(self, Building, Selections, DateStart, DateEnd=datetime.datetime.today()):
        self.connect()
        self.__conn.select_db(database="EiT_V2")
        self.__conn.select_collection(collect="Metadata")
        MetaData = self.GetEitMetadata(Building=Building)
        return 0


class MongoDB:
    __name = ""
    __host = "150.214.203.106"
    Port = 27017
    __User = ""
    __Pass = ""
    Client = False
    db = ""
    collection = ""
    uri = 0

    def __init__(self, name, host="150.214.203.106", port=27017, user="", pasw=""):
        self.name = name
        self.__host = host
        self.Port = port
        self.__User = user
        self.__Pass = pasw
        self.uri = 'mongodb://' + self.__User + ':' + self.__Pass + '@' + self.__host + ':' + str(self.Port) + '/'

    def connect(self):
        self.Client = MongoClient(self.uri, self.Port)

    def select_db(self, database="EiT"):
        self.db = self.Client[database]

    def select_collection(self, collect="PlatformData"):
        self.collection = self.db[collect]

    def find_2(self, query):
        cur = self.collection.find({"data.Parameter.values.2": "SanomataloBMS"})

    def read_mongo(self, query={}, no_id=True):
        """ Read from Mongo and Store into DataFrame """
        cursor = self.collection.find(query)
        # Expand the cursor and construct the DataFrame
        df = pd.DataFrame(list(cursor))
        # Delete the _id
        if no_id:
            del df['_id']

        return df

    def select_db(self, database="EiT_V2"):
        self.db = self.Client[database]

    def select_collection(self, collect="Metadata"):
        self.collection = self.db[collect]


if __name__ == '__main__':
    print("Star")
    x = DRepositoryAPI("cjferba", "alfaomega")
    print(x.GetEitMetadata("ICPE"))
