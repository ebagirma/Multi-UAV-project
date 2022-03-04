import json
from mission_planner import Planner
from controller_utils import normalizePolygon

info = {}
with open("a.json", "r") as f:
    info = json.loads(''.join(f.readlines()))
location_polygon = info['location_polygon']
locs = normalizePolygon(location_polygon, [41.9066063687059, -94.2415092741269])
print(locs)
p = Planner(locs, d=0.15, m=float("inf"))
path = p.full_path()
p.pretty()
