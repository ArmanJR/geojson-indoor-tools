import json
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature
import random


f = open('data/add-polygon-heights/input.geojson', encoding='utf-8')
data = json.load(f)

count = 0
newFeatures = []
for feature in data['features']:
    count += 1
    insert = True
    geometry = feature['geometry']
    coordinates = geometry['coordinates']

    if geometry['type'] != 'Polygon':
        newFeatures.append(feature)
        continue

    feature['properties']['level'] = 0
    feature['properties']['height'] = 5
    feature['properties']['base_height'] = 0
    r = lambda: random.randint(0,255)
    feature['properties']['color'] = '#%02X%02X%02X' % (r(),r(),r())

    newFeatures.append(feature)


newGeojson = {}
newGeojson['type'] = 'FeatureCollection'
newGeojson['features'] = newFeatures

with open('data/add-polygon-heights/output.geojson', 'w', encoding='utf-8') as f:
    json.dump(newGeojson, f)
  
f.close()

print(count)