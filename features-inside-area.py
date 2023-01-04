import json
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature

f = open('data/features-inside-area/input.geojson', encoding='utf-8')
data = json.load(f)

fPoly = open('data/features-inside-area/polygon.txt', 'r')
lines = fPoly.readlines()
polygonCords = []
for line in lines:
    coords = line.split(',')
    polygonCords.append((float(coords[0]), float(coords[1])))

area = Polygon([polygonCords])

count = 0
newFeatures = []
for feature in data['features']:
    count += 1
    insert = True
    geometry = feature['geometry']
    coordinates = geometry['coordinates']

    if type(coordinates[0]) is float:
        point = Feature(geometry=Point((coordinates[0], coordinates[1])))
        if boolean_point_in_polygon(point, area) is False:
            insert = False
    elif type(coordinates[0]) is list:
        for coordinate in coordinates:
            if type(coordinate[0]) is float:
                point = Feature(geometry=Point((coordinate[0], coordinate[1])))
                if boolean_point_in_polygon(point, area) is False:
                    insert = False
                    break
            elif type(coordinate[0]) is list:
                for subCord in coordinate:
                    if type(subCord[0]) is float:
                        point = Feature(geometry=Point((subCord[0], subCord[1])))
                        if boolean_point_in_polygon(point, area) is False:
                            insert = False
                            break

    if insert:
        newFeatures.append(feature)

newGeojson = {}
newGeojson['type'] = 'FeatureCollection'
newGeojson['features'] = newFeatures

with open('data/features-inside-area/output.geojson', 'w', encoding='utf-8') as f:
    json.dump(newGeojson, f)
  
f.close()

print(count)