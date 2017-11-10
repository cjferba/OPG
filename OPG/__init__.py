import datetime
import glob
import json
import datetime as dt
import os
import ssl
import sys
import time
import pymongo
import numpy as np
import zipfile
from os import listdir
from shutil import copyfile
import pandas as pd
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh.io import save
import shutil


import OPG.OPG_Structures.Scenario as Scenario
import OPG.OPG_Structures.scan_api as scan_api
import OPG.OPG_Structures.Config as Config

class OPG:


    """Esta clase se utiliza para la generacion de un plan operacional optimo para Faro

        - **parameters**, **types**, **return** and **return types**::

              :param Current: parallel executions
              :param arg2: description
              :type arg1: type description
              :type arg1: type description
              :return: return description
              :rtype: the return type description

        - and to provide sections such as **Example** using the double commas syntax::

              :Example:

              followed by a blank line !

          which appears as follow:

          :Example:

          followed by a blank line

        - Finally special sections such as **See Also**, **Warnings**, **Notes**
          use the sphinx syntax (*paragraph directives*)::

              .. seealso:: blabla
              .. warnings also:: blabla
              .. note:: blabla
              .. todo:: blabla

        .. note::
            There are many other Info fields but they may be redundant:
                * param, parameter, arg, argument, key, keyword: Description of a
                  parameter.
                * type: Type of a parameter.
                * raises, raise, except, exception: That (and when) a specific
                  exception is raised.
                * var, ivar, cvar: Description of a variable.
                * returns, return: Description of the return value.
                * rtype: Return type.

        .. note::
            There are many other directives such as versionadded, versionchanged,
            rubric, centered, ... See the sphinx documentation for more details.

        Here below is the results of the :func:`function1` docstring.

        """

    Current = 25
    DryBulbTem = None
    Building = 'FARO'  ## Pilot ##
    ##  Day ##
    StarDate = (datetime.date.today() + datetime.timedelta(days=1))
    EndDate = (datetime.date.today() + datetime.timedelta(days=1))
    Day = StarDate.weekday()
    ##  Channel ##
    Channels = []
    # Ocupacion
    OcupacionChannels = []
    OcuppacionRooms = []
    # Tiempo(prevision)
    WeatherChannel = []
    WeatherSetpoint = []
    ##  Scenaries names ##
    ScenariesNames = []
    ScenariosList = []
    Limit = {'SC002238': {'Min': 0, 'Max': 1}, 'SC002271': {'Min': 0, 'Max': 1},
             'SC002310': {'Min': 0, 'Max': 1}}  ## Values MAx-Min ##"Tsupply AHU":{'Min': 40, 'Max': 60}
    ValuesOfSensor = {'SC002238': [0, 1], 'SC002271': [0, 1], 'SC002310': [0, 1]}
    ActiveTime = []
    Occupancy = []
    Sample_period = 15
    Configuration = []
    Best = 1
    # Flag
    UseExternalWeather = False
    UseExternalOccupacy = True
    dir=0

    ## path##
    path = ""
    pathScenarios = ""
    pathPlot = ""
    pathIterations = ""

    ListDataExport = [
        # comford
        "SC002420", "SC002421", "SC000250", "SC000115", "SC000121", "SC000202",
        # comford MALO
        "SC000167", "SC000170", "SC000173", "SC000244", "SC000247", "SC000106", "SC000006", "SC000109", "SC000112",
        "SC000118", "SC000199", "SC000205",
        # Setpoint
        "SC002227", "SC002236", "SC002249", "SC002271", "SC002238", "SC002310", "SC002321",
        "SC002282", "SC002332", "SC002354", "SC002365", "SC002376", "SC002299", "SC002343", "SC002260",
        # HeatMeter
        "SC002460",
        "SC002474",
        # tiempo
        "SCAN0004",
        # OCupacion
        "SC002477", "SC002478", "SC002479", "SC002480", "SC002481", "SC002482"]

    def __init__(self, Current=45, Building='FARO', OcupacionChannels=[], OcuppacionRooms=[],
                 WeatherChannel=[], WeatherSetpoint=[],
                 StarDate=(datetime.date.today() + datetime.timedelta(days=1)),
                 EndDate=(datetime.date.today() + datetime.timedelta(days=1)),
                 channels=[], limit={}, ValSensor={},
                 Sample_period=15, Directory="."):
        #os.chdir(Directory)
        self.dir = os.path.dirname(Directory)
        self.Current = Current
        self.Building = Building  ## Pilot ##
        ##  Day ##
        self.StarDate = StarDate
        self.EndDate = EndDate
        self.Day = StarDate.weekday()
        ##  Channel ##
        self.Channels = channels
        ##  Scenaries names ##
        self.Limit = limit  ## Values Max-Min ##
        self.ValuesOfSensor = ValSensor
        self.Sample_period = Sample_period
        self.GenerateOccupancy()
        self.OcupacionChannels = OcupacionChannels
        self.OcuppacionRooms = OcuppacionRooms
        self.WeatherChannel = WeatherChannel
        print("current" + str(self.Current))
        self.ScenariesNames = []
        for i in range(0, self.Current):
            name = self.Building + "_" + self.StarDate.strftime('%Y%m%d') + "_" + str(i)
            self.ScenariesNames.append(name)
        print("Scenarios post current" + str(self.ScenariesNames))
        for i in range(0, self.Current):
            a = Scenario.Scenario(Name=self.ScenariesNames[i],
                                  Date=self.StarDate.strftime('%Y-%m-%d'),
                                  Channel=self.Channels + self.OcupacionChannels,
                                  Freq=self.Sample_period,
                                  SetPoints={})
            self.ScenariosList.append(a)

        '''Salida de los resultados'''
        print(Directory)
        print(self.dir)
        xx
        output = os.path.join(self.dir, 'OutPut/')
        if not os.path.exists(output + self.StarDate.strftime('%Y-%m-%d')):
            print(output)
            os.makedirs(output + self.StarDate.strftime('%Y-%m-%d'))
        self.path = output + self.StarDate.strftime('%Y-%m-%d') + "/"
        self.pathScenarios = os.path.join(self.dir, 'Scenarios/')
        filelist = glob.glob(self.pathScenarios + "*.json")
        for f in filelist:
            os.remove(f)

        if not os.path.exists(output + self.StarDate.strftime('%Y-%m-%d') + "/Plots"):
            os.makedirs(output + self.StarDate.strftime('%Y-%m-%d') + "/Plots")
        self.pathPlot = output + self.StarDate.strftime('%Y-%m-%d') + "/Plots" + "/"

        if not os.path.exists(output + self.StarDate.strftime('%Y-%m-%d') + "/Iterations"):
            os.makedirs(output + self.StarDate.strftime('%Y-%m-%d') + "/Iterations")
        self.pathIterations = output + self.StarDate.strftime('%Y-%m-%d') + "/Iterations" + "/"

        print("Generating Config file")
        self.Configuration = Config.Config(end_date=self.StarDate, start_date=self.EndDate,
                                           apr_file=Building + "_sim_T",
                                           scenarios=self.ScenariesNames)
        self.Configuration.ConfigJsonToFile()

    def GenerateOccupancy(self, period=4):
        print("Generating occupancy")
        self.Occupancy = [0] * 28
        if self.Day == 4:
            self.Occupancy = self.Occupancy + ([1] * 23)  # 34
        elif self.Day == 5 or self.Day == 6:
            self.Occupancy = self.Occupancy + ([0] * 23)
        else:
            self.Occupancy = self.Occupancy + ([1] * 34)
        self.Occupancy = self.Occupancy + ([0] * (96 - len(self.Occupancy)))  # 0

        self.ActiveTime = sorted(np.where(np.array(self.Occupancy) == 1)[0])
        if len(self.ActiveTime) == 0:
            print("finde de semana")
        elif self.ActiveTime[0] % period != 0:
            aux = self.ActiveTime[0] % period
            aux1 = list(range(self.ActiveTime[0] - aux, self.ActiveTime[0], 1))
            self.ActiveTime = aux1 + self.ActiveTime

    def Generate_Scenarios(self,wheather=False):
        print("Generating Config occupancy")
        YChanels = {}
        for sensor in self.Channels:
            y = []
            for i in range(0, len(self.Occupancy)):
                if self.Occupancy[i] == 0:
                    y.append(self.Limit[sensor]["Min"])
                if self.Occupancy[i] == 1:
                    y.append(self.Limit[sensor]["Min"])
            YChanels[sensor] = (y.copy())
        if wheather==False:
            for i in range(0, len(self.ScenariosList)):
                self.ScenariosList[i].setAllSetPoints(YChanels.copy())
                self.ScenariosList[i].ScenarioJsonToFile(path=self.pathScenarios,weather=False)

    def Generate_AutoOP(self, ListDIC, Ocupacion):
        if len(ListDIC) == (self.Current):
            tam = len(ListDIC)
            YChanels = {}
            for i in range(0, tam):
                y = []
                dic = {}
                dic.update(ListDIC[i].copy())
                dic.update(Ocupacion.copy())
                self.ScenariosList[i].setAllSetPoints(dic)
                self.ScenariosList[i].ScenarioJsonToFile(path=self.pathScenarios, weather=False)
        else:
            print("Error 13")
            exit()

    def Generate_Weather(self):
        Faro = "{\"FARO\": {        \"sample_period\": 15,        \"channels\": []    }}"
        ConfigureB = Config.Config(end_date=self.StarDate, start_date=self.StarDate,
                                   apr_file=self.Building + "_sim_T", scenarios=self.ScenariesNames)
        self.ScenariosList[0].ScenarioJsonToFile(path=self.pathScenarios,weather=True)
        name = self.RunSimulation("Weather", 1)
        Weather = pd.read_csv( self.Empty + self.nameEmpty)["SCAN0004"]
        self.DryBulbTem = list(Weather)
        return Weather

    def Generate_Tsupply(self):
        print(self.DryBulbTem)

    def Generate_Report(self):
        self.pathIterations

    def GetCurrent(self):
        return self.Curren

    def SetCurrent(self, c):
        self.Current = c
        for i in range(0, self.Current):
            name = self.Building + "_" + self.StarDate.strftime('%Y%m%d') + "_" + str(i)
            self.ScenariesNames.append(name)

        for i in range(0, self.Current):
            a = Scenario.Scenario(Name=self.ScenariesNames[i],
                                  Date=self.Date.strftime('%Y-%m-%d'),
                                  Channel=self.Channels,
                                  Freq=self.Sample_period,
                                  SetPoints=[])
            self.ScenariosList.append(a)

    def GetBuilding(self):
        return self.Building

    def GetDate(self):
        return self.StarDate

    def GetChannels(self):
        return self.Channels

    def GetLimit(self):
        return self.Limit

    def GetValuesOfSensor(self):
        return self.ValuesOfSensor

    def GetSample_period(self):
        return self.Sample_period

    def GetActiveTime(self):
        return self.ActiveTime

    def GetOccupancy(self):
        return self.Occupancy

    def GetScenarios(self):
        for i in range(len(self.ScenariosList)):
            print(self.ScenariosList[i].GetScenario())

    def PlotScenarios(self):
        filenames = glob.glob(self.path + "/*.json")
        dfsSimulation = []
        namesSimulation = []
        for filename in filenames:
            dfsSimulation = []
            namesSimulation = []
            # print(filename)
            namesSimulation.append(str(filename.split('/')[-1]))
            with open(filename) as data_file:
                dfsSimulation.append(json.load(data_file))
            for i in range(0, len(dfsSimulation)):
                dfsSimulation[i] = dfsSimulation[i][list(dfsSimulation[i].keys())[0]]
                # .fillna()
                # for i in range(0, len(dfsSimulation)):
                k = sorted(list(dfsSimulation[i].keys()))
                base = pd.to_datetime(k[0], format='%Y-%m-%d', errors='raise',
                                      infer_datetime_format=False, exact=True)

                freq = dfsSimulation[i]['sample_period']
                date_list = [base + datetime.timedelta(minutes=x) for x in range(0, 1440, freq)]
                dfsSimulation[i] = pd.DataFrame({'Timestamp': date_list,
                                                 'SimulationSetPoints': dfsSimulation[i][k[0]]})
            ListSetpoint = []
            for i in range(0, len(dfsSimulation)):
                SetPoint = figure(x_axis_type="datetime", title=str(namesSimulation[i]) + "Setpoint SC000405",
                                  width=1300, height=500)
                SetPoint.grid.grid_line_alpha = 0.3
                SetPoint.xaxis.axis_label = 'Date'
                SetPoint.yaxis.axis_label = 'Value'
                SetPoint.legend.location = "top_left"
                setpointValue = dfsSimulation[0]['SimulationSetPoints']

                SetPoint.line(dfsSimulation[0]['Timestamp'], dfsSimulation[0]['SimulationSetPoints'],
                              legend='Setpoint Interpolated')  # ,fill_color="green",  size=3)
                SetPoint.circle(dfsSimulation[0]['Timestamp'], dfsSimulation[0]['SimulationSetPoints'],
                                legend='Setpoint sending', fill_color="red", size=5)

                ListSetpoint.append(SetPoint)

            grid = gridplot([ListSetpoint])
            # print(pathPlot + '/setpoint' + str(iteration) + str(filename.split('/')[-1]) + str(date) + '.html')
            # save(grid, pathPlot + '/setpoint' + str(iteration) + str(filename.split('/')[-1]) + str(date) + '.html')

    def StoreDB(self):
        return 1

    def readDataResultPreheating(self, names, Phase, Iteration):
        i = 0
        ComplexDF = pd.DataFrame()
        for file in names:

            df = pd.read_csv(self.pathIterations + str(Phase) + "_" + str(Iteration) + "_" + str(file))
            # list=ListaExport.append('Timestamp')
            df = df.ix[:, ["Timestamp",
                           # comfort
                           "SC002420", "SC002421", "SC000006", "SC000115", "SC000121", "SC000202",
                           # Setpoint
                           "SC002227", "SC002236", "SC002249", "SC002271", "SC002238", "SC002310", "SC002321",
                           "SC002282", "SC002332", "SC002354", "SC002365", "SC002376", "SC002299", "SC002343",
                           "SC002260",
                           # HeatMeter
                           "SC002474",
                           # tiempo
                           "SCAN0004",
                           # OCupacion
                           "SC002477", "SC002478", "SC002479", "SC002480", "SC002481", "SC002482"]]

            # print(df)
            # df = df.fillna(0)
            StarDay = pd.to_datetime(df['Timestamp'],
                                     format='%Y-%m-%d', errors='raise', infer_datetime_format=False, exact=True)[12]
            date_list = [StarDay + datetime.timedelta(minutes=x) for x in range(0, 1440, 15)]  # 0, 1440, 10
            df['Timestamp'] = date_list
            self.ScenariosList[i].Result['Timestamp'] = date_list.copy()
            self.ScenariosList[i].Result['ComfordA51'] = pd.DataFrame(df[['SC002420']])
            self.ScenariosList[i].Result['ComfordA52'] = pd.DataFrame(df[['SC002421']])
            self.ScenariosList[i].Result['ComfordA53'] = pd.DataFrame(df[['SC000006']])
            self.ScenariosList[i].Result['ComfordA54'] = pd.DataFrame(df[['SC000115']])
            self.ScenariosList[i].Result['ComfordA55'] = pd.DataFrame(df[['SC000121']])
            self.ScenariosList[i].Result['ComfordA56'] = pd.DataFrame(df[['SC000202']])

            self.ScenariosList[i].Result['Boiler'] = pd.DataFrame(df[["SC002474"]]).copy()
            if i == 0:
                Best = 0
                # aux = df['Timestamp']
                # ComplexDF.append(aux.copy())
                ComplexDF['Timestamp'] = pd.Series(date_list)
                ComplexDF['ComfordA51' + str(i)] = pd.DataFrame(df[['SC002420']])
                ComplexDF['ComfordA52' + str(i)] = pd.DataFrame(df[['SC002421']])
                ComplexDF['ComfordA53' + str(i)] = pd.DataFrame(df[['SC000006']])
                ComplexDF['ComfordA54' + str(i)] = pd.DataFrame(df[['SC000115']])
                ComplexDF['ComfordA55' + str(i)] = pd.DataFrame(df[['SC000121']])
                ComplexDF['ComfordA56' + str(i)] = pd.DataFrame(df[['SC000202']])

                ComplexDF['Boiler' + str(i)] = pd.Series(df[["SC002474"]])

                ComplexDF['Setpoint_SC002227' + str(i)] = pd.DataFrame(df[['SC002227']])
                ComplexDF['Setpoint_SC002236' + str(i)] = pd.DataFrame(df[['SC002236']])
                ComplexDF['Setpoint_SC002249' + str(i)] = pd.DataFrame(df[['SC002249']])
                ComplexDF['Setpoint_SC002271' + str(i)] = pd.DataFrame(df[['SC002271']])
                ComplexDF['Setpoint_SC002238' + str(i)] = pd.DataFrame(df[['SC002238']])
                ComplexDF['Setpoint_SC002310' + str(i)] = pd.DataFrame(df[['SC002310']])
            elif i != 0:
                ComplexDF['ComfordA51' + str(i)] = pd.DataFrame(df[['SC002420']])
                ComplexDF['ComfordA52' + str(i)] = pd.DataFrame(df[['SC002421']])
                ComplexDF['ComfordA53' + str(i)] = pd.DataFrame(df[['SC000006']])
                ComplexDF['ComfordA54' + str(i)] = pd.DataFrame(df[['SC000115']])
                ComplexDF['ComfordA55' + str(i)] = pd.DataFrame(df[['SC000121']])
                ComplexDF['ComfordA56' + str(i)] = pd.DataFrame(df[['SC000202']])

                ComplexDF['Boiler' + str(i)] = pd.Series(df[['SC002474']])

                ComplexDF['Setpoint_SC002227' + str(i)] = pd.DataFrame(df[['SC002227']])
                ComplexDF['Setpoint_SC002236' + str(i)] = pd.DataFrame(df[['SC002236']])
                ComplexDF['Setpoint_SC002249' + str(i)] = pd.DataFrame(df[['SC002249']])
                ComplexDF['Setpoint_SC002271' + str(i)] = pd.DataFrame(df[['SC002271']])
                ComplexDF['Setpoint_SC002238' + str(i)] = pd.DataFrame(df[['SC002238']])
                ComplexDF['Setpoint_SC002310' + str(i)] = pd.DataFrame(df[['SC002310']])
            i = i + 1
            ComplexDF.to_csv(self.pathIterations + "All_" + str(Phase) + "_" + str(Iteration) + "_" + "Completo.csv",
                             sep=',')

    def RunSimulation(self, Phase, Iteration, ExportChannels=[]):
        if ExportChannels==[]:
            ExportChannels=self.ListDataExport
        if (Phase == "Weather"):
            ExportChannels = self.ListDataExport

        ######################################  Part 1  ######################################
        ssl._create_default_https_context = ssl._create_unverified_context  # hack to bypass SSL certificate validation

        # # Functions
        # These functions are called into the script and must be run before the script at the end.
        # select_directory is used to locate the json files that have the scenario data in them.
        # optional arguments to pass in are "path_to_directory" and "extension". recommended having
        # a folder called "Scenarios" and using the extension "json"

        def select_directory(path_to_directory=None, extension=None):
            if path_to_directory == None and extension == None:
                return os.listdir(path_to_directory)

            elif path_to_directory != None:
                full_list = ['{0}/{1}'.format(path_to_directory, a) for a in
                             os.listdir('{0}/'.format(path_to_directory))]
            else:
                full_list = os.listdir(path_to_directory)

            if extension == None:
                return full_list
            else:
                return [f for f in full_list if f.endswith('.{0}'.format(extension)) == True]

        # json_scenario_to_scan does the workflow and gets the json information to post to SCAN. Arguments required are
        #  building (scan building) and json (the file that has the scenario info). "create_scenario" is an optional
        #  argument defaulted to "False". setting this to true will create a scenario if it cannot be located by either
        #  it's DisplayName or ItemName (id) attributes.
        # This function gives some feedback as to the stage of the process and the current scenario being worked on.
        # takes a json file and runs it through to create a scenario and set the scenario.

        def json_scenario_to_scan(building=None, json=None, create_scenario=False):
            # gets the list of scenarios on SCAN
            scenario_list = building.get('scenario-list').Scenarios

            # parse json file
            for scenario in json.keys():
                print('Starting scenario : "{}"'.format(scenario))
                # check if the current scenario already exists on SCAN.
                scenario_check, scenario_id = check_scenario(building, scenario, scenario_list, create_scenario)
                if scenario_check == True:
                    sample_period = json[scenario]['sample_period']
                    channels = json[scenario]['channels']
                    del (json[scenario]['sample_period'], json[scenario]['channels'])
                    # 2016-09-06 added sorting to keys to handle crossing month boundaries.
                    dates = list(sorted(json[scenario].keys()))

                    channel_ids = get_channel_ids(building, channels, False)

                    values = []
                    offsets = []
                    last_month = None

                    for idx, day in enumerate(dates):
                        current_day = dt.datetime.strptime(day, '%Y-%m-%d')
                        start_position = (current_day.day - 1) * 1440
                        json_values = json[scenario][day]
                        # json_values = list((None) for x in range(0,1440))
                        day_offsets = list(
                            (x * sample_period) + start_position for x in range(0, 1440 // sample_period))
                        if last_month == None:
                            last_month = current_day.month

                        if current_day.month == last_month and idx != len(dates) - 1:
                            values.extend(json_values)
                            offsets.extend(day_offsets)
                            last_month = current_day.month
                        else:
                            # 2016-09-06 added a couple of lines to handle last date in the list.
                            # month for uploading data is now set as data_month
                            data_month = current_day.month - 1

                            if idx == len(dates) - 1:
                                values.extend(json_values)
                                offsets.extend(day_offsets)
                                data_month = current_day.month

                            for channel in channel_ids:
                                building.post('data-update-channel', channel=channel, scenario=scenario_id,
                                              year=current_day.year,
                                              month=data_month, data={'Values': values, 'Offsets': offsets})
                            values = json_values
                            offsets = day_offsets
                            last_month = current_day.month

                    print('Scenario "{}" updated.\n'.format(scenario))
                else:
                    pass

        # check_scenario is called by json_scenario_to_scan. it checks if the scenario exists by ItemName or DisplayName,
        #  if it doesnt exist it can create it if the argument is set in json_scenario_to_scan

        def check_scenario(building, scenario_name, scenario_list, create_scenario=True):

            try:
                current_scenario = next((x for x in scenario_list if x.ItemName == scenario_name))
                print('Scenario "{}" will be updated'.format(current_scenario.DisplayName))
                return True, current_scenario.ItemName
            except:
                try:
                    current_scenario = next((x for x in scenario_list if x.DisplayName == scenario_name))
                    print('Scenario "{}" will be updated'.format(current_scenario.DisplayName))
                    return True, current_scenario.ItemName
                except:
                    if create_scenario == True:
                        # if the scenario doesnt exist, create a new one and set it to be the current scenario to post updates to.
                        current_scenario = building.post('scenario-create', {'name': scenario_name})
                        print('New Scenario "{}" created'.format(current_scenario.DisplayName))
                        return True, current_scenario.ItemName

                    else:
                        print(
                            'Scenario "{}" does not exist and was not created. Use "create_scenario= True" argument.\n'.format(
                                scenario_name))
                        return False, scenario_name

        # get_channel_ids is called by json_scenario_to_scan. it gets the list of channels that have been provided from
        #  the json file and returns the ItemName of the channel when it finds a match. It will always return for the first
        # match it finds so if there are duplicate names the user will need to consider this.
        # there's an optional "output_details" argument which if set to True, will output more information about the
        #  channel that is selected. If a channel cannot be found the function will report this and move to the next channel.

        def get_channel_ids(building, channels, output_details=True):

            # 2016-09-06 "DisplayName" has been changed to "ExportReference" to ensure consistency with mappings

            channel_list = building.get('channel-list').Channels
            channel_ids = []
            for chan in channels:
                try:
                    channel = next((x for x in channel_list if x.ItemName == chan))
                    channel_ids.append(channel.ItemName)
                except:
                    try:
                        channel = next((x for x in channel_list if x.ExportReference == chan))
                        channel_ids.append(channel.ItemName)
                        if output_details == True:
                            print('ItemName="{}", ExportReference="{}", Level="{}", OwnerReference="{}"'.format(
                                channel.ItemName,
                                channel.ExportReference,
                                channel.Level,
                                channel.OwnerReference))
                    except:
                        print('Channel "{}" not found by ExportReference match or ItemName match'.format(chan))

            return channel_ids

        # after the functions above have been run, this will get the list of files and run through each of them sending
        #  the data to SCAN. and output from the script will be printed


        root, building, server = scan_api.open_token()
        files_list = select_directory(path_to_directory='Scenarios', extension='json')

        print('Selecting FARO AIRPORT - PORTUGAL')

        # find the API URLs for the building with the display name 'Unit Test Building'.
        building = next(b for b in root.Buildings if b.DisplayName == "FARO AIRPORT - PORTUGAL")

        for scenario in files_list:
            with open(scenario) as json_scenario:
                scenario_details = json.load(json_scenario)
            json_scenario.close()
            json_scenario_to_scan(building, json=scenario_details, create_scenario=True)

        print('Complete part 1')
        print('Start Part 2')
        ######################################  Part 2  ######################################
        # # Run simulation using settings in configuration file
        # Simple script ot send simulation jobs based on the settings in a simulation configuration file

        ssl._create_default_https_context = ssl._create_unverified_context  # hack to bypass SSL certificate validation

        def scan_connect():
            root, building, server = scan_api.open_token()
            print('Selecting FARO AIRPORT - PORTUGAL')

            # find the API URLs for the building with the display name 'Unit Test Building'.
            building = next(b for b in root.Buildings if b.DisplayName == "FARO AIRPORT - PORTUGAL")
            return building

        def scenario_itemnames(building, scenario_list, error='stop'):
            scan_scenarios = building.get('scenario-list').Scenarios
            scenarios = []
            for item in scenario_list:
                try:
                    current_scenario = next((x.ItemName for x in scan_scenarios if x.DisplayName == item))
                    scenarios.append(current_scenario)
                except:
                    try:
                        current_scenario = next((x.ItemName for x in scan_scenarios if x.ItemName == item))
                        scenarios.append(current_scenario)
                    except:
                        if error == 'stop':
                            print('Cannot find scenario "{}". Exiting script. Simulations have not been run.'.format(
                                item))
                            sys.exit()
                        else:
                            print('Scenario not found, excluded from simulation: "{0}"'.format(item))
                            pass

            if len(scenarios) == 0:
                print('No Scenarios to run. Cancelling simulation.')
                sys.exit()
            else:
                return scenarios

        def configure_simulation(config_json='sim_config.json', error='stop'):
            with open(config_json) as config_json:
                config = json.load(config_json)
                start_date = config.get('start_date')
                end_date = config.get('end_date')
                preconditioning = config.get('preconditioning')
                timestep = config.get('simulation_timestep')
                report_interval = config.get('reporting_interval')
                apr_file = config.get('apr_file')
                scenarios_list = config.get('scenarios')

                simulation_settings = {
                    'DisplayName': '{0}_{1}_{2}'.format(apr_file, start_date, end_date),
                    'ScenariosToRun': scenario_itemnames(building, scenarios_list, error=error),
                    'StartDate': start_date,
                    'EndDate': end_date,
                    'NumberOfPreconditioningDays': preconditioning,
                    'SimulationTimestep': timestep,
                    'ReportingTimestep': report_interval

                }

            config_json.close()
            return simulation_settings

        def send_to_scan(return_status=True):
            sim_settings = configure_simulation(error=None)
            simulation_run = building.post('simulationrun-create', sim_settings)
            print('"{}" has been sent to SCAN.'.format(sim_settings['DisplayName']))
            print('{0} Scenarios to run. Start date = {1}, End date = {2}, {3} days preconditioning'.format(
                len(sim_settings['ScenariosToRun']),
                sim_settings['StartDate'],
                sim_settings['EndDate'],
                sim_settings['NumberOfPreconditioningDays']))
            print('\n\n')
            if return_status == True:
                tick = 0

                last_status = ''
                last_percent = -1

                while simulation_run.Status != 'Finished':
                    time.sleep(15)
                    simulation_run.refresh()
                    if simulation_run.Status != last_status or simulation_run.PercentComplete != last_percent:
                        if simulation_run.Status != 'Failed':
                            last_status = simulation_run.Status
                            last_percent = simulation_run.PercentComplete
                            print(
                                '  status {0}\t{1}%\t{2}'.format(simulation_run.Status, simulation_run.PercentComplete,
                                                                 dt.datetime.now().isoformat()))
                        else:
                            print('Simulation failed to complete. Exiting script.')
                            sys.exit()
                    tick += 1
            else:
                print('Simulation has been sent to SCAN. No status will be returned')

        building = scan_connect()
        send_to_scan()

        ######################################  Part 3  ######################################
        print('Complete par 2')
        print('Start Part 3')

        pathRemove =os.path.join(self.dir, 'Exports/')
        filelist = glob.glob(pathRemove + "*.zip")
        for f in filelist:
            os.remove(f)

        ssl._create_default_https_context = ssl._create_unverified_context  # hack to bypass SSL certificate validation

        # # Functions
        # These functions are called into the script and must be run before the script at the end.
        # select_directory is used to locate the json files that have the scenario data in them.
        # optional arguments to pass in are "path_to_directory" and "extension". recommended having a folder called "Scenarios" and using the extension "json"


        def export_csv_for_channel(building, start_date, end_date, scenarios_list, channels, output_details=False):

            channels_to_export, channel_list = get_channel_ids(building, channels, output_details=False)

            scenarios = scenario_ids(building, scenarios_list)
            existing_channel_states = list(item for item in channel_list if item.ExportToCsv == True)
            print('Updating exported channels.')
            for item in existing_channel_states:
                channel = next(channel for channel in channel_list if channel.ItemName == item.ItemName)
                channel.ExportToCsv = False
                channel.update()

            for item in channels_to_export:
                channel = next(channel for channel in channel_list if channel.ItemName == item)
                channel.ExportToCsv = True
                channel.update()
            print('Channels to be exported set')

            for scenario in scenarios:
                print('Exporting Scenario :{}'.format(scenario))

                export = building.post('dataexport-create',
                                       {'EndDate': end_date, 'ExportToCsv': "true", 'ExportToCsvIsoDate': "true",
                                        'ExportedChannels': '', 'FileDescription': "file description",
                                        'Scenario': scenario,
                                        'SourceDescription': "source description", 'StartDate': start_date})

                print('Downloading {}_{}_{}.zip'.format(start_date, end_date, scenario))
                p = os.path.join(self.dir, 'Exports/')
                with open(os.path.join(p, '{}_{}_{}.zip'.format(start_date, end_date, scenario)), 'wb') as out_file:
                    out_file.write(export.get_raw('download').read())
                out_file.close()
                # ERROR de DEscarga
                export.post('remove', {})
            print('Resetting original channels to export')
            for item in channels_to_export:
                channel = next(channel for channel in channel_list if channel.ItemName == item)
                channel.ExportToCsv = False
                channel.update()

            for item in existing_channel_states:
                item.ExportToCsv = True
                item.update()

            print('Export complete')

        # simulation_parameters gets the start and end dates and list of scenarios that were run for the simulation. these are taken from config.json

        def simulation_parameters(config_json='sim_config.json', error='stop'):
            with open(config_json) as config_json:
                config = json.load(config_json)
                start_date = config.get('start_date')
                end_date = config.get('end_date')
                scenarios_list = config.get('scenarios')
            config_json.close()
            return start_date, end_date, scenarios_list

        # scenario_ids gets the scenario ItemNames to pass into the export options and confirms that the specified scenarios exist.

        def scenario_ids(building, scenarios):
            scenario_list = building.get('scenario-list').Scenarios
            scenario_ids = []

            for scenario in scenarios:
                try:
                    current_scenario = next((x for x in scenario_list if x.ItemName == scenario))
                    scenario_ids.append(current_scenario.ItemName)
                except:
                    try:
                        current_scenario = next((x for x in scenario_list if x.DisplayName == scenario))
                        scenario_ids.append(current_scenario.ItemName)

                    except:
                        print('Scenario "{}" does not exist.'.format(scenario))
            return scenario_ids

        # get_channel_ids is called by json_scenario_to_scan. it gets the list
        # of channels that have been provided from the json file and returns the
        # ItemName of the channel when it finds a match. It will always return for
        #  the first match it finds so if there are duplicate names the user will need to consider this.
        # there's an optional "output_details" argument which if set to True, will output more information
        #  about the channel that is selected. If a channel cannot be found the function will report this
        # and move to the next channel.


        def get_channel_ids(building, channels, output_details=True):
            channel_list = building.get('channel-list').Channels
            channel_ids = []
            for chan in channels:
                try:
                    channel = next((x for x in channel_list if x.ItemName == chan))
                    channel_ids.append(channel.ItemName)
                except:
                    try:
                        channel = next((x for x in channel_list if x.DisplayName == chan))
                        channel_ids.append(channel.ItemName)
                        if output_details == True:
                            print('ItemName="{}", DisplayName="{}", Level="{}", OwnerReference="{}"'.format(
                                channel.ItemName,
                                channel.DisplayName,
                                channel.Level,
                                channel.OwnerReference))
                    except:
                        print('Channel "{}" not found by DisplayName match or ItemName match'.format(chan))

            return channel_ids, channel_list

        # # This is the script

        # after the functions above have been run, this will get the list of files and run through each of them sending the data to SCAN. and output from the script will be printed below this cell

        root, building, server = scan_api.open_token()
        building = next(b for b in root.Buildings if b.DisplayName == "FARO AIRPORT - PORTUGAL")
        channels_to_export = ExportChannels
        print(channels_to_export)

        p=os.path.join(self.dir, 'Exports/')
        print(listdir(p))
        for cosa in listdir(p):
            cosa=cosa.split("\\")[1]
            print(cosa)
            os.remove(os.path.join(p, str(cosa)))

        export_start, export_end, scenarios_to_export = simulation_parameters()
        export_csv_for_channel(building, export_start, export_end, scenarios_to_export, channels_to_export)

        i = 0
        names = []
        p = os.path.join(self.dir, 'Exports/')
        for cosa in listdir(pathRemove):

            zip_ref = zipfile.ZipFile(os.path.join(p, str(cosa)), 'r')
            zip_ref.extract(zip_ref.namelist()[0], self.path)
            x = cosa
            cosa = os.path.splitext(cosa[0] + '.csv')
            x = x.split("_")
            x = x[-1].split(".")
            if os.path.isfile(self.path + str(x[0]) + ".csv"):
                os.remove(self.path + str(x[0]) + ".csv")
            os.rename(self.path + zip_ref.namelist()[0], str(self.path) + str(x[0]) + ".csv")
            names.append(str(x[0]) + ".csv")
            zip_ref.close()
            i = i + 1
        if (Phase == "Weather"):
            self.Empty = os.path.join(self.dir, 'Simulaciones Vacias/')
            self.nameEmpty=names[0].replace("Faro","")
            self.nameEmpty=self.nameEmpty[0:4]+"-"+self.nameEmpty[4:6]+"-"+self.nameEmpty[6:8]+".csv"
            os.rename(str(self.path) + "/" + names[0],
                      self.Empty + "/" + str(self.nameEmpty))
            for file in range(1, len(names)):
                os.remove(str(self.path) + "/" + names[file])
                shutil.rmtree(str(self.path))
        else:
            for file in names:
                os.rename(str(self.path) + file,
                          self.pathIterations + str(Phase) + "_" + str(Iteration) + "_" + str(file))
                aux=os.path.join(self.dir, 'PlanesSimulados/')
                copyfile(self.pathIterations + str(Phase) + "_" + str(Iteration) + "_" + str(file), aux + "/"+ str(Phase) + "_" + str(Iteration) + "_" + str(file))

        if (Phase != "Weather"):
            self.readDataResultPreheating(Phase=Phase, Iteration=Iteration, names=names)

        pathPlot = self.pathPlot
        pathScenarios = "Scenarios/"
        iteration = Phase
        date = str(self.StarDate)
        # exec(open("Scenario_plots.py").read())
        return names[0]

    def ExtractingWeather(self):
        self.DryBulbTem = 0
        return self.DryBulbTem

    def Run_PreRooms(self, Occupancy=0):
        y = []
        if Occupancy != 0:
            self.Occupancy = Occupancy

        for i in range(0, len(self.Occupancy)):
            if self.Occupancy[i] == 0:
                y.append(self.Limit['Min'])
            if self.Occupancy[i] == 1:
                y.append(30)  # self.Limit['Max'])

        for indice in range(28, 38):
            y[indice] = 40
        for indice in range(38, 44):
            y[indice] = 35

        Options = [2]  # [56,62]#, ,4, 9, 12]

        Pre_Heating = []
        self.ScenariosList[0].setSetPoints(self.Channels[0], y.copy())
        Setpoint = self.ScenariosList[0].getSetpointPlot()
        ListSetpointPREHEATING = []
        ListSetpointNAMES = []
        for i in Options:
            x = self.ActiveTime[0] - i
            for tem in self.ValuesOfSensor:
                Setpoint = y.copy()
                for j in range(0, i):
                    Setpoint[x + j] = tem
                ListSetpointPREHEATING.append(Setpoint.copy())
        ban = False
        iteration = 1
        ListSetpointPREHEATING[0][24] = 35
        ListSetpointPREHEATING[0][25] = 35
        ListSetpointPREHEATING[0][26] = 40
        ListSetpointPREHEATING[0][27] = 40
        while (ban == False):
            print(len(ListSetpointPREHEATING))
            if len(ListSetpointPREHEATING) > self.Current:
                number = self.Current
            else:
                number = len(ListSetpointPREHEATING)
            print(len(self.ScenariosList))
            print(len(ListSetpointPREHEATING) > self.Current)
            print(len(ListSetpointPREHEATING))
            for i in range(0, number):
                auxlist = ListSetpointPREHEATING.pop()
                self.ScenariosList[i].setSetPoints(self.Channels[0], auxlist)
                self.ScenariosList[i].setOutPutName("Preheating_Option_" + str(len(ListSetpointPREHEATING) - i))
                # print(len(self.ScenariosList[i].getOutPutName()))
                # self.ScenariosList[i].ScenarioJsonToFile2(self.path, str(self.StarDate) + 'SANOMATALO_test' + str(iteration),
                #
                print(self.ScenariosList[i])
                # np.array(ListSetpointPREHEATING[iteration]))
                # print(len(np.array(ListSetpointPREHEATING[i])))
                # print(np.array(ListSetpointPREHEATING[i]))
                self.ScenariosList[i].ScenarioJsonToFile(self.pathScenarios, np.array(auxlist))
            self.RunSimulation(Iteration=iteration, Phase="PReHeating")
            iteration = iteration + 1
            ban = True
        return 1

    def Run_ReOPG(self, Hora):
        return 2

    def Run_Gredy(self):
        y = []
        print(len(self.Occupancy))
        for i in range(0, len(self.Occupancy)):
            if self.Occupancy[i] == 0:
                y.append(self.Limit['Min'])
            if self.Occupancy[i] == 1:
                y.append(20)  # self.Limit['Max'])

        Pre_Heating = []
        self.ScenariosList[0].setSetPoints(self.Channels[0], y.copy())
        Setpoint = self.ScenariosList[0].getSetpointPlot()
        ListSetpointPREHEATING = []
        ListSetpointNAMES = []
        for i in [1,2]:
            x = self.ActiveTime[0] - i
            for tem in self.ValuesOfSensor:
                Setpoint = y.copy()
                for j in range(0, i):
                    Setpoint[x + j] = tem
                print(Setpoint)
                ListSetpointPREHEATING.append(Setpoint.copy())
        ban = False
        iteration = 1

        while (ban == False):
            print(len(ListSetpointPREHEATING))
            if len(ListSetpointPREHEATING) > self.Current:
                number = self.Current
            else:
                number = len(ListSetpointPREHEATING)
            print(len(self.ScenariosList))
            print(len(ListSetpointPREHEATING) > self.Current)
            print(len(ListSetpointPREHEATING))
            for i in range(0, number):
                auxlist = ListSetpointPREHEATING.pop()
                self.ScenariosList[i].setSetPoints(self.Channels[0], auxlist)
                self.ScenariosList[i].setOutPutName("Preheating_Option_" + str(len(ListSetpointPREHEATING) - i))
                # print(len(self.ScenariosList[i].getOutPutName()))
                # self.ScenariosList[i].ScenarioJsonToFile2(self.path, str(self.StarDate) + 'SANOMATALO_test' + str(iteration),
                #
                print(self.ScenariosList[i])
                # np.array(ListSetpointPREHEATING[iteration]))
                # print(len(np.array(ListSetpointPREHEATING[i])))
                # print(np.array(ListSetpointPREHEATING[i]))
                self.ScenariosList[i].ScenarioJsonToFile(self.pathScenarios, np.array(auxlist))
            self.RunSimulation(Iteration=iteration, Phase="PReHeating")
            iteration = iteration + 1
            ban = True
        return 1

    def StoreScenario(self):
        return 1

    def WriteJsonB(self, Dic: dict, Name=""):
        """

        :type Dic: dict
        """
        import pandas as pd
        StarDay = pd.to_datetime(self.StarDate.strftime(format='%Y-%m-%d'),
                                 format='%Y-%m-%d', errors='raise', infer_datetime_format=False, exact=True)
        date_list = [StarDay + datetime.timedelta(minutes=x) for x in range(0, 1440, 15)]  # 0, 1440, 10
        # print(type(date_list[0]))
        # Json = ""
        # print(date_list)


        for i in Dic.keys():
            StringJson = "["
            if i == "SC002227":
                var = 1
                des = "UC76_CMD"
            elif i == "SC002236":
                var = 2
                des = "UC67_CMD"
            elif i == "SC002249":
                var = 3
                des = "UC78_CMD"
            elif i == "SC002271":
                var = 4
                des = "UC80_CMD"
            elif i == "SC002238":
                var = 5
                des = "UC77_CMD"
            elif i == "SC002310":
                var = 6
                des = "UC69_CMD"
            elif i == "SC002321":
                var = 7
                des = "UC70_CMD"
            elif i == "SC002282":
                var = 8
                des = "UC81_CMD"
            elif i == "SC002332":
                var = 9
                des = "UC71_CMD"
            elif i == "SC002354":
                var = 10
                des = "UC73_CMD"
            elif i == "SC002365":
                var = 11
                des = "UC74_CMD"
            elif i == "SC002376":
                var = 12
                des = "UC75_CMD"
            elif i == "SC002299":
                var = 13
                des = "UC68_CMD"
            elif i == "SC002343":
                var = 14
                des = "UC72_CMD"
            elif i == "SC002260":
                var = 15
                des = "UC79_CMD"
            for j in range(0, len(Dic[i])):
                StringJson = StringJson + "{" \
                                          "\"StartDateTime\": \"" + str(date_list[j].isoformat()) + "\",\n" + \
                             "\"VariableID\": " + str(var) + ",\n" + \
                             "\"VariableName\": \"" + str(i) + "\",\n" + \
                             "\"Description\": \"" + str(des) + "\",\n" + \
                             "\"Value\":" + str(Dic[i][j]) + "},\n"

            StringJson = StringJson[:-2] + "]"
            print(self.path)
            pathFull = os.path.abspath(self.path + Name+"pizarra" + "_Variable_" + str(i) + ".json")
            print(pathFull)
            with open(pathFull, "w") as out:
                out.write(StringJson)
        return 1

    def WriteJsonBRecalculo(self, Dic: dict, Name="", hour=0, Recalculo=0):
        """

        :type Dic: dict
        """
        import pandas as pd
        StarDay = pd.to_datetime(self.StarDate.strftime(format='%Y-%m-%d'),
                                 format='%Y-%m-%d', errors='raise', infer_datetime_format=False, exact=True)
        date_list = [StarDay + datetime.timedelta(minutes=x) for x in range(0, 1440, 15)]  # 0, 1440, 10
        # print(type(date_list[0]))
        # Json = ""
        # print(date_list)


        for i in Dic.keys():
            StringJson = "["
            if i == "SC002227":
                var = 1
                des = "UC76_CMD"
            elif i == "SC002236":
                var = 2
                des = "UC67_CMD"
            elif i == "SC002249":
                var = 3
                des = "UC78_CMD"
            elif i == "SC002271":
                var = 4
                des = "UC80_CMD"
            elif i == "SC002238":
                var = 5
                des = "UC77_CMD"
            elif i == "SC002310":
                var = 6
                des = "UC69_CMD"
            elif i == "SC002321":
                var = 7
                des = "UC70_CMD"
            elif i == "SC002282":
                var = 8
                des = "UC81_CMD"
            elif i == "SC002332":
                var = 9
                des = "UC71_CMD"
            elif i == "SC002354":
                var = 10
                des = "UC73_CMD"
            elif i == "SC002365":
                var = 11
                des = "UC74_CMD"
            elif i == "SC002376":
                var = 12
                des = "UC75_CMD"
            elif i == "SC002299":
                var = 13
                des = "UC68_CMD"
            elif i == "SC002343":
                var = 14
                des = "UC72_CMD"
            elif i == "SC002260":
                var = 15
                des = "UC79_CMD"
            for j in range(hour, len(Dic[i])):
                StringJson = StringJson + "{" \
                                          "\"StartDateTime\": \"" + str(date_list[j].isoformat()) + "\",\n" + \
                             "\"VariableID\": " + str(var) + ",\n" + \
                             "\"VariableName\": \"" + str(i) + "\",\n" + \
                             "\"Description\": \"" + str(des) + "\",\n" + \
                             "\"Value\":" + str(Dic[i][j]) + "},\n"

            StringJson = StringJson[:-2] + "]"
            print(self.path)
            if Recalculo==0:
                pathFull = os.path.abspath(self.path + Name + "pizarra" + "_Variable_" + str(i) + ".json")
            if Recalculo!=0:
                pathFull = os.path.abspath(self.path + Name +"_"+Recalculo+ "_pizarra" + "_Variable_" + str(i) + ".json")
            print(pathFull)
            with open(pathFull, "w") as out:
                out.write(StringJson)
        return 1