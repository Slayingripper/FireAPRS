from geopy.geocoders import Nominatim
import news
from configparser import ConfigParser
import requests
import json
news.newsfinder()
config = ConfigParser()
config.read('config.ini')
authtoken = config.get('AQI','authtoken')
#get location name from lat and long
def getlocation(latitude,longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse(latitude+","+longitude)
    print(location)
    address = location.raw['address']
    print(address)
    city = address.get('city', '')
    url = "http://api.waqi.info/feed/"+city+"/?token="+authtoken
    #parse url and grab the aqi value
    response = requests.get(url)
    data = response.json()
    aqi = data['data']['aqi']
    iaqi= data['data']['iaqi']
    iaqit = data['data']['iaqi']['t']['v']
    print(aqi)
    print(iaqi)
    print(iaqit)
    return iaqit
