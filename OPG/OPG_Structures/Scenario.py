import json
import pandas as pd
import datetime
import os
from bokeh.layouts import gridplot
from bokeh.plotting import figure

from bokeh.io import save

class Scenario:
    """Esta clase se utiliza para la representacion de un escenario para enviarselo al simulador

        - **parameters**, **types**, **return** and **return types**::

              :param arg1: description
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
    Name = None
    OutPutName=""
    Date = None
    Sample_period = None
    Channels = []
    Weather = []
    Ocuppacy=[]
    SetPoints = {}
    SetPointsPlot = figure()
    # Datos sobre los resultados de la simulacion
    ResultSetPoint = {}
    Result = pd.DataFrame()

    def __init__(self, Name, Channel, Date, Freq, SetPoints):
        self.Name = Name
        self.Date = Date
        self.Sample_period = Freq
        self.Channels = Channel
        self.SetPoints = SetPoints
        self.SetPointsPlot=[]
        for i in self.Channels:
            self.SetPointsPlot.append(figure(x_axis_type="datetime", title=str(self.Name)+"Setpoint"+str(i), width=1300, height=500))
    def GetScenario(self):
        ListaStringScenario=[]
        for i in self.Channels:
            StringJsonScenario = "{\n"
            Dic = {}
            Dic2 = {}
            Dic["sample_period"] = self.Sample_period
            Dic["channels"] = [i]
            #print(self.SetPoints.keys())
            Dic[str(self.Date)] = self.SetPoints[i]
            Dic2[str(self.Name)] = Dic
            x=(json.dumps(Dic2,indent=2))
            #x=x.replace(",", ",\n\t")
            #x = x.replace("[", "[\n")
            #x = x.replace("]", "\n]")
            StringJsonScenario=StringJsonScenario+ str(x)[1:-1]+"\n,"
            StringJsonScenario=StringJsonScenario[:-1]+"\n}"
            ListaStringScenario.append(StringJsonScenario)
        #StringJsonScenario = StringJsonScenario.replace("{", "\n{")
        return ListaStringScenario

    def getDate(self):
        return self.Date
    def setDate(self,date):
        self.Date=date
    def getName(self):
        return self.Name
    def setName(self, name):
        self.Name = name
        return name
    def GetOutPutName(self):
        return self.OutPutName
    def setOutPutName(self,Name):
        self.OutPutName=Name
    def getSetpoint(self,chanel):
        return self.SetPoints[chanel]
    def getAllSetpoint(self):
        return self.SetPoints
    def setSetPoints(self, Channel, Setpoint):
        #index = self.Channels.index(Channel)
        #self.SetPoints[index] = Setpoint
        self.SetPoints[Channel]=Setpoint
        base = pd.to_datetime(self.getDate(), format="%Y-%m-%d", errors="raise",
                              infer_datetime_format=False, exact=True)

        freq =self.Sample_period
        date_list = [base + datetime.timedelta(minutes=x) for x in range(0, 1440, freq)]
        DataFrameSetPoint = pd.DataFrame({"Timestamp": date_list,
                                         "SimulationSetPoints": self.SetPoints[Channel]})
        self.SetPointsPlot.grid.grid_line_alpha = 0.3
        self.SetPointsPlot.xaxis.axis_label = "Date"
        self.SetPointsPlot.yaxis.axis_label = "Value"
        self.SetPointsPlot.legend.location = "top_left"
        #setpointValue = dfsSimulation[0]["SimulationSetPoints"]

        self.SetPointsPlot.line(DataFrameSetPoint["Timestamp"], DataFrameSetPoint["SimulationSetPoints"],
                          legend="Setpoint Interpolated")  # ,fill_color="green",  size=3)
        self.SetPointsPlot.circle(DataFrameSetPoint["Timestamp"], DataFrameSetPoint["SimulationSetPoints"],
                            legend="Setpoint sending", fill_color="red", size=5)

        #grid = gridplot([ListSetpoint])
        #save(grid, pathPlot + "/setpoint" + str(iteration) + str(filename.split("/")[-1]) + str(date) + ".html")
        return self.SetPointsPlot

    def setAllSetPoints(self, Setpoint):
        # index = self.Channels.index(Channel)
        # self.SetPoints[index] = Setpoint
        self.SetPoints = Setpoint
    def getSetpointPlot(self,name):
        return self.SetPointsPlot
    def getChannels(self):
        return self.Channels
    def setChannels(self, chanels):
        self.Channels = chanels
        return chanels

    def WriteJsonScenario(self):
        json_data = (self.GetScenario())#json.dumps
        return json_data

    def ScenarioJsonToFile(self,weather=False, path="Scenarios/"):
        if weather==True:
            p = os.path.join(path)
            print("entra")
            pathFull = os.path.abspath(p + self.Name + "variableEmpty.json")
            with open(pathFull, "w") as out:
                out.write("{\""+self.getName()+"\": {"
                          "        \"sample_period\": 15,"
                          "        \"channels\": []"
                          "    }}")
        else:
            lista=self.GetScenario()
            for i in range(0,len(lista)):
                p = os.path.join(path)
                pathFull = os.path.abspath(p+self.Name+"variable_"+str(i) + ".json")
                with open(pathFull ,"w") as out:
                    out.write(lista[i])
                    print("entramos Mandar setpoint")
            return self.GetScenario()

    def ScenarioJsonToFile2(self,name, path="Scenarios/"):
        pathFull = os.path.abspath(path + name + ".json")
        with open(pathFull, "w") as out:
            out.write(self.GetScenario())
        return self.GetScenario()

        # for i in self.SetPoints:
        #     data[key1][keys2[0]][j] = float(lista[j])
        #     j = j + 1
        # pathFull = os.path.abspath(path + "/" + name + ".json")
        # with open(pathFull,"w") as out:
        #     json.dump((data), out, sort_keys=True, indent=4, ensure_ascii=False)
        # return 0


