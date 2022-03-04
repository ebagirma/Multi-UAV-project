import math
def project(lat, lng):
  siny = math.sin(lat * math.pi / 180)
  siny = min(max(siny, -0.9999), 0.9999)
  return [256.0 * (0.5 + lng / 360), 256.0 * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))]


def windowContext(lat, lng, zoom):
  scale = 1 << zoom
  worldCoordinate = project(lat, lng)
  pixelCoordinate = [math.floor(worldCoordinate[0] * scale), math.floor(worldCoordinate[1] * scale)]
  tileCoordinate =  [math.floor(worldCoordinate[0] * scale / 256.0), math.floor(worldCoordinate[1] * scale / 256.0)]
  print zoom
  print worldCoordinate
  print pixelCoordinate
  print map(int, tileCoordinate)



windowContext(30.443671, -96.358410, 15)
