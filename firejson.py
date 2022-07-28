from flask import Flask,jsonify
import json
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')
hosti = config.get('firejson','host')
porti = config.get('firejson','port')


app = Flask(__name__)


with open('viirs.json') as f:
  fire = json.load(f)


@app.route("/fire", methods = ["GET"])
def getFire():
	#return jsonify(fire)
    return json.dumps(fire)
if __name__ == '__main__':
	app.run(port=porti,debug=True, host=hosti)
