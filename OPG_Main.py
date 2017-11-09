import OPG
import datetime
import pandas as pd

import shutil, os

listaHoras = ["0:00", "0:15", "0:30", "0:45", "1:00", "1:15", "1:30", "1:45",
              "2:00", "2:15", "2:30", "2:45", "3:00", "3:15", "3:30", "3:45",
              "4:00", "4:15", "4:30", "4:45", "5:00", "5:15", "5:30", "5:45",
              "6:00", "6:15", "6:30", "6:45", "7:00", "7:15", "7:30", "7:45",
              "8:00", "8:15", "8:30", "8:45", "9:00", "9:15", "9:30", "9:45",
              "10:00", "10:15", "10:30", "10:45", "11:00", "11:15", "11:30",
              "11:45", "12:00", "12:15", "12:30", "12:45", "13:00", "13:15",
              "13:30", "13:45", "14:00", "14:15", "14:30", "14:45", "15:00",
              "15:15", "15:30", "15:45", "16:00", "16:15", "16:30", "16:45",
              "17:00", "17:15", "17:30", "17:45", "0:00", "0:15", "0:30",
              "0:45", "19:00", "19:15", "19:30", "19:45", "20:00", "20:15",
              "20:30", "20:45", "21:00", "21:15", "21:30", "21:45", "22:00",
              "22:15", "22:30", "22:45", "23:00", "23:15", "23:30", "23:45"]
Limites = {"SC002227": {"Min": 0, "Max": 1},
           "SC002236": {"Min": 0, "Max": 1},
           "SC002249": {"Min": 0, "Max": 1},
           "SC002271": {"Min": 0, "Max": 1},
           "SC002238": {"Min": 0, "Max": 1},
           "SC002310": {"Min": 0, "Max": 1},
           "SC002321": {"Min": 0, "Max": 1},
           "SC002282": {"Min": 0, "Max": 1},
           "SC002332": {"Min": 0, "Max": 1},
           "SC002354": {"Min": 0, "Max": 1},
           "SC002365": {"Min": 0, "Max": 1},
           "SC002376": {"Min": 0, "Max": 1},
           "SC002299": {"Min": 0, "Max": 1},
           "SC002343": {"Min": 0, "Max": 1},
           "SC002260": {"Min": 0, "Max": 1},
           # Ocupacion
           "SC002477": {"Min": 0, "Max": 1},
           "SC002478": {"Min": 0, "Max": 1},
           "SC002479": {"Min": 0, "Max": 1},
           "SC002480": {"Min": 0, "Max": 1},
           "SC002481": {"Min": 0, "Max": 1},
           "SC002482": {"Min": 0, "Max": 1}
           }
SensorVal = {"SC002227": [0, 1], "SC002236": [0, 1], "SC002249": [0, 1], "SC002271": [0, 1],
             "SC002238": [0, 1], "SC002310": [0, 1], "SC002321": [0, 1], "SC002282": [0, 1],
             "SC002332": [0, 1], "SC002354": [0, 1], "SC002365": [0, 1], "SC002376": [0, 1],
             "SC002299": [0, 1], "SC002343": [0, 1], "SC002260": [0, 1],
             # Ocupacion
             "SC002477": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
             "SC002478": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
             "SC002479": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
             "SC002480": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
             "SC002481": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
             "SC002482": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
             }

Channels = ["SC002227", "SC002236", "SC002249", "SC002271", "SC002238", "SC002310",
            "SC002321", "SC002282", "SC002332", "SC002354", "SC002365", "SC002376",
            "SC002299", "SC002343", "SC002260",
            # Ocupacion
            "SC002477", "SC002478", "SC002479", "SC002480", "SC002481", "SC002482"]
Ocuppacion = ["SC002477", "SC002478", "SC002479", "SC002480", "SC002481", "SC002482"]
rooms = ["A51", "A52", "A53", "A54", "A55", "A56"]
dir = os.path.dirname(__file__)
print(dir)

p = "Data_Scenarios/"

from os import walk

from dateutil.parser import parse


def is_date(string):
    try:
        parse(string)
        return True
    except ValueError:
        return False


def ls(ruta='.'):
    dir, subdirs, archivos = next(walk(ruta))
    return subdirs, archivos


Lista = (ls(ruta=p))[0]
ListaFechas = []

# for i in Lista:
#    if is_date(i):
#        ListaFechas.append(i)


Lista = (ls(ruta=p))[1]  # "/"+ListaFechas[0])

for i in range(0, len(Lista)):
    Lista[i] = p + "/" + Lista[i]
print(Lista)

for name in Lista:
    print(name)
    SimulacionName = "Simulacion FARO Planes Ocupacion" + name.split("/")[2].replace(".csv", "_")
    print(name.split("/")[2])
    DIC = {}
    Datos = pd.read_csv(name)
    DIC["SC002227"] = list((Datos['SC002227']).astype(dtype=float))
    DIC["SC002236"] = list((Datos['SC002236']).astype(dtype=float))
    DIC["SC002249"] = list((Datos['SC002249']).astype(dtype=float))
    DIC["SC002271"] = list((Datos['SC002271']).astype(dtype=float))
    DIC["SC002238"] = list((Datos['SC002238']).astype(dtype=float))
    DIC["SC002310"] = list((Datos['SC002310']).astype(dtype=float))
    DIC["SC002321"] = list((Datos['SC002321']).astype(dtype=float))
    DIC["SC002282"] = list((Datos['SC002282']).astype(dtype=float))
    DIC["SC002332"] = list((Datos['SC002332']).astype(dtype=float))
    DIC["SC002354"] = list((Datos['SC002354']).astype(dtype=float))
    DIC["SC002365"] = list((Datos['SC002365']).astype(dtype=float))
    DIC["SC002376"] = list((Datos['SC002376']).astype(dtype=float))
    DIC["SC002299"] = list((Datos['SC002299']).astype(dtype=float))
    DIC["SC002343"] = list((Datos['SC002343']).astype(dtype=float))
    DIC["SC002260"] = list((Datos['SC002260']).astype(dtype=float))

    DicOcupacion = {}
    DicOcupacion["SC002477"] = list((Datos['SC002477']).astype(dtype=float))
    DicOcupacion["SC002478"] = list((Datos['SC002478']).astype(dtype=float))
    DicOcupacion["SC002479"] = list((Datos['SC002479']).astype(dtype=float))
    DicOcupacion["SC002480"] = list((Datos['SC002480']).astype(dtype=float))
    DicOcupacion["SC002481"] = list((Datos['SC002481']).astype(dtype=float))
    DicOcupacion["SC002482"] = list((Datos['SC002482']).astype(dtype=float))

    Dic4 = DIC.copy()
    print("######################################")
    print(DicOcupacion["SC002482"])

    inde = name.find("(")
    inde2 = name.find(")")
    Fecha = name[(inde + 1):inde2]
    Fecha = Fecha.split("-")
    print("######################################")
    print(Fecha)
    a = 0
    # Fecha=["08","07","2017"]
    a = OPG.OPG(Current=1, OcupacionChannels=Ocuppacion,
                OcuppacionRooms=rooms,
                StarDate=datetime.date(year=int(Fecha[2]), month=int(Fecha[1]), day=int(Fecha[0])),
                EndDate=datetime.date(year=int(Fecha[2]), month=int(Fecha[1]), day=int(Fecha[0])),
                Building="FARO",
                channels=Channels,
                limit=Limites,
                ValSensor=SensorVal,
                Directory=".")
    print(a.GetDate())
    a.GenerateOccupancy()
    a.Generate_Scenarios()
    plan = (name.split("__")[1].replace(".csv", "").replace(" ", ""))
    print(plan == "plan2")
    if (plan == "plan2"):
        a.WriteJsonB(Dic4, Name=name.split("__")[1].replace(".csv", ""))
    # a.ExtractingWeather()
    print(a.GetDate())

    Dic = [Dic4]  # ,Dic4]
    print("######################################")

    a.Generate_AutoOP(Dic, DicOcupacion)
    # a.RunSimulation()
    a.RunSimulation(SimulacionName, 1)
    # HechosOcupacion/
    print(shutil.move(name, p + str("Hechos/") + name.split("/")[2]))
