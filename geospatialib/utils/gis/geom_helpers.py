from django.contrib.gis.geos import Polygon, GEOSGeometry

WORLD_BBOX = (-180, -90, 180, 90, 'EPSG:4326')
WORLD_GEOJSON_GEOM = '{"type":"Polygon","coordinates":[[[-180,-90],[-180,90],[180,90],[180,-90],[-180,-90]]]}'
WORLD_GEOM = GEOSGeometry(WORLD_GEOJSON_GEOM)
