import subprocess
import json
from flask import Flask, escape, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

with open("a.json") as f:
    info = json.loads(''.join(f.readlines()))
# subproces s.call(['droneit-sitl', 'copter', '--home=9.0834701,38.7993882,0,1'])
# print "Running dronekit-sitl at home location", info['home']
# out = subprocess.Popen(['dronekit-sitl', 'copter', '--home='+info['home']], stdout=subprocess.PIPE,  stderr=subprocess.STDOUT)
# print(out.communicate())
@app.route('/')
def main():
    return json.dumps(info)


