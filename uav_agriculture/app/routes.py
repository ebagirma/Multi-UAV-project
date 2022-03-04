import subprocess
import json
import os
from app import app, db
from app.models import Farm, Drone, LocationPoint, Crop, Schedule, Path, CollectedImage, SurveyParameters, User
from flask import request, Response
from utils import AlchemyEncoder
from drone_controller.wifi_scanner import broadcastMasterIP
from drone_controller.mission_planner import Planner
from datetime import datetime
from drone_controller.controller_utils import chunkPath, normalizePolygon

# subproces s.call(['droneit-sitl', 'copter', '--home=9.0834701,38.7993882,0,1'])
# print "Running dronekit-sitl at home location", info['home']
# out = subprocess.Popen(['dronekit-sitl', 'copter', '--home='+info['home']], stdout=subprocess.PIPE,  stderr=subprocess.STDOUT)
# print(out.communicate())
from flask import send_from_directory

@app.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               os.path.join(folder, filename))


@app.route('/')
def main():
    with open("app/drone_controller/a.json") as f:
        info = json.loads(''.join(f.readlines()))
    return Response(json.dumps(info), 200)

@app.route('/farms/')
def list_farms():
    farms = Farm.query.all()
    return Response(json.dumps(farms, cls=AlchemyEncoder), 200)

@app.route('/farms/<int:id>/')
def getFarmDetails(id):
    farm = Farm.query.filter_by(id=id).first()
    crops = Crop.query.filter_by(farm_id=farm.id).all()
    plants = {}
    for crop in crops:
        plants[crop.id] = crop.plant
    return Response(json.dumps({"farm": farm, "crops" : crops, "plants": plants}, cls=AlchemyEncoder), 200)

@app.route('/create/farm/', methods=['POST'])
def create_farm():
    farm = Farm(name=request.json['name'], description=request.json['description'], city=request.json['city'], owner_id=1)
    db.session.add(farm)
    db.session.commit()
    sp = SurveyParameters(farm_id=farm.id, slope=1.0, altitude=2, speed=10, spacing=0.5)
    db.session.add(sp)
    db.session.commit()
    return Response(json.dumps(farm, cls=AlchemyEncoder), 200)

@app.route('/drones/')
def list_drones():
    drones = Drone.query.all()
    return Response(json.dumps(drones, cls=AlchemyEncoder), 200)

@app.route('/create/drone/', methods=['POST'])
def create_drone():
    # uri = db.Column(db.String(256), nullable=False)
    # description = db.Column(db.String(1000))
    # network_address = db.Column(db.String(256))
    # mac_address = db.Column(db.String(256))
    # stream_address = db.Column(db.String(256))
    # farm_id = db.Column(db.Integer, db.ForeignKey("farm.id"), nullable=False)
    drone = Drone(uri=request.json['uri'], description=request.json['description'], 
                network_address=request.json['network_address'], mac_address=request.json['mac_address'],
                stream_address=request.json['stream_address'], farm_id=request.json['farm_id'])
    db.session.add(drone)
    db.session.commit()
    return Response(json.dumps(drone, cls=AlchemyEncoder), 200)

@app.route('/set/locations/', methods=['POST'])
def set_locations():
    data = request.get_json()
    farm_id = data['farm_id']
    LocationPoint.query.filter_by(farm_id=farm_id, path_id=None).delete(synchronize_session=False)
    # print(data)
    i = 1
    lps = []
    for lp in data['locations']:
        lp = LocationPoint(lat=lp[1], lon=lp[0], order=i, farm_id=farm_id)
        i += 1
        db.session.add(lp)
        lps.append(lp)
        if i == len(data["locations"]):
            break
    db.session.commit()

    return Response(get_locs(lps, farm_id), 200)

@app.route('/set/sps/', methods=['POST'])
def set_sps():
    data = request.get_json()
    owner_id = data['owner_id']
    user = User.query.get(owner_id)
    farms = Farm.query.filter_by(owner_id=user.id)
    for farm in farms:
        sp = SurveyParameters.query.filter_by(farm_id=farm.id).first()
        sp.slope = data["slope"]
        sp.spacing = data["spacing"]
        sp.speed = data["speed"]
        sp.altitude = data["altitude"]
        db.session.commit()
    return Response(json.dumps(sp, cls=AlchemyEncoder), 200)


def get_locs(lps, farm_id):
    if len(lps) > 0:
        data = {"farm_id": farm_id, "location_polygon": [], "home": { "lat": lps[0].lat, "lon": lps[0].lon }}
    else:
        data = {"farm_id" : farm_id, "location_polygon": [], "home" : {"lat" : 0.0, "lon": 0.0}}
    for lp in lps:
        data["location_polygon"].append({"lat": lp.lat, "lon": lp.lon, "order": lp.order})
    return json.dumps(data)


@app.route('/get/locations/<int:farm_id>/')
def get_locations(farm_id):
    lps = LocationPoint.query.filter_by(farm_id=farm_id, path_id=None).all()
    lps = sorted(lps, key=lambda lp: lp.order)
    return Response(get_locs(lps, farm_id), 200)

@app.route('/get/drones/<int:farm_id>/')
def get_drones(farm_id):
    lps = Drone.query.filter_by(farm_id=farm_id).all()
    return Response(json.dumps(lps, cls=AlchemyEncoder), 200)

@app.route('/get/sps/<int:farm_id>/')
def get_sps(farm_id):
    sp = SurveyParameters.query.filter_by(farm_id=farm_id).first()
    return Response(json.dumps(sp, cls=AlchemyEncoder), 200)

@app.route('/get/pictures/<int:drone_id>/')
def get_pictures(drone_id):
    cis = CollectedImage.query.filter_by(drone_id=drone_id).all()
    return Response(json.dumps(cis, cls=AlchemyEncoder), 200)


@app.route('/start/<int:id>/')
def start_cont(id):
    farm = Farm.query.filter_by(id=id).first()
    drones = Drone.query.filter_by(farm_id=farm.id).order_by(Drone.uri)
    config = {}
    with open("app/drone_controller/status.json", "r") as f:
        try:
            config = json.loads(f.readline())
        except Exception:
            pass
    config["drones"] = drones.count()
    config['controller'] = True
    with open("app/drone_controller/status.json", "w") as f:
        f.write(json.dumps(config))
    with open("app/drone_controller/a.json", "w") as f:
        # locations = {}
        # try:
        #     locations = json.loads(''.join(f.readlines()))
        # except Exception as e:
        #     print(e)
        locations = LocationPoint.query.filter_by(farm_id=farm.id)
        locs = {'location_polygon': []}
        for location in locations:
            locs["location_polygon"].append({'lat': location.lat, 'lng': location.lon})
        # config["drones"] = drones
        # config['controller'] = True
        if len(locs) > 0:
            locs["home"] = locs["location_polygon"][0]
        else:
            locs["home"] = ''
        f.write(json.dumps(locs))

        location_polygon = locs['location_polygon']
        home = [locs['home']['lat'], locs["home"]['lng']]
        location_polygon = normalizePolygon(location_polygon, home)

        planner = Planner(location_polygon)
        path = planner.full_path(home[0], home[1])
        dronePaths = {}
        sp = SurveyParameters.query.filter_by(farm_id=farm.id).first()
        for i, drone in enumerate(drones):
            scheduled = Schedule.query.filter_by(status=0, drone_id=drone.id).first()
            mypath = path[i*len(path)//drones.count(): ((i + 1) * (len(path)//drones.count() + 1))]
            dronePaths[drone.id] = mypath
            if not scheduled:
                # chunkedPath = chunkPath(mypath)
                schedule = Schedule(drone_id=drone.id, status=0, frequency=datetime.now(), slope=sp.slope, altitude=sp.altitude, spacing=sp.spacing, speed=sp.speed)
                db.session.add(schedule)
                db.session.commit()

                p = Path(schedule_id=schedule.id, timestamp=datetime.now())
                db.session.add(p)
                db.session.commit()
                for i, point in enumerate(mypath):
                    lp = LocationPoint(lat=point[1], lon=point[0], order=i, path_id=p.id)
                    db.session.add(lp)
                db.session.commit()
            else:
                p  = Path.query.filter_by(schedule_id=scheduled.id).first()
                ls = LocationPoint.query.filter_by(path_id=p.id)
                pps = []
                for l in ls:
                    pps.append([l.lon, l.lat])
                dronePaths[drone.id] = pps
        return Response(json.dumps({"success": True, "path": dronePaths}), 200)
    return Response(json.dumps({"success": False}), 400)

@app.route('/scan/<int:id>/')
def start_scan(id):
    farm = Farm.query.filter_by(id=id).first()
    # TODO: Make this faster using dictionaries
    drones_all = Drone.query.filter_by(farm_id=farm.id)
    drones = broadcastMasterIP()
    toSend = []
    check = {}
    for drone in drones:
        drPrev = Drone.query.filter_by(farm_id=farm.id, mac_address=drone['mac']).first()
        if drPrev == None:
            dr = Drone(uri="resource://drone"+str(drones_all.count()), description='', 
                    network_address=drone['ip'], mac_address=drone['mac'],
                    stream_address=drone['ip'], farm_id=farm.id)
            db.session.add(dr)
            db.session.commit()
            toSend.append(dr)
            check[dr.id] = 1
        else:
            drPrev.network_address = drone["ip"]
            drPrev.stream_address = drone["ip"]
            db.session.commit()
            toSend.append(drPrev)
            check[drPrev.id] = 1
    for drone in drones_all:
        if drone.id not in check:
            toSend.append(drone)
    return Response(json.dumps({"success": True, "drones": toSend}, cls=AlchemyEncoder), 200)


@app.route('/mission_images/', methods=["POST"])
def mission_images():
    file = request.files["image"]
    drone_id = request.form["drone"]
    drone = Drone.query.filter_by(uri=drone_id).first()
    if drone:
        if file.filename == '':
            return json.dumps({"error": "No file sent"})
        if file:
            filename = file.filename
            coordinates = {}
            coordinates["lat"] = request.form["lat"]
            coordinates["lon"] = request.form["lon"]
            coordinates["alt"] = request.form["alt"]
            timestamp = request.form["timestamp"]
            generated = datetime.fromtimestamp(float(timestamp))
            # print(coordinates)
            # print(lat, lon, alt)
            # print(timestamp)
            ci = CollectedImage(image=str(drone.id) + "/" + filename, drone_id=drone.id, timestamp=generated, details=json.dumps({"coordinates": coordinates}))
            db.session.add(ci)
            if not os.path.exists(app.config['UPLOAD_FOLDER'] + str(drone.id) +"/"):
                os.mkdir(app.config["UPLOAD_FOLDER"] + str(drone.id) + "/")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'] + str(drone.id)+ "/", filename))
            db.session.commit()
        return Response(json.dumps({"success": True, "message": "Successfully saved"}), 200)
    return Response(json.dumps({"success": False, "message": "Error"}), 400)


@app.route('/update/schedule/<int:drone_id>/', methods=["POST"])
def update_schedule(drone_id):
    drone = Drone.query.get(drone_id)
    schedule = Schedule.query.filter_by(drone_id=drone.id, status=0).first()
    path = Path.query.filter_by(schedule_id=schedule.id).first()
    dels = LocationPoint.query.filter_by(farm_id=None, path_id=path.id).delete(synchronize_session='evaluate')
    print(dels)
    data = request.get_json()
    points = data['lps']
    for i, point in enumerate(points):
        lp = LocationPoint(lat=point[1], lon=point[0], order=i, path_id=path.id)
        try:
            db.session.add(lp)
        except:
            pass
    db.session.commit()
    return Response(json.dumps({"success": True, "message": "Successfully saved"}), 200)

