import time, sys, argparse, math, datetime
import json
import os
import socket 

from threading import Thread


def accept_mission():
    # Create a socket object 
    s = socket.socket()          
    
    # Define the port on which you want to connect 
    port = 65432                
    
    # connect to the server on local computer 
    # TODO: Get connection from master
    master = None
    with open("master.json", "r") as f:
        try:
            master = json.loads(f.readline())
            if "ip" not in master:
                print("No master IP found")
        except ValueError:
            print("No master IP found decode again")

    print("Master IP found " + master["ip"])
    s.connect((master["ip"], port)) 
    print("Connected with master")

    # receive data from the server 
    drone_id = s.recv(1024)
    print(int(str(drone_id)))

    command = None
    while True:
        try:
            command = s.recv(4096)
            # print(command)
            if command != "":
                print("Received command...")
                break
        except Exception as e:
            print(e)    
            break
    
    print(command)
    if command:
        cmd = json.loads(command.strip())
        
        if os.path.exists("mission.json"):
            with open("mission.json", "r") as f:
                config = ''.join(f.readlines()).strip() 
                config = json.loads(config)
                # TODO: Check if the datetime stored here is more than a day old
                s.send(json.dumps({'success': False, 'message': 'Already have a mission.'}).encode('utf-8'))
        else:
            with open("mission.json", "w") as f:
                f.write(json.dumps(cmd).encode('utf-8'))
            s.send(json.dumps({'success': True, 'message': 'Mission successfully stored.'}).encode('utf-8'))

    s.close()

accept_mission()