from owslib import wms, wfs
from urllib.parse import urlparse, urlunparse

from ..general import util_helpers
from ...library import choices

class XYZHandler():
    pass


def get_dataset_format(url):
    helpers = {
        'xyz': ['{x}','{y}','{z}', 'tile'],
    }
    format_list = list(choices.DATASET_FORMATS.keys())
    match = util_helpers.get_first_substring_match(url, format_list, helpers)
    return match

def resolve_dataset_access_path(path, format):
    if format in ['wms', 'xyz']:
        parsed_url = urlparse(path)
        parsed_url = parsed_url._replace(query='')
        return urlunparse(parsed_url)


def get_dataset_layers(path, format):
    if format == 'xyz':
        domain = urlparse(path).netloc
        return {domain: domain}
    else:
        handler = {
            'wms': get_wms_layers,
            'wfs': get_wfs_layers,
        }.get(format, None)

        if handler:
            try:
                return handler(path)
            except Exception as e:
                print('ERROR with get_dataset_layers: ', e)

def get_wms_layers(path):
    service = wms.WebMapService(path)
    contents = service.contents
    layers = {}
    for layer_name in contents:
        layers[layer_name] = service[layer_name].title
    return layers

def get_wfs_layers(path):
    service = wfs.WebFeatureService(path)
    contents = service.contents
    layers = {}
    for layer_name in contents:
        layers[layer_name] = service[layer_name].title
    return layers


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