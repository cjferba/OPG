# -*- coding: utf-8 -*-

import pandas as pd
import os
import cx_Oracle


def GetOccupation(DateStart,DateEnd, Site, Subsite):

    # jdbcConnection < - dbConnect(jdbcDriver, "jdbc:", "",
    #                              "")
    #
    # date = today()
    # # Query on the Oracle instance name.
    # instanceName < - dbGetQuery(
    #     jdbcConnection, paste("
    # '",
    # format(today(), format="%d-%m-%y"), "' and '",
    # format(today() + 1, format="%d-%m-%y"), "'", sep = ""))


    connection = cx_Oracle.connect("opg", "opg3n3rgy", "oracle:thin:@//150.214.203.106:1521/occupancy_faro")

    connstr = 'scott/tiger@server:1521/orcl'
    conn = cx_Oracle.connect(connstr)


    cursor = connection.cursor()
    cursor.execute("""select * from eit.occupancy_view
                      WHERE
                      eit.occupancy_view.OCU_DATE
                      between""",
                   did=50,
                   eid=190)
    #for fname, lname in cursor:
     #   print("Values:", fname, lname)


    Lista=[]
    for name in Lista:
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
    return 0

if __name__ == '__main__':
    GetOccupation("", "", "", "")