from pymongo import MongoClient
import pandas as pd
import datetime

class DRepositoryAPI:
    __user = ""
    __password = ""
    __conn=0
    def __init__(self,User, Password):
        self.__user=User
        self.__password=Password
    def connect(self):
        self.__conn=MongoDB("conn", host="crono.ugr.es", port=27017, user=self.__user, pasw=self.__password)
        return True
    def disconnect(self):
        self.__conn.close()
        return True
    def GetDataMining(self):
        return 0
    def GetEitMetadata(self, Building):
        self.connect()
        return 0
    def GetEitData(self, Building, Selections, DateStart, DateEnd=datetime.datetime.today()):
        self.connect()
        self.__conn.select_db()
        self.__conn.select_collection()
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

    def __init__(self, name, host="150.214.203.106", port=27017, user="", pasw=""):
        self.name = name
        self.__host = host
        self.Port = port
        self.__User = user
        self.__Pass = pasw
        self.Client = MongoClient(self.__host, self.Port, self.__User, self.__Pass)


    def select_db(self, database="EiT_V2"):
        self.db = self.Client[database]

    def select_collection(self, collect="Metadata"):
        self.collection = self.db[collect]


if __name__ == '__main__':
    print("Star")
    x= DRepositoryAPI("cjferba","alfaomega")
    x.GetEitData("","","")
