import json
import pandas as pd
import datetime

class Scenario:
    '''Datos para el esceanrio'''
    Name = None
    Date = None
    Sample_period = None
    Channels = []
    SetPoints = []
    # Datos sobre los resultados de la simulacion
    ResultSetPoint = {}
    Result = pd.DataFrame()

    def __init__(self, Name, Channel, Date, Freq, SetPoints):
        self.Name = Name
        self.Date = Date
        self.Sample_period = Freq
        self.Channels = Channel
        self.SetPoints = SetPoints
    def getDate(self):
        return self.Date
    def getScenario(self):
        Dic = {}
        Dic2 = {}
        Dic["sample_period"] = self.Sample_period
        Dic["channels"] = self.Channels
        Dic[self.Date] = self.SetPoints
        Dic2[self.Name] = Dic
        return Dic2
    def getSetpoint(self):
        return self.SetPoints
    def setName(self, name):
        self.Name = name
        return name

    def setChannels(self,name, chanels):
        self.Channels[name] = chanels
        return chanels

    def setSetPoints(self, Channel, Setpoint):
        index = self.Channels.index(Channel)
        self.SetPoints[index] = Setpoint

    def WriteJsonScenario(self):
        json_data = json.dumps(self.getScenario())
        return json_data

    # def ScenarioJsonToFile(self,path,lista):
    #     with open('ICPE12012017_test1.json') as data_file:
    #         data = json.load(data_file)
    #     key1=list(data.keys())[0]
    #     keys2 = (sorted(data[key1].keys()))
    #     data[self.Name] = data.pop(key1)
    #     key1=self.Name
    #     data[key1][self.getDate()] = data[key1].pop(keys2[0])
    #     keys2 = (sorted(data[key1].keys()))
    #     data[key1]["sample_period"] = self.Sample_period
    #     data[key1]["channels"] = self.Channels
    #     j=0
    #     for i in self.SetPoints:
    #         data[key1][keys2[0]][j]=float(lista[j])
    #         j=j+1
    #     with open(path+self.Name+'.json', 'w') as out:
    #         json.dump((data), out,sort_keys = True, indent = 4,ensure_ascii = False)
    #     return 0

    def ScenarioJsonToFile2(self,path,name,lista):
        with open('ICPE12012017_test1.json') as data_file:
            data = json.load(data_file)
        key1=list(data.keys())[0]
        keys2 = (sorted(data[key1].keys()))
        data[self.Name] = data.pop(key1)
        key1=self.Name
        data[key1][self.getDate()] = data[key1].pop(keys2[0])
        keys2 = (sorted(data[key1].keys()))
        data[key1]["sample_period"] = self.Sample_period
        data[key1]["channels"] = self.Channels
        j=0
        for i in self.SetPoints:
            data[key1][keys2[0]][j]=float(lista[j])
            j=j+1
        with open(path+name+'.json', 'w') as out:
            json.dump((data), out,sort_keys = True, indent = 4,ensure_ascii = False)
        return 0

    def getName(self):
        return self.Name


class Config:
    Reporting = 10
    End_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    Start_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    Preconditioning = 10
    Apr_file = "_sim_T"
    Simulation_timestep = 6
    Scenarios = []

    def __init__(self, end_date, start_date, apr_file, scenarios):
        self.End_date = end_date.strftime('%Y-%m-%d')
        self.Start_date = start_date.strftime('%Y-%m-%d')
        self.Apr_file = apr_file
        self.Scenarios = scenarios

    def WriteJsonConfig(self):
        Data = {}
        Data['reporting_interval'] = self.Reporting
        Data['end_date'] = self.End_date
        Data['start_date'] = self.Start_date
        Data['preconditioning'] = self.Preconditioning
        Data['apr_file'] = self.Apr_file
        Data['simulation_timestep'] = self.Simulation_timestep
        self.self_scenarios = self.Scenarios
        Data['scenarios'] = self.self_scenarios
        json_data = json.dumps(Data)
        return Data

    def ConfigJsonToFile(self):
        with open('sim_config.json', 'w') as outfile:
            json.dump(self.WriteJsonConfig(), outfile)

