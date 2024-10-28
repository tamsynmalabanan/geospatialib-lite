from django.core.cache import cache
from django.contrib.gis.geos import Polygon
from django.contrib.gis.gdal import SpatialReference

from owslib import wms, wfs
from urllib.parse import urlparse, urlunparse
import json

from . import geom_helpers
from ..general import util_helpers, model_helpers
from apps.library import choices, models


class DatasetHandler():
    access_url = None
    layers = None

    def __init__(self, url, key):
        self.url = url
        self.key = key
        
        self.handler()

        cache.set(key, self, timeout=3600)

class XYZHandler(DatasetHandler):

    def get_layers(self):
        domain = urlparse(self.url).netloc
        return {domain: domain}
    
    def handler(self):
        self.access_url = self.url
        self.layers = self.get_layers()

    def populate_dataset(self, dataset):
        content = dataset.content

        content.label = urlparse(self.access_url).netloc
        content.bbox = geom_helpers.WORLD_GEOM
        content.tags.set(model_helpers.collect_url_tags(self.access_url))

        content.save()

class WMSHandler(DatasetHandler):
    
    def get_service(self):
        try:
            return wms.WebMapService(self.access_url)
        except:
            return

    def get_layers(self, service):
        contents = service.contents
        layers = {}
        for layer_name in contents:
            layers[layer_name] = service[layer_name].title
        return layers

    def handler(self):
        clean_url = util_helpers.remove_query_params(self.url)
        self.access_url = clean_url

        service = self.get_service()
        if service:
            self.layers = self.get_layers(service)

    def get_label(self, layer):
        if layer and hasattr(layer, 'title'):
            return layer.title
        return self.dataset.name

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

    def get_tags(self, id, layer):
        tag_instances = model_helpers.collect_url_tags(self.access_url)

        keywords = []
        for obj in [obj for obj in [id, layer] if obj is not None]:
            if hasattr(obj, 'keywords') and isinstance(obj.keywords, (list, tuple)):
                keywords = keywords + list(obj.keywords)
        keywords = list(set(keywords))

        for kw in keywords:
            tag_instance, created = models.Tag.objects.get_or_create(tag=kw.lower())
            if tag_instance:
                tag_instances.append(tag_instance)

        return tag_instances

    def get_abstract(self, id, layer):
        abstracts = []
        for obj in [id, layer]:
            if obj and hasattr(obj, 'abstract'):
                abstract = obj.abstract
                if isinstance(abstract, str) and abstract.strip() != '':
                    abstracts.append(abstract)
        return '<br><br>'.join(abstracts)

    def get_extra_data(self, id, provider, layer):
        data = {}
        
        if id:
            id_vars = {}
            for attr in ['accessconstraints', 'fees']:
                if hasattr(id, attr):
                    id_vars[attr] = getattr(id, attr)
            data['id'] = id_vars
        
        if layer:
            layer_vars = {}
            for attr in ['queryable', 'styles', 'dataUrls', 'metadataUrls']:
                if hasattr(layer, attr):
                    layer_vars[attr] = getattr(layer, attr)
            if hasattr(layer, 'auth') and hasattr(getattr(layer, 'auth'), '__dict__'):
                layer_vars['auth'] = vars(getattr(layer, 'auth'))
            data['layer'] = layer_vars

        if provider:
            provider_vars = {}
            for attr in ['name', 'url']:
                if hasattr(provider, attr):
                    provider_vars[attr] = getattr(provider, attr)
            if hasattr(provider, 'contact') and hasattr(getattr(provider, 'contact'), '__dict__'):
                provider_vars['contact'] = vars(getattr(provider, 'contact'))
            data['provider'] = provider_vars

        return data

    def populate_dataset(self, dataset):
        self.dataset = dataset

        service = self.get_service()
        if service:
            id = service.identification
            provider = service.provider
            layer = service[dataset.name]

            extra_data = self.get_extra_data(id, provider, layer)
            dataset.extra_data = json.dumps(extra_data)
            dataset.save()

            content = dataset.content
            content.label = self.get_label(layer)
            content.bbox = self.get_bbox(layer)
            content.abstract = self.get_abstract(id, layer)
            content.tags.set(self.get_tags(id, layer))
            content.save()

    def test_connection(self, layer_name):
        service = self.get_service()
        if service:
            layer = service[layer_name]
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
        clean_url = util_helpers.remove_query_params(self.url)
        self.access_url = clean_url

        try:
            service = wfs.WebFeatureService(clean_url)
        except Exception as e:
            service = None
        
        if service:
            self.layers = self.get_layers(service)


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

