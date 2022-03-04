import json
import requests
import os
import time

master = None
with open("master.json", "r") as f:
    try:
        master = json.loads(f.readline())
        if "ip" not in master:
            print("No master IP found")
    except ValueError:
        print("No master IP found decode again")

mission = None
with open("mission.json", "r") as f:
    try:
        mission = json.loads(f.readline())["id"]
    except Exception as e:
        print(e)

print("Master IP found " + master["ip"])

url = "http://" + master["ip"] + ":5000/mission_images/"

while True:
    images = os.listdir('data')
    # print(images)
    if len(images) == 0:
        time.sleep(5)
    else:
        for image in images:
            filename = image.split('.jpg')[0]
            coords, timestamp = filename.split("__")
            lat, lon, alt = coords.split("::")
            # print(lat, lon, alt)
            # print(timestamp)
            d = {"drone": mission, "lat": float(lat), "lon": float(lon), "alt": float(alt), "timestamp": timestamp}
            try:
                ret = requests.post(url, data=d, files={"image": open("data/"+image)})
                data = ret.json()
                if data["success"]:
                    print (filename, "upload success")
                    os.remove("data/"+image)
            except Exception as e:
                print(e)
                print("Trying after 5 seconds...")
                time.sleep(5)
        # break


# requests.post(url, data)

