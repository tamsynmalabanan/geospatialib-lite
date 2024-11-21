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

    def handler(self):
        pass

class XYZHandler(DatasetHandler):

    def get_layers(self):
        name = util_helpers.get_domain_name(self.url)
        return {name: name}
    
    def handler(self):
        self.access_url = self.url
        self.layers = self.get_layers()

    def populate_dataset(self, dataset):
        content = dataset.content

        content.label = dataset.name.replace('_', ' ')
        content.bbox = geom_helpers.WORLD_GEOM
        content.tags.set(
            model_helpers.collect_url_tags(
                util_helpers.remove_query_params(self.access_url)
            )
        )

        content.save()

class ArcGISImageHandler(DatasetHandler):

    def get_layers(self):
        domain = urlparse(self.url).netloc
        if domain.endswith('arcgis.com'):
            name = self.url.split('.arcgis.com/arcgis/rest/services/')[1].split('/ImageServer')[0].replace('/', ' ')
        else:
            name = util_helpers.get_domain_name(self.url)
        return {name: name}
    
    def handler(self):
        self.access_url = self.url
        self.layers = self.get_layers()

    def populate_dataset(self, dataset):
        content = dataset.content

        content.label = dataset.name.replace('_', ' ')
        content.bbox = geom_helpers.WORLD_GEOM
        content.tags.set(
            model_helpers.collect_url_tags(
                util_helpers.remove_query_params(self.access_url)
            )
        )

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
            label = layer.title
        else:
            label = self.dataset.name
        return label.replace('_', ' ')

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
        for obj in [id, layer]:
            if obj and hasattr(obj, 'keywords') and isinstance(obj.keywords, (list, tuple)):
                keywords = keywords + list(obj.keywords)

        clean_keywords = []
        for kw in keywords:
            if ',' in kw:
                kws = [i.strip() for i in kw.split(',')]
                for i in kws:
                    clean_keywords.append(i)
            else:
                clean_keywords.append(kw)

        clean_keywords = list(set(clean_keywords))

        for kw in clean_keywords:
            if isinstance(kw, str):
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
            
            styles = extra_data.get('layer', {}).get('styles', {})
            if styles:
                name = list(styles.keys())[0]
                dataset.default_style = name
                
                url = styles[name].get('legend')
                if url:
                    url_instance, created = models.URL.objects.get_or_create(url=url)
                    if url_instance:
                        dataset.default_legend = url_instance
            
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

    def get_service(self):
        try:
            return wfs.WebFeatureService(self.access_url)
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
            label = layer.title
        else:
            label = self.dataset.name
        return label.replace('_', ' ')

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
        for obj in [id, layer]:
            if obj and hasattr(obj, 'keywords') and isinstance(obj.keywords, (list, tuple)):
                keywords = keywords + list(obj.keywords)

        clean_keywords = []
        for kw in keywords:
            if ',' in kw:
                kws = [i.strip() for i in kw.split(',')]
                for i in kws:
                    clean_keywords.append(i)
            else:
                clean_keywords.append(kw)

        clean_keywords = list(set(clean_keywords))

        for kw in clean_keywords:
            if isinstance(kw, str):
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
            
            styles = extra_data.get('layer', {}).get('styles', {})
            if styles:
                name = list(styles.keys())[0]
                dataset.default_style_name = name
                
                url = styles[name].get('legend')
                url_instance, created = models.URL.objects.get_or_create(url=url)
                if url_instance:
                    dataset.default_style_url = url_instance
            
            dataset.save()

            content = dataset.content
            content.label = self.get_label(layer)
            content.bbox = self.get_bbox(layer)
            content.abstract = self.get_abstract(id, layer)
            content.tags.set(self.get_tags(id, layer))
            content.save()



def get_dataset_handler(format, **kwargs):
    handler = {
        'xyz': XYZHandler, 
        'wms': WMSHandler, 
        'wfs': WFSHandler, 
        'arcgis-image': ArcGISImageHandler, 
    }.get(format)

    if handler:
        return handler(**kwargs)

def get_dataset_format(url):
    helpers = {
        'xyz': ['{x}','{y}','{z}', 'tile'],
        'arcgis-image': ['ImageServer'],
    }
    format_list = list(choices.DATASET_FORMATS.keys())
    match = util_helpers.get_first_substring_match(url, format_list, helpers)
    return match

