import httplib2 as http
from os import walk
import shutil, os
import datetime

date=datetime.date.today()+ datetime.timedelta(days=1)#25,24,23,22,21,20


pathJson='OutPut/'+date.strftime("%Y-%m-%d")+'/'

print(pathJson)

dir = os.path.dirname(__file__)
p=os.path.join(dir, pathJson)

from pathlib import Path

def ls(ruta = Path.cwd()):
    return [arch.name for arch in Path(ruta).iterdir() if arch.is_file()]

Lista=(ls(ruta=p))


for i in Lista:
    pathLista=os.path.join(dir, pathJson+i)
    try:
        from urlparse import urlparse
    except ImportError:
        from urllib.parse import urlparse

    headers = {
        'Content-Type': 'application/json',
        'x-access-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJVc2VyIjoiT1BHIiwiUGlsb3QiOiJGQVJPIiwiZXhwIjoxNTE5MTMxOTk2LCJpYXQiOjE0ODc1OTU5OTZ9.ZJfXJrebFV54VttkPKjdbIYplJzEjkF54aGJek2MukQ'
        }

    uri = 'http://citic-ps9.ugr.es:8099'
    path = '/project/EnergyInTime/OPG/FaroAirport/setpoints/store-plan'

    '''
    data = {}
    data['key'] = 'value'
    json_data = json.dumps(data)
    body = json.dumps(data);
    '''


    target = urlparse(uri+path)
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
