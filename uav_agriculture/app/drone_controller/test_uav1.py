################################################################################################
# @File DroneKitPX4.py
# Example usage of DroneKit with PX4
#
# @author Sander Smeets <sander@droneslab.com>
#
# Code partly based on DroneKit (c) Copyright 2015-2016, 3D Robotics.
################################################################################################

# Import DroneKit-Python
from dronekit import connect, Command, LocationGlobal, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time, sys, argparse, math
from mission_planner import Planner
import json
import socket                

################################################################################################
# Settings
################################################################################################

connection_string = '127.0.0.1:14541'
MAV_MODE_AUTO   = 4
# https://github.com/PX4/Firmware/blob/master/Tools/mavlink_px4.py


# Parse connection argument
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--connect", help="connection string")
args = parser.parse_args()

if args.connect:
    connection_string = args.connect


################################################################################################
# Init
################################################################################################

# Connect to the Vehicle
print("Connecting")
vehicle = connect(connection_string, wait_ready=True)

def PX4setMode(mavMode):
    vehicle._master.mav.command_long_send(vehicle._master.target_system, vehicle._master.target_component,
                                               mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                                               mavMode,
                                               0, 0, 0, 0, 0, 0)



def get_location_offset_meters(original_location, dNorth, dEast, alt):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned Location adds the entered `alt` value to the altitude of the `original_location`.
    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius=6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    return LocationGlobal(newlat, newlon, original_location.alt+alt)





################################################################################################
# Listeners
################################################################################################

home_position_set = False

#Create a message listener for home position fix
@vehicle.on_message('HOME_POSITION')
def listener(self, name, home_position):
    global home_position_set
    home_position_set = True

# with open("a.json") as f:
#     info = json.loads(''.join(f.readlines()))



################################################################################################
# Start mission example
################################################################################################

# wait for a home position lock
while not home_position_set:
    print("Waiting for home position...")
    time.sleep(1)



home = vehicle.location.global_relative_frame
print(home)

  
# Create a socket object 
s = socket.socket()          
  
# Define the port on which you want to connect 
port = 65432                
  
# connect to the server on local computer 
s.connect(('127.0.0.1', port)) 
  
# receive data from the server 
drone_id = s.recv(1024)
s.send(str(home.lat)+","+str(home.lon))
print(int(str(drone_id)))
# close the connection 

# def setHome():
#     if home_position_set:
#         return None
#     global home
#     return home

# Display basic vehicle state
print(" Type: %s" % vehicle._vehicle_type)
print(" Armed: %s" % vehicle.armed)
print(" System status: %s" % vehicle.system_status.state)
print(" GPS: %s" % vehicle.gps_0)
print(" Alt: %s" % vehicle.location.global_relative_frame.alt)

# Change to AUTO mode
PX4setMode(MAV_MODE_AUTO)
time.sleep(1)
robot_occupied = False

def fly_robot(path):
    def get_location_metres(original_location, dNorth, dEast):
        """
        Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the 
        specified `original_location`. The returned Location has the same `alt` value
        as `original_location`.

        The function is useful when you want to move the vehicle around specifying locations relative to 
        the current vehicle position.
        The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
        For more information see:
        http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
        """
        earth_radius=6378137.0 #Radius of "spherical" earth
        #Coordinate offsets in radians
        dLat = dNorth/earth_radius
        dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

        #New position in decimal degrees
        newlat = original_location.lat + (dLat * 180/math.pi)
        newlon = original_location.lon + (dLon * 180/math.pi)
        return LocationGlobal(newlat, newlon,original_location.alt)


    def get_distance_metres(aLocation1, aLocation2):
        """
        Returns the ground distance in metres between two LocationGlobal objects.

        This method is an approximation, and will not be accurate over large distances and close to the 
        earth's poles. It comes from the ArduPilot test code: 
        https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
        """
        dlat = aLocation2.lat - aLocation1.lat
        dlong = aLocation2.lon - aLocation1.lon
        return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5



    def distance_to_current_waypoint():
        """
        Gets distance in metres to the current waypoint. 
        It returns None for the first waypoint (Home location).
        """
        nextwaypoint = vehicle.commands.next
        if nextwaypoint==0:
            return None
        missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
        lat = missionitem.x
        lon = missionitem.y
        alt = missionitem.z
        targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
        distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
        return distancetopoint




    def download_mission():
        """
        Download the current mission from the vehicle.
        """
        cmds = vehicle.commands
        cmds.download()
        cmds.wait_ready() # wait until download is complete.



    # def adds_square_mission(aLocation, path):
    #     """
    #     Adds a takeoff command and four waypoint commands to the current mission. 
    #     The waypoints are positioned to form a square of side length 2*aSize around the specified LocationGlobal (aLocation).

    #     The function assumes vehicle.commands matches the vehicle mission state 
    #     (you must have called download at least once in the session and after clearing the mission)
    #     """	
    #     aSize = 10

    #     cmds = vehicle.commands

    #     print(" Clear any existing commands")
    #     cmds.clear() 
        
    #     print(" Define/add new commands.")
    #     # Add new commands. The meaning/order of the parameters is documented in the Command class. 
        
    #     #Add MAV_CMD_NAV_TAKEOFF command. This is ignored if the vehicle is already in the air.
    #     cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10))

    #     #Define the four MAV_CMD_NAV_WAYPOINT locations and add the commands
    #     point1 = get_location_metres(aLocation, aSize, -aSize)
    #     point2 = get_location_metres(aLocation, aSize, aSize)
    #     point3 = get_location_metres(aLocation, -aSize, aSize)
    #     point4 = get_location_metres(aLocation, -aSize, -aSize)
    #     cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point1.lat, point1.lon, 11))
    #     cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point2.lat, point2.lon, 12))
    #     cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point3.lat, point3.lon, 13))
    #     cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point4.lat, point4.lon, 14))
    #     #add dummy waypoint "5" at point 4 (lets us know when have reached destination)
    #     cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point4.lat, point4.lon, 14))    

    #     print(" Upload new commands to vehicle")
    #     cmds.upload()

    def adds_square_mission(aLocation, path):
        """
        Adds a takeoff command and four waypoint commands to the current mission. 
        The waypoints are positioned to form a square of side length 2*aSize around the specified LocationGlobal (aLocation).

        The function assumes vehicle.commands matches the vehicle mission state 
        (you must have called download at least once in the session and after clearing the mission)
        """	

        cmds = vehicle.commands

        print(" Clear any existing commands")
        cmds.clear() 
        
        print(" Define/add new commands.")
        # Add new commands. The meaning/order of the parameters is documented in the Command class. 
        wp = get_location_offset_meters(home, 0, 0, 10);
        # # print(wp)
        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1, 0, 0, 0, 0, wp.lat, wp.lon, wp.alt)
        cmds.add(cmd)
        


        # wp = get_location_offset_meters(wp, 10, 0, 0);
        # print(wp)
        # cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0, wp.lat, wp.lon, wp.alt)
        # cmds.add(cmd)
            
        #Add MAV_CMD_NAV_TAKEOFF command. This is ignored if the vehicle is already in the air.
        # cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1, 0, 0, 0, 0, 0, 0, a))
        # print(aLocation.lat, aLocation.lon, path[0])
        # Define the four MAV_CMD_NAV_WAYPOINT locations and add the commands
        i = 0
        for point in path:
            point1 = LocationGlobal(point[1], point[0], 10)
            cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0, point1.lat, point1.lon, 10))
            i += 10
        # print(" Upload new commands to vehicle")
        cmds.upload()


    def arm_and_takeoff(aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """

        print("Basic pre-arm checks")
        # Don't let the user try to arm until autopilot is ready
        while not vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)

            
        print("Arming motors")
        # Copter should arm in GUIDED mode
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True

        while not vehicle.armed:      
            print(" Waiting for arming...")
            time.sleep(1)

        print("Taking off!")
        vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)      
            if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
                print("Reached target altitude")
                break
            time.sleep(1)

    global robot_occupied
    if robot_occupied:
        return 

    robot_occupied = True


    # home = vehicle.location.global_relative_frame

    print('Create a new mission (for current location)')
    adds_square_mission(vehicle.location.global_frame, path)


    # From Copter 3.3 you will be able to take off using a mission item. Plane must take off using a mission item (currently).
    # arm_and_takeoff(10)

    print("Starting mission")
    # Reset mission set to first (0) waypoint
    # vehicle.commands.next=0

    # Set mode to AUTO to start mission
    # vehicle.mode = VehicleMode("AUTO")


    # Monitor mission. 
    # Demonstrates getting and setting the command number 
    # Uses distance_to_current_waypoint(), a convenience function for finding the 
    #   distance to the next waypoint.
    # while True:
    #     nextwaypoint=vehicle.commands.next
    #     print('Distance to waypoint (%s): %s' % (nextwaypoint, distance_to_current_waypoint()))

    #     # if nextwaypoint==3: #Skip to next waypoint
    #     #     print('Skipping to Waypoint 5 when reach waypoint 3')
    #     #     vehicle.commands.next = 5
    #     if nextwaypoint == len(path): #Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
    #         print("Exit 'standard' mission when start heading to final waypoint (5)")
    #         # break
    #     time.sleep(1)

    # print('Return to launch')

    # time.sleep(2)

    # # Arm vehicle
    vehicle.armed = True

    # # monitor mission execution
    nextwaypoint = vehicle.commands.next
    # print(nextwaypoint)
    while nextwaypoint < len(vehicle.commands):
        if vehicle.commands.next > nextwaypoint:
            display_seq = vehicle.commands.next+1
            print("Moving to waypoint %s" % display_seq)
            nextwaypoint = vehicle.commands.next
        time.sleep(1)

    vehicle.mode = VehicleMode("RTL")

    # # wait for the vehicle to land

    while vehicle.commands.next > 0:
        time.sleep(1)


    # # Disarm vehicle
    vehicle.armed = False
    # time.sleep(1)

    # Close vehicle object before exiting script
    vehicle.close()
    time.sleep(1)

    robot_occupied = False


# fly_robot(path)
# while True:
#     try:
#         pass
#     except KeyboardInterrupt:
#         break

while True:
    try:
        command = s.recv(2048)
        # print(command)
        if command != "":
            print("Received command...")
            # print(command)
            command.strip()
            cmds = command.split("\n")
            # print(cmds)
            path = []
            for cmd in cmds:
                if cmd == '': break
                latlon = cmd.split(",")
                if len(latlon) < 2: break
                latlon = (float(latlon[0]), float(latlon[1]))
                path += [latlon]
        # if path 
            print(path)
            fly_robot(path)
    except Exception as e:
        print(e)
        break


s.close()
