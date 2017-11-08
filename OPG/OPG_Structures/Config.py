import datetime
import json

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
