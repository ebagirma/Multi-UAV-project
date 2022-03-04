import math
import datetime

def normalizePolygon(location_polygon, home):
    home = [float(home[0]), float(home[1])]
    diff = [location_polygon[0]['lat'] - home[0], location_polygon[0]['lng'] - home[1]]

    for i in range(len(location_polygon)):
        location_polygon[i]["lat"] -= diff[0]
        location_polygon[i]["lng"] -= diff[1]
    return location_polygon


TRIP_MAX_LENGTH = 500 # In meters


def get_distance_metres(aLocation1, aLocation2):
    dlat = aLocation2[0] - aLocation1[0]
    dlong = aLocation2[1] - aLocation1[1]
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


def chunkPath(locations):
    chunks = []
    if locations != []:
        chunks.append([locations[0]])
    left = TRIP_MAX_LENGTH
    for i in range(1, len(locations)):
        distance_between_cons = get_distance_metres(locations[i], locations[i - 1])  
        if left - distance_between_cons >= 0:
            chunks[-1].append(locations[i])
        else:
            chunks.append([locations[i]])
    return chunks