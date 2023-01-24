import json
from geojson import Feature, LineString, FeatureCollection, Polygon, MultiLineString
from turfpy.transformation import line_offset, transform_scale, union
import warnings

warnings.filterwarnings('ignore')  # for turfpy warnings
zeta = 0.07  # walls thickness of polygons
walls_thickness = 50  # walls thickness of non-polygons
walls_properties = {'height': 6, 'color': 'green'}
lintel_properties = {'height': 6, 'base_height': 4, 'color': 'green'}
include_original = False


def polygon_walls(poly):
    f = Feature(geometry=Polygon(poly['geometry']['coordinates']))
    outer = transform_scale(f, 1 + zeta, origin='centroid')
    inner = transform_scale(f, 1 - zeta, origin='centroid')

    walls_coords = inner['geometry']['coordinates'][0] + outer['geometry']['coordinates'][0] + [
        inner['geometry']['coordinates'][0][0]]

    walls_feature = {
        'type': 'Feature', 'properties': walls_properties, 'geometry': {
            'type': 'Polygon',
            'coordinates': [walls_coords],
            'tags': {
                'indoor': 'room'
            }
        }
    }
    return walls_feature


def line_string_walls(line_string):
    offset_top = line_offset(line_string['geometry'], distance=walls_thickness, unit='cen')
    offset_bot = line_offset(line_string['geometry'], distance=-walls_thickness, unit='cen')
    merged_coords = [
        offset_top['geometry']['coordinates'] +
        list(reversed(offset_bot['geometry']['coordinates'])) +
        [offset_top['geometry']['coordinates'][0]]
    ]

    if 'tags' in line_string['properties'] and line_string['properties']['tags'].get('indoor') == 'lintel':
        properties = lintel_properties
    else:
        properties = walls_properties

    return Feature(geometry=Polygon(coordinates=merged_coords), properties=properties)


def multi_line_string_walls(multi_line_string):
    polys = []
    for line_string_coords in multi_line_string['geometry']['coordinates']:
        line_string = Feature(geometry=LineString(coordinates=line_string_coords))
        poly = line_string_walls(line_string)
        polys.append(poly)

    unions = union(FeatureCollection(polys))
    unions['properties'] = walls_properties
    return unions


f = open('data/rooms-to-walls/input.geojson', encoding='utf-8')
data = json.load(f)

wallsFeatures = []
for feature in data['features']:
    featureType = feature['geometry']['type']

    if include_original:
        wallsFeatures.append(feature)

    if featureType == 'Polygon':
        walls = polygon_walls(feature)
        wallsFeatures.append(walls)
    elif featureType == 'LineString':
        walls = line_string_walls(feature)
        wallsFeatures.append(walls)
    elif featureType == 'MultiLineString':
        walls = multi_line_string_walls(feature)
        wallsFeatures.append(walls)

newGeojson = {'type': 'FeatureCollection', 'features': wallsFeatures}

with open('data/rooms-to-walls/output.geojson', 'w', encoding='utf-8') as f:
    json.dump(newGeojson, f, indent=4)

f.close()
