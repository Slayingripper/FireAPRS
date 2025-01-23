# fire_aprs_cli/aqi_fetcher.py

import logging

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderUnavailable
import requests

class AQIFetcher:
    def __init__(self, authtoken, user_agent="fire_aprs_cli"):
        self.authtoken = authtoken
        self.geolocator = Nominatim(user_agent=user_agent)
        self.session = requests.Session()

    def get_location_name(self, latitude, longitude):
        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True, timeout=10)
            if not location:
                logging.warning(f"No location found for coordinates: {latitude}, {longitude}")
                return None
            address = location.raw.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village') or address.get('hamlet')
            if not city:
                logging.warning(f"City not found in address for coordinates: {latitude}, {longitude}")
                return None
            logging.info(f"Resolved city '{city}' for coordinates: {latitude}, {longitude}")
            return city
        except (GeocoderServiceError, GeocoderUnavailable) as e:
            logging.error(f"Geocoding error for coordinates {latitude}, {longitude}: {e}")
            return None

    def fetch_aqi(self, city):
        url = f"http://api.waqi.info/feed/{city}/?token={self.authtoken}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('status') != 'ok':
                logging.error(f"API response error for city '{city}': {data.get('data')}")
                return None
            aqi = data['data'].get('aqi')
            iaqi = data['data'].get('iaqi', {})
            iaqit = iaqi.get('t', {}).get('v')
            logging.info(f"AQI for {city}: {aqi}, Temperature: {iaqit}")
            return iaqit
        except requests.RequestException as e:
            logging.error(f"HTTP request failed for city '{city}': {e}")
            return None
        except (KeyError, TypeError, ValueError) as e:
            logging.error(f"Error parsing API response for city '{city}': {e}")
            return None

    def get_aqi_temperature(self, latitude, longitude):
        city = self.get_location_name(latitude, longitude)
        if not city:
            logging.error(f"Could not determine city for coordinates: {latitude}, {longitude}")
            return None
        iaqit = self.fetch_aqi(city)
        if iaqit is None:
            logging.error(f"Could not retrieve AQI temperature for city: {city}")
        return iaqit

    def __del__(self):
        self.session.close()
