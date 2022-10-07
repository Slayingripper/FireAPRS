from re import T
import news
from configparser import ConfigParser
news.newsfinder()
latitude = "51.481583"
longitude = "-3.179090"
config = ConfigParser()
config.read('config.ini')
authtoken = config.get('AQI','authtoken')
import geopy
#get location name from lat and long
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="geoapiExercises")
location = geolocator.reverse(latitude+","+longitude)
print(location)
address = location.raw['address']
print(address)
city = address.get('city', '')
state = address.get('state', '')
country = address.get('country', '')
code = address.get('country_code')
zipcode = address.get('postcode')
print('City : ',city)
print('State : ',state)
print('Country : ',country)
print('Zip Code : ', zipcode)

url = "http://api.waqi.info/feed/"+city+"/?token="+authtoken

#parse url and grab the aqi value
import requests
import json
response = requests.get(url)
data = response.json()
aqi = data['data']['aqi']
iaqi= data['data']['iaqi']
iaqit = data['data']['iaqi']['t']['v']
print(aqi)
print(iaqi)
print(iaqit)

