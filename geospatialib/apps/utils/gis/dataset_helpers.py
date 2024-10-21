from owslib import wms, wfs
from urllib.parse import urlparse

from ..general import util_helpers
from ...library import choices


def get_dataset_format(url):
    helpers = {
        'xyz': ['{x}','{y}','{z}', 'tile'],
    }
    format_list = list(choices.DATASET_FORMATS.keys())
    match = util_helpers.get_first_substring_match(url, format_list, helpers)
    return match


def get_dataset_layers(path, format):
    if format == 'xyz':
        domain = urlparse(path).netloc
        return {domain: domain}
    else:
        handler = {
            'wms': get_wms_layers,
            'ogc-wfs': get_wfs_layers,
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