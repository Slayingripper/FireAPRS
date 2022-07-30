import json
import string
import aprslib
import time
from viirs import viirsdownloader
from datetime import datetime
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')
thedate = datetime.now().strftime('%d%H%M')
dataset = json.load(open('viirs.json'))
#grab the current time and date in zulu time
thedate = datetime.now().strftime('%d%H%M')
#add their callsign and the password for aprs here
callsign = config.get('aprssend','callsign')
password = config.get('aprssend','password')
suffix = 11
AIS = aprslib.IS(f"{callsign}", passwd=f"{password}", port=14580)
AIS.connect()
#add the message to send here
comment = config.get('aprssend','comment')
symbol = config.get('aprssend','symbol')
#increment through all the messages in the json file
for message in dataset:
    #grab the latitude and longitude from the json file
    latitude = message['latitude']
    #check if or statement is needed here
    print(latitude)
    #These latitude coordinates cause the aprs message to be sent to the wrong location
    #not sure why this happens but need to investigate more
    if latitude == "34.72600" or latitude == "34.72647":
        latitude = float(latitude) *100
        #to 2 decimal places and add 0s if needed
        latitude = round(latitude,1)
        latitude = format(latitude, '.1f')
        longitude = message['longitude']
        longitude = float(longitude) *100
        longitude = round(longitude,1)
        longitude = format(longitude, '.1f')
        #create the aprs message
        AIS.sendall(f"{callsign}-{suffix}>APDR15,TCPIP*,qAC,T2STRAS:={latitude} N/0{longitude} E:{comment}")
        print(latitude)
        print(longitude)
        suffix = suffix + 1
        print(suffix)
        time.sleep(5)
    else:
        print("Exiting program")
        break
        #exit program if latitude is 34.72600 or 34.72647      
    #wait for a second before sending the next message    
#AIS.disconnect()
print("Done")


