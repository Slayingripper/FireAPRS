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


viirsdownloader()

dataset = json.load(open('viirs.json'))
#grab the current time and date in zulu time
thedate = datetime.now().strftime('%d%H%M')
#add their callsign and the password for aprs here
#callsign = config.get('aprssend','callsign')
#password = config.get('aprssend','password')
callsign = "5B4ANU"
suffix = 11
#Password = "15540"
AIS = aprslib.IS("5b4anu", passwd="", port=14580)
AIS.connect()
#add the message to send here
comment = config.get('aprssend','comment')
symbol = config.get('aprssend','symbol')

#increment through all the messages in the json file
for message in dataset:
    #grab the latitude and longitude from the json file
    
    latitude = message['latitude']
    latitude = float(latitude) *100
    #to 2 decimal places and add 0s if needed
    latitude = round(latitude,1)
    latitude = format(latitude, '.1f')
    longitude = message['longitude']
    longitude = float(longitude) *100
    longitude = round(longitude,1)
    longitude = format(longitude, '.1f')
    #create the aprs message
    #AIS.sendall(f"{callsign}-{suffix}>APDR15,TCPIP*,qAC,T2STRAS:={latitude} N/0{longitude} E:{comment}")
    msg = "{}-{}>APDR15,TCPIP*,qAC,T2STRAS:={}N/0{}E{}{}".format(callsign, suffix, latitude, longitude, symbol, comment)
    AIS.sendall(msg)
    #print(my_packet)
    print(latitude)
    print(longitude)
    suffix = suffix + 1
    print(suffix)
    #send the message
    #AIS.send(msg)
    #wait for a second before sending the next message
    time.sleep(5)
#AIS.disconnect()
print("Done")

#add the location here (latitude and longitude)
#latitude = "" #example: "3440.80N"
#longitude = "" #example: "03256.50E"
#add the symbol here
#refer to http://www.aprs.org/symbols.html for a list of symbols

#AIS.sendall(f"{callsign}>APDR15,WIDE1-1:={latitude}N/{longitude}E{symbol}{comment}")


