import json
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature

f = open('data/input.geojson')
data = json.load(f)
area = Polygon(
    [
        [
            (51.534273819789206,
              35.7304129735428),
            (51.533968300502096,
              35.729250849295525),
            (51.53522238443253,
              35.729130384227204),
            (51.53572867353867,
              35.72989568862401),
            (51.535519174597965,
              35.730221649375224),
            (51.534273819789206,
              35.7304129735428),
        ]
    ]
)

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

with open('data/output.geojson', 'w') as f:
    json.dump(newGeojson, f)
  
f.close()

print(count)