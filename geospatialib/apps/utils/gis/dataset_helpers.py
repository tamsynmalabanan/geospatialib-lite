from django.core.cache import cache
from django.contrib.gis.geos import Polygon
from django.contrib.gis.gdal import SpatialReference

from owslib import wms, wfs
from urllib.parse import urlparse, urlunparse
import json

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

    def populate_dataset(self, dataset):
        dataset.bbox = geom_helpers.WORLD_GEOM
        
        dataset.save()

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
        except Exception as e:
            service = None

        if service:
            self.access_url = service.url
            self.layers = self.get_layers(service)

    def get_title(self, layer):
        if layer and hasattr(layer, 'title'):
            return layer.title

    def get_bbox(self, layer):
        bbox = None
        
        if layer:
            for attr in ['boundingBoxWGS84', 'boundingBox']:
                if hasattr(layer, attr) and isinstance(getattr(layer, attr), (list, tuple)):
                    bbox = getattr(layer, attr)
                    break
        
        if bbox:
            w,s,e,n,*srid = bbox
            bbox_corners = [(w,s), (e,s), (e,n), (w,n), (w,s)]
            if len(srid) != 0 and ':' in srid[0]:
                bbox_srid = int(srid[0].split(':')[1])
            else:
                bbox_srid = 4326
            
            geom = Polygon(bbox_corners, srid=bbox_srid)
            if bbox_srid == 4326:
                return geom
            else:
                wgs84_srs = SpatialReference(4326)
                return geom.transform(wgs84_srs, clone=True)
        else:
            return geom_helpers.WORLD_GEOM

    def get_data(self, service, layer):
        id = service.identification if hasattr(service, 'identification') else None
        provider = service.provider if hasattr(service, 'provider') else None

        data = {}
        
        if id:
            for attr in ['accessconstraints', 'fees']:
                if hasattr(id, attr):
                    data[attr] = getattr(id, attr)
        
        if layer:
            for attr in ['queryable', 'styles', 'dataUrls', 'metadataUrls']:
                if hasattr(layer, attr):
                    data[attr] = getattr(layer, attr)
            if hasattr(layer, 'auth') and hasattr(getattr(layer, 'auth'), '__dict__'):
                data['auth'] = vars(getattr(layer, 'auth'))

        if provider:
            provider = {}
            for attr in ['name', 'url']:
                if hasattr(provider, attr):
                    provider[attr] = getattr(provider, attr)
            if hasattr(provider, 'contact') and hasattr(getattr(provider, 'contact'), '__dict__'):
                provider['contact'] = vars(getattr(provider, 'contact'))
            data['provider'] = provider

        objects = [obj for obj in [id, layer] if obj is not None]

        titles = []
        for obj in objects:
            if hasattr(obj, 'title'):
                title = obj.title
                if isinstance(title, str):
                    titles.append(title)
        data['title'] = ' - '.join(titles)

        abstracts = []
        for obj in objects:
            if hasattr(obj, 'abstract'):
                abstract = obj.abstract
                if isinstance(abstract, str):
                    abstracts.append(abstract)
        data['abstract'] = '<br><br>'.join(abstracts)

        keywords = []
        for obj in objects:
            if hasattr(obj, 'keywords') and isinstance(obj.keywords, (list, tuple)):
                keywords = keywords + list(obj.keywords)
        data['keywords'] = list(set(keywords))

        return json.dumps(data)

    def populate_dataset(self, dataset):
        try:
            service = wms.WebMapService(self.path)
        except Exception as e:
            service = None

        if service:
            layer_name = dataset.name
        
            try:
                layer = service[layer_name]
            except:
                layer = None
            
            dataset.title = self.get_title(layer)
            dataset.bbox = self.get_bbox(layer)
            dataset.data = self.get_data(service, layer)

            dataset.save()

    def test_connection(self, layer_name):
        try:
            service = wms.WebMapService(url=url)
        except:
            service = None

        if service:
            try:
                layer = service[layer_name]
            except:
                layer = None
            
            if layer:
                try:
                    response = service.getmap(
                        layers=[layer.id],
                        srs='EPSG:4326',
                        bbox=layer.boundingBoxWGS84,
                        size=(512, 512),
                        format='image/jpeg',
                        transparent=True
                    )
                    return response.read()
                except Exception as e:
                    return None

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
            print('ERROR with WFSHandler handler', e)
   

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

