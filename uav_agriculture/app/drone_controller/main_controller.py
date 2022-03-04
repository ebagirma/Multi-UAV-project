import socket
import time, sys, argparse, math, datetime
from mission_planner import Planner
import json
sys.path.append('../../')

from app.models import Drone, Schedule, Path, LocationPoint

from threading import Thread
from socketserver import ThreadingMixIn 
from wifi_scanner import test_split
from controller_utils import normalizePolygon, chunkPath

home_set = False
path = None

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

conn = None
droneIpAddresses = {}
DRONES = 0


# Multithreaded Python server : TCP Server Socket Thread Pool
# TODO: Remove location polygon and insert the drone model here
class ClientThread(Thread): 
    def __init__(self, ip, port, drone): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
        self.drone = drone
        print("[+] New server socket thread started for " + ip + ":" + str(port) )
 
    def run(self): 
        # data = conn.recv(2048) 
        # print "Server received data:", data
        # # MESSAGE = raw_input("Multithreaded Python server : Enter Response from Server/Enter exit:")
        # if MESSAGE == 'exit':
        #     break
        global conn
        # conn.send(MESSAGE)  # echo
        # home_location = conn.recv(1024)
        # home = home_location.decode('utf-8').split(',')
        # print(home)
        # if len(home) != 2: return 
        drone_i = self.drone.uri
        schedule = Schedule.query.filter_by(drone_id=self.drone.id, status=0).first()
        path = Path.query.filter_by(schedule_id=schedule.id).first()
        points = LocationPoint.query.filter_by(path_id=path.id).order_by(LocationPoint.order)
        mypath = []
        for point in points:
            mypath.append([point.lon, point.lat])
        # drone_i = droneIpAddresses[self.ip]
        # mypath = path[drone_i*len(path)//DRONES: ((drone_i + 1) * (len(path)//DRONES + 1))]
        # print(mypath)
        chunkedPath = chunkPath(mypath)

        # print(drone_i, mypath)
        command = {"chunks": chunkedPath, "index": 0, "id": drone_i, "generated": str(datetime.datetime.now())}
        conn.send(json.dumps(command).encode("utf-8"))
        print("Sent the mission data to", str(drone_i))
        # for p in chunkedPath:
        #     toBe = str(p[0]) + "," + str(p[1]) + "\n"
        # conn.send(str(home[0]) + ","+str(home[1]) + "\n")

# TODO: Call this from request in flask app
def start_controller():
    i = 0
    # TODO: Replace this with get from database
    # with open("a.json", "r") as f:
    #     info = json.loads(''.join(f.readlines()))
    # TODO: Scan wifi and communicate the ip address of the master to the clients
    # wifi_client_info = scan_wifi()
    # print(wifi_client_info)
    interfaces = test_split()
    if len(interfaces) == 0:
        print("no interfaces to bind to")
        return

    # TODO: Make the user choose if there are multiple wifi interfaces
    HOST = str(interfaces[0][1])

    # TODO: Try to connect with the master / Clean up this code below
    # location_polygon = info['location_polygon']
    # home = [info['home']['lat'], info["home"]['lng']]
    # location_polygon = normalizePolygon(location_polygon, home)
    
    # # TODO: Get from request/database
    # p = Planner(self.location_polygon)

    # path = p.pretty()
    # print(path)
    # path = p.full_path(home[0], home[1])

    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    tcpServer.bind((HOST, PORT)) 
    threads = [] 
    

    global conn
    while True: 
        tcpServer.listen(4) 
        print("Multithreaded Python server : Waiting for connections from TCP clients..." )
        (conn, (ip,port)) = tcpServer.accept()
        drone = Drone.query.filter_by(network_address=ip).first()
        if drone:
            print("Accepted drone", str(drone.uri))
            if ip not in droneIpAddresses:
                conn.send(str(i).encode('utf-8'))
                newthread = ClientThread(ip, port, drone) 
                newthread.start() 
                threads.append(newthread) 
                droneIpAddresses[ip] = i
                i += 1
            else:
                for i in range(len(threads)):
                    if threads[i].ip == ip:
                        conn.send(str(i).encode('utf-8'))
                        threads[i] = ClientThread(ip, port, drone) 
                        threads[i].start() 
                        break

    for t in threads: 
        t.join() 
    
    with open('status.json', "w+") as f:
        config = {}
        try:
            config = json.loads(f.readline())
        except Exception:
            pass
        config["drones"] = 1
        config['controller'] = True
        f.write(json.dumps(config))



# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST, PORT))
#     s.listen()
#     conn, addr = s.accept()
#     with conn:
#         print('Connected by', addr)
#         conn.send(str(i).encode('utf-8'))
#     # conn.close()
#         home_location = conn.recv(1024)
#         home = home_location.decode('utf-8').split(',')
#         print(home)
#         with open("a.json") as f:
#             info = json.loads(''.join(f.readlines()))

#     # # home = setHome()
#         home = [float(home[0]), float(home[1])]
#         location_polygon = info['location_polygon']
#         diff = [location_polygon[0]['lat'] - home[0], location_polygon[0]['lng'] - home[1]]

#         for i in range(len(location_polygon)):
#             location_polygon[i]["lat"] -= diff[0]
#             location_polygon[i]["lng"] -= diff[1]
#         p = Planner(location_polygon)
#         # path = p.pretty()
#         # print(path)
#         path = p.full_path(home[0], home[1])
#         # print(path)
#         for p in path:
#             toBe = str(p[0]) + "," + str(p[1]) + "\n"
#             conn.send(toBe.encode("utf-8"))

        # while True:
        #     data = conn.recv(1024)
        #     if not data:
        #         break
        #     conn.sendall(data)
def main_controller():
    while True:
        status = {}
        try:
            with open("status.json", "r") as f:
                status = json.loads(f.readline())
        except IOError:
            pass
        except ValueError:
            pass
        global DRONES
        if status and "controller" in status and status["controller"]:
            if "drones" in status:
                DRONES = status["drones"]
            print('Controlling ' + str(DRONES) + " drones")
            start_controller()
        else:
            time.sleep(5)
    
main_controller()