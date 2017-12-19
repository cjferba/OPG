from pymongo import MongoClient
import pandas as pd
import datetime
import pytz
import dateutil.parser
from pathlib import Path
import httplib2 as http
from os import walk
import shutil, os
import datetime

def SendToBlackBoard(Lista,pathJson,token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJVc2VyIjoiT1BHIiwiUGlsb3QiOiJGQVJPIiwiZXhwIjoxNTE5MTMxOTk2LCJpYXQiOjE0ODc1OTU5OTZ9.ZJfXJrebFV54VttkPKjdbIYplJzEjkF54aGJek2MukQ'):
    for i in Lista:
        pathLista = os.path.join(dir, pathJson + i)
        try:
            from urlparse import urlparse
        except ImportError:
            from urllib.parse import urlparse

        headers = {
            'Content-Type': 'application/json',
            'x-access-token': token
        }

        uri = 'http://citic-ps9.ugr.es:8099'
        path = '/project/EnergyInTime/OPG/FaroAirport/setpoints/store-plan'

        '''
        data = {}
        data['key'] = 'value'
        json_data = json.dumps(data)
        body = json.dumps(data);
        '''

        target = urlparse(uri + path)
        method = 'POST'
        import json
        from pprint import pprint

        with open(pathLista) as data_file:
            data = json.load(data_file)

        body = data
        h = http.Http()

        response, content = h.request(
            target.geturl(),
            method,
            json.dumps(body),
            headers)

        print(content)


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
        self.__conn.disconnect()
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

    def GetEitRawData(self, Building, Selections=[], DateStart=str((datetime.datetime.today()).isoformat()) + "Z",
                      DateEnd=str((datetime.datetime.today()).isoformat()) + "Z", Resample=False):
        if Resample == False:
            self.connect()
            self.__conn.select_db(database="EiT_V2")
            self.__conn.select_collection(collect="Metadata")
            MetaData = self.GetEitMetadata(Building=Building)
            if Selections == []:
                Sensors = list(MetaData["Sensor_ID"])
            else:
                Sensors = Selections
        else:
            Sensors = Selections

        """Date to Timestamp"""
        Start = Timestamp(dateutil.parser.parse(DateStart))
        End = Timestamp(dateutil.parser.parse(DateEnd))
        """Query"""
        self.__conn.select_collection(collect=Building)
        if len(Sensors)==1:
            cursor = self.__conn.collection.find(
                {"ID_Sensor": Sensors, "timestamp": {"$gte": Start, "$lte": End}})
        else:
            cursor = self.__conn.collection.find(
                {"ID_Sensor": {"$in": Sensors}, "timestamp": {"$gte": Start, "$lte": End}})
        df = pd.DataFrame(list(cursor))
        """ Read from Mongo and Store into DataFrame """
        # Delete the _id
        #     del df['_id']
        return df

    def GetEitData(self, Building, Selections=[], DateStart=str((datetime.datetime.today()).isoformat()) + "Z",
                   DateEnd=str((datetime.datetime.today()).isoformat()) + "Z", Resample='15T',Interpolate=False):

        data = pd.DataFrame(columns=["time"])
        data["time"] = pd.date_range(start=DateStart, end=DateEnd, freq=Resample)#[:-1]
        data["Building"] = pd.Series(len(data) * [Building], index=data.index)
        self.connect()
        self.__conn.select_db(database="EiT_V2")
        self.__conn.select_collection(collect="Metadata")
        MetaData = self.GetEitMetadata(Building=Building)
        if Selections == []:
            Sensors = list(MetaData["Sensor_ID"])
        else:
            Sensors = Selections
        count=0
        for i in Sensors:
            print(str(count)+" de "+ str(len(Sensors)))
            x = self.GetEitRawData(Building=Building, Selections=[i], DateStart=DateStart, DateEnd=DateEnd,
                                   Resample=True)
            count = count+1
            if len(x) != 0:
                x = x.loc[:, ["value", "date"]]
                from dateutil import parser
                dt = parser.parse("Aug 28 1999 12:00AM")
                df2 = pd.DataFrame(
                    [[x.loc[len(x) - 1, "value"],
                      parser.parse(str(data.loc[len(data) - 1, 'time']).split("+")[0])],#- datetime.timedelta(minutes=15)
                     [x.loc[0, "value"], parser.parse((str(data.loc[0, 'time'])).split("+")[0])]],
                    columns=['value', 'date'])
                x = x.append(df2,ignore_index=True)

                x=x.resample(Resample, on='date').mean()
                if Interpolate==True:
                    x = x.interpolate(method='cubic', downcast='infer')
                data[i] = x.loc[:, ["value"]].values
        self.disconnect()
        return data

    def InsertoOP(self,plan,Building):
        self.connect()
        self.__conn.select_db(database="OPG")
        self.__conn.select_collection(collect="OPG" + str(Building))
        result = self.__conn.collection.insert_one(plan)

        return result.inserted_id

    def GetOP(self,Date,Building):
        self.connect()
        self.__conn.select_db(database="OPG")
        self.__conn.select_collection(collect="OPG"+str(Building))
        cursor = self.__conn.collection.find(
            {"ID_Sensor": Sensors, "timestamp": {"$gte": Start, "$lte": End}})

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
    def disconnect(self):
        self.Client.close()

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


def Timestamp(date):
    # x=date.strftime('%s')
    # date = datetime.datetime(int(year), int(moth), int(day), int(hour), int(minu), int(seclist[0]), int(0), pytz.UTC)
    return (date - datetime.datetime(1970, 1, 1, 0, 0, 0, 0, pytz.UTC)).total_seconds()
def Date(t):
    return datetime.datetime.fromtimestamp(t)

if __name__ == '__main__':
    print("Star")
    x = DRepositoryAPI("cjferba", "alfaomega")

    DateStart = "2017-08-16T00:00:00.000000Z"
    DateEnd = "2017-08-17T00:00:00.000000Z"
    s = (x.GetEitData(Building="FaroBMS", DateStart=DateStart, DateEnd=DateEnd))#,Selections=[9003]))
    s.to_csv("DataRepository.csv")
    print(s)


