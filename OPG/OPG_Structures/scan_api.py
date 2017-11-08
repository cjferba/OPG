import json
from urllib.parse import urljoin
from urllib.request import urlopen, Request
import http.client
import mimetypes
import os

# from http://blog.spotflux.com/uploading-files-python-3/


def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for
    data to be uploaded as files
    Return (content_type, body) ready for http.client connection instance
    """
    BOUNDARY_STR = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = bytes("\r\n", "ASCII")
    L = []
    if fields is not None:
        for key, value in fields.items():
            L.append(bytes("--" + BOUNDARY_STR, "ASCII"))
            L.append(
                bytes(
                    'Content-Disposition: form-data; name="%s"' %
                    key, "ASCII"))
            L.append(b'')
            L.append(bytes(value, "ASCII"))
    if files is not None:
        print(os.getcwd())
        for key, filename in files.items():
            L.append(bytes('--' + BOUNDARY_STR, "ASCII"))
            L.append(
                bytes(
                    'Content-Disposition: form-data; name="%s"; filename="%s"' %
                    (key, filename), "ASCII"))
            L.append(
                bytes(
                    'Content-Type: %s' %
                    get_content_type(filename),
                    "ASCII"))
            L.append(b'')
            with open(filename, 'rb') as f:
                byte = f.read()
                while byte:
                    L.append(byte)
                    byte = f.read()

    L.append(bytes('--' + BOUNDARY_STR + '--', "ASCII"))
    L.append(b'')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=' + BOUNDARY_STR
    return content_type, body


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

# end http://blog.spotflux.com/uploading-files-python-3/


def expand_url(url, args):
    for k, v in args.items():
        url = url.replace('{' + k + '}', str(v))
    return url


class Api(object):
    """
    The Api object has a token and a root URL for API access to a SCAN project.

    The API token is created for a specific project and allows a script to
    impersonate that user.  see 'API tokens' under the project menu

    set the base URL of the project the token is for, obtained from the
    link at the bottom of the project's 'API tokens' page.
    e.g.  BASE_URL = 'https://scan.iseve.com/project/ApiTestProject'

    root = open_api(BASE_URL, API_TOKEN)

    get and post helpers for JSON and raw data, inserting the bearer token into
    the Authorization header
    """

    def __init__(self, base_url, api_token):
        self._base_url = base_url
        self._api_token = api_token

    def root(self):
        """GET the api object for the base URL of the project"""
        req = Request(self._base_url)
        req.add_header('Authorization', 'Bearer ' + self._api_token)
        res = urlopen(req)
        root = ApiObject(
            self, json.loads(
                res.read().decode(
                    res.info().get_param('charset') or 'utf-8')))
        root._links['details'] = {'href': self._base_url}
        return root

    def get_json(self, url, **kwargs):
        """GET the url relative to the base url and return a dict populated from the returned json"""
        url = expand_url(url, kwargs)
        req = Request(urljoin(self._base_url, url))
        req.add_header('Authorization', 'Bearer ' + self._api_token)
        res = urlopen(req)
        return json.loads(res.read().decode(
            res.info().get_param('charset') or 'utf-8'))

    def _get_object(self, url, **kwargs):
        return self._to_object(self.get_json(url, **kwargs), url)

    def _post_object(self, url, data, **kwargs):
        return self._to_object(self.post_json(url, data, **kwargs))

    def _to_object(self, json, url = None):
        if 'Error' in json:
            raise ApiError(self, json['Message'])
        return ApiObject(self, json, url)

    def get_raw(self, url, **kwargs):
        """GET the url relative to the base url and return the response"""
        url = expand_url(url, kwargs)
        req = Request(urljoin(self._base_url, url))
        req.add_header('Authorization', 'Bearer ' + self._api_token)
        return urlopen(req)

    def post_json(self, url, data, **kwargs):
        """POST the given data to the url relative to the base url and return a dict populated from the returned json"""
        url = expand_url(url, kwargs)
        req = Request(urljoin(self._base_url, url),
                      json.dumps(data).encode('utf-8'))
        req.add_header('Authorization', 'Bearer ' + self._api_token)
        req.add_header('Content-Type', 'application/json')
        res = urlopen(req)
        return json.loads(res.read().decode(
            res.info().get_param('charset') or 'utf-8'))

    def post_raw(self, url, data, content_type, **kwargs):
        """POST the given data to the url relative to the base url and return the response"""
        url = expand_url(url, kwargs)
        req = Request(urljoin(self._base_url, url), data)
        req.add_header('Authorization', 'Bearer ' + self._api_token)
        req.add_header('Content-Type', content_type)
        return urlopen(req)

    def put_raw(self, url, data, content_type, **kwargs):
        """PUT the given data to the url relative to the base url and return the response"""
        url = expand_url(url, kwargs)
        req = Request(urljoin(self._base_url, url), data, method='PUT')
        req.add_header('Authorization', 'Bearer ' + self._api_token)
        req.add_header('Content-Type', content_type)
        return urlopen(req)


def to_api_object_recurse(api, data):
    return ApiObject(api, data) if isinstance(data, dict) else data


class ApiError(Exception):

    def __init__(self, source, message):
        self.source = source
        self.message = message

    def __str__(self):
        return repr(self.message)


class ApiObject(object):
    """Wraps the endpoints in the json API as actions on objects and their properties."""

    def __str__(self):
        name = self.DisplayName if 'DisplayName' in self.__dict__ else '?'
        item = self.ItemName if 'ItemName' in self.__dict__ else '?'
        link = self._links['details']['href'] if 'details' in self._links else '?'
        return '<ApiObject `{0}` [{1}] @ {2} = {3}>'.format(name, item, link, self.to_data())
    def name(self):
        return self.DisplayName
    def Itemname(self):
        return self.ItemName
    def __init__(self, api, parms, url=None):
        self._api = api
        self._links = {}
        # if an url is passed, it is the url used to get this object, so can be used to refresh it
        if url is not None:
            self._links['details'] = {'href': url}
        self._update(parms)

    def get(self, relation, **kwargs):
        """GET the related url for the object and return an ApiObject populated from the returned json"""
        return self._api._get_object(self._links[relation]['href'], **kwargs)

    def get_raw(self, relation, **kwargs):
        """GET the related url for the object and return the raw data"""
        return self._api.get_raw(self._links[relation]['href'], **kwargs)

    def post(self, relation, data, **kwargs):
        """POST the data to the related url for the object and return an ApiObject populated from the returned json. Data may be dict, list, primitve or ApiObject"""
        #print(relation)
        #print(data)
        return self._api._post_object(self._links[relation]['href'], value_to_data(data), **kwargs)

    def post_files(self, relation, data, files):
        """POST the contents of the file to the related url for the object and return an ApiObject populated from the returned json."""

        content_type, body = encode_multipart_formdata(data, files)
        api = self._api
        res = api.post_raw(self._links[relation]['href'], body, content_type)
        return api._to_object(json.loads(res.read().decode(
            res.info().get_param('charset') or 'utf-8')))

    def put_file(self, relation, filename):
        """PUTs the contents of the file to the related url for the object and return an ApiObject populated from the returned json."""

        with open(filename, 'rb') as f:
            byte = f.read()

        api = self._api
        url = self._links[relation]['href']
        res = api.put_raw(url, byte, 'application/octet-stream')
        return api._to_object(json.loads(res.read().decode(res.info().get_param('charset') or 'utf-8')), url)

    def refresh(self):
        """Fetch the object's data again via its 'details' link"""
        update = self._api.get_json(self._links['details']['href'])
        self._update(update)
        return self

    def update(self):
        """Saves any changes made to the object by post the object's data to its 'update' link"""
        update = self._api.post_json(
            self._links['update']['href'], self.to_data())
        self._update(update)
        return self

    def _update(self, update):
        if 'Error' in update:
            raise ApiError(self, update['Message'])

        api = self._api

        if '_links' in update:
            self._links.update(update['_links'])
            del update['_links']

        for k, v in update.items():
            if isinstance(v, dict) and '_links' in v:
                update[k] = ApiObject(api, v)
            elif isinstance(v, list):
                update[k] = [to_api_object_recurse(api, item) for item in v]

        self.__dict__.update(update)

        return self

    def to_data(self):
        """Convert to a dict suitable for JSON serialisation"""
        return dict_to_data(self.__dict__)

def dict_to_data(d):
    data = {}

    for k, v in d.items():
        if k == '_links':
            continue
        if k == '_api':
            continue
        data[k] = value_to_data(v);

    return data;

def value_to_data(v):
    if type(v) is ApiObject:
        return v.to_data()
    elif isinstance(v, list):
        return [value_to_data(item) for item in v]
    elif isinstance(v, dict):
        return dict_to_data(v)
    else:
        return v

def open_api(base_url, api_token):
    return Api(base_url, api_token).root()

def open_token(path=None):
    with open(path or 'scan.token', 'r') as f:
        server_url = f.readline().rstrip()
        api_token = f.readline().rstrip()
        root_url = f.readline().rstrip()
        root = open_api(root_url, api_token)
        line = f.readline()
        building = None

        if line:
            building_url = line.rstrip()[len(server_url)-1:]
            try:
                building = next(item.refresh() for item in root.Buildings if item._links['details']['href'] == building_url)
            except:
                pass
    return root, building, server_url

