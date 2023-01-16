import json
from turfpy.transformation import circle, intersect
from geojson import Point, Feature, FeatureCollection
from turfpy.measurement import center, point_to_line_distance

circle_radius_cm = 60
include_lintels = True
lintel_properties = {'height': 8, 'base_height': 5}

f = open('data/add-doors-to-rooms/input.geojson', encoding='utf-8')
data = json.load(f)

doors = [x for x in data['features'] if
         x['geometry']['type'] == 'Point' and x['properties']['tags'].get('door') == 'yes']


def cutLine(lineString, baseLine, sliceLine):
    coords = lineString['geometry']['coordinates']
    sliceCoords = sliceLine['geometry']['coordinates']
    firstSliceCoords = []
    secondSliceCoords = []
    found = False
    # look for the baseLine
    for lineStartPointIndex in range(len(coords[:-1])):
        line = Feature(geometry={'coordinates': [coords[lineStartPointIndex],
                                                 coords[lineStartPointIndex + 1]],
                                 'type': 'LineString'})
        if line['geometry'] == baseLine['geometry']:
            found = True
            firstSliceCoords += [coords[lineStartPointIndex], sliceCoords[0]]
            secondSliceCoords += [sliceCoords[1], coords[lineStartPointIndex + 1]]
        else:
            if found:
                secondSliceCoords += [coords[lineStartPointIndex], coords[lineStartPointIndex + 1]]
            else:
                firstSliceCoords += [coords[lineStartPointIndex], coords[lineStartPointIndex + 1]]

    return Feature(geometry={'coordinates': [firstSliceCoords, secondSliceCoords], 'type': 'MultiLineString'})


def cutRoom(roomLineString, intersections):
    coords = roomLineString['geometry']['coordinates']
    lines = []
    for lineStartPointIndex in range(len(coords[:-1])):
        line = Feature(geometry={'coordinates': [coords[lineStartPointIndex],
                                                 coords[lineStartPointIndex + 1]],
                                 'type': 'LineString'})
        intersectionFound = False
        for intersection in intersections:
            if intersection['onLine']['geometry'] == line['geometry']:
                intersectionFound = True
                newLine = cutLine(line, line, intersection['intersection'])
                lines += newLine['geometry']['coordinates']

        if not intersectionFound:
            lines += [line['geometry']['coordinates']]

    return Feature(geometry={'coordinates': lines, 'type': 'MultiLineString'})


final = []
for feature in data['features']:
    if feature['geometry']['type'] == 'Polygon' and feature['properties']['tags'].get('indoor') == 'room':
        # feature is a room
        roomBorder = Feature(geometry={'coordinates': feature['geometry']['coordinates'][0], 'type': 'LineString'})
        roomBorderML = Feature(
            geometry={'coordinates': [feature['geometry']['coordinates'][0]], 'type': 'MultiLineString'})
        roomBorderFC = FeatureCollection(features=[roomBorder])
        intersectionsToCutOut = []
        lintels = []
        room = Feature(geometry={'coordinates': feature['geometry']['coordinates'], 'type': 'Polygon'})
        # find its doors
        roomDoors = [x for x in doors if x['properties']['room_id'] == feature['properties']['id']]
        for door in roomDoors:
            centerCoord = Feature(
                geometry=Point((door['geometry']['coordinates'][0], door['geometry']['coordinates'][1])))
            # make a circle
            doorCircle = circle(center=centerCoord, radius=circle_radius_cm, steps=50, units='cen')
            # find intersecting points
            intersection = intersect([doorCircle, roomBorder])
            # make sure they have only 2 intersections
            if len(intersection['geometry']['coordinates']) != 2:
                continue
            # save intersection as door lintel
            lintel = intersection
            lintel['properties'] = lintel_properties
            lintels += [lintel]
            # cut room border from intersections
            # find which line contains the intersection line
            minLine = Feature(geometry={'coordinates': [roomBorder['geometry']['coordinates'][0],
                                                        roomBorder['geometry']['coordinates'][1]],
                                        'type': 'LineString'})
            minPointIndex = 0
            minDistance = 1000
            for pointIndex in range(len(roomBorder['geometry']['coordinates'][:-1])):
                line = Feature(geometry={'coordinates': [roomBorder['geometry']['coordinates'][pointIndex],
                                                         roomBorder['geometry']['coordinates'][pointIndex + 1]],
                                         'type': 'LineString'})

                intersectionCenterPoint = center(FeatureCollection([intersection]))
                distance = point_to_line_distance(intersectionCenterPoint, line, units='m')
                if distance < minDistance:
                    minLine = line
                    minPointIndex = pointIndex
                    minDistance = distance

            # minLine is the one containing the intersection
            # save all then cut out the intersection from minLine from the room border
            intersectionsToCutOut += [{'intersection': intersection, 'onLine': minLine}]

        slicedRoom = cutRoom(roomBorder, intersectionsToCutOut)
        final.append(slicedRoom)
        if include_lintels:
            final += lintels

newGeojson = {'type': 'FeatureCollection', 'features': final}
with open('data/add-doors-to-rooms/output.geojson', 'w', encoding='utf-8') as f:
    json.dump(newGeojson, f, indent=4)

f.close()
