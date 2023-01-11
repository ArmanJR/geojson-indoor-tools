from turfpy.transformation import transform_scale
from geojson import Polygon, Feature
import json

zeta = 0.05

f = open('data/rooms-to-walls/input.geojson', encoding='utf-8')
data = json.load(f)

wallsFeatures = []
for feature in data['features']:
    if feature['geometry']['type'] != 'Polygon':
        wallsFeatures.append(feature)
        continue

    f = Feature(geometry=Polygon(feature['geometry']['coordinates']))
    outer = transform_scale(f, 1 + zeta, origin='centroid')
    inner = transform_scale(f, 1 - zeta, origin='centroid')

    walls = inner['geometry']['coordinates'][0] + outer['geometry']['coordinates'][0] + [
        inner['geometry']['coordinates'][0][0]]

    wallsFeature = {
        'type': 'Feature', 'properties': {
            'height': 5,
            'color': 'green'
        }, 'geometry': {
            'type': 'Polygon',
            'coordinates': [walls]
        }
    }

    wallsFeatures.append(wallsFeature)

newGeojson = {'type': 'FeatureCollection', 'features': wallsFeatures}

with open('data/rooms-to-walls/output.geojson', 'w', encoding='utf-8') as f:
    json.dump(newGeojson, f)

f.close()
