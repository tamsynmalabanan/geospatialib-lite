from django.core.cache import cache

from owslib import wms, wfs
from urllib.parse import urlparse, urlunparse

from . import geom_helpers
from ..general import util_helpers
from ...library import choices



class DatasetHandler():
    access_url = None
    layers = None

    def __init__(self, path, key):
        self.path = path
        self.key = key
        
        self.handler()

        cache.set(key, self, timeout=3600)

class XYZHandler(DatasetHandler):

    def get_layers(self):
        domain = urlparse(self.path).netloc
        return {domain: domain}
    
    def handler(self):
        self.access_url = self.path
        self.layers = self.get_layers()

class WMSHandler(DatasetHandler):
    
    def get_layers(self, service):
        contents = service.contents
        layers = {}
        for layer_name in contents:
            layers[layer_name] = service[layer_name].title
        return layers

    def handler(self):
        try:
            service = wms.WebMapService(self.path)
            self.access_url = service.url
            self.layers = self.get_layers(service)
        except Exception as e:
            print(e)

    def populate_dataset(self, dataset):
        pass

class WFSHandler(DatasetHandler):

    def get_layers(self, service):
        contents = service.contents
        layers = {}
        for layer_name in contents:
            layers[layer_name] = service[layer_name].title
        return layers

    def handler(self):
        try:
            service = wfs.WebFeatureService(self.path)
            self.access_url = service.url
            self.layers = self.get_layers(service)
        except Exception as e:
            print(e)

            

def get_dataset_handler(format, **kwargs):
    handler = {
        'xyz': XYZHandler, 
        'wms': WMSHandler, 
    }.get(format)

    if handler:
        return handler(**kwargs)

def get_dataset_format(url):
    helpers = {
        'xyz': ['{x}','{y}','{z}', 'tile'],
    }
    format_list = list(choices.DATASET_FORMATS.keys())
    match = util_helpers.get_first_substring_match(url, format_list, helpers)
    return match




def wms_request(url, name):
    service = wms.WebMapService(url=url)
    layer = service[name]
    
    try:
        response = service.getmap(
            layers=[name],
            srs='EPSG:4326',
            bbox=layer.boundingBoxWGS84,
            size=(512, 512),
            format='image/jpeg',
            transparent=True
        )
        print(response)
        with open('map.png', 'wb') as f:
            f.write(response.read())
    except Exception as e:
        print('ERROR with wms_request: ', e)