# fire_aprs_cli/aprs_sender.py

import logging
import time

import aprslib

class APRSSender:
    def __init__(self, config):
        self.callsign = config['callsign']
        self.password = config['password']
        self.comment = config['comment']
        self.symbol = config['symbol']
        self.port = config['port']
        self.suffix = 11  # Starting suffix

        try:
            self.ais = aprslib.IS(self.callsign, passwd=self.password, port=self.port)
            self.ais.connect()
            logging.info("Connected to APRS.")
        except Exception as e:
            logging.error(f"Failed to connect to APRS: {e}")
            raise

    def format_coordinates(self, latitude, longitude):
        # Convert decimal degrees to degrees and minutes
        lat_deg = int(latitude)
        lat_min = (latitude - lat_deg) * 60
        lon_deg = int(longitude)
        lon_min = (longitude - lon_deg) * 60

        # Format with leading zeros and two decimal places
        formatted_lat = f"{lat_deg:02d}{lat_min:05.2f}N" if lat_deg >= 0 else f"{abs(lat_deg):02d}{lat_min:05.2f}S"
        formatted_lon = f"{lon_deg:03d}{lon_min:05.2f}E" if lon_deg >= 0 else f"{abs(lon_deg):03d}{lon_min:05.2f}W"

        return formatted_lat, formatted_lon


    def send_message(self, latitude, longitude, message):
        try:
            formatted_lat, formatted_lon = self.format_coordinates(latitude, longitude)
            full_message = f"{self.callsign}-{self.suffix}>APDR15,TCPIP*,qAC,T2STRAS:={formatted_lat}/{formatted_lon}:{message}"
            self.ais.sendall(full_message)
            logging.info(f"Sent APRS message: {full_message}")
            self.suffix += 1
            time.sleep(5)  # Respecting APRS rate limits
        except Exception as e:
            logging.error(f"Failed to send APRS message: {e}")

    def send_no_fire_message(self):
        try:
            # Coordinates for a specific location or central point
            default_lat = "34.0000N"  # Replace with desired latitude
            default_lon = "31.0000E"  # Replace with desired longitude
            # Use APRS symbol 'T' for tree
            message = f"T No fires today"
            full_message = f"{self.callsign}-{self.suffix}>APDR15,TCPIP*,qAC,T2STRAS:={default_lat}/{default_lon}:{message}"
            self.ais.sendall(full_message)
            logging.info(f"Sent APRS no-fire message: {full_message}")
            self.suffix += 1
            time.sleep(5)  # Respecting APRS rate limits
        except Exception as e:
            logging.error(f"Failed to send no-fire APRS message: {e}")

    def disconnect(self):
        try:
            self.ais.disconnect()
            logging.info("Disconnected from APRS.")
        except AttributeError:
            logging.error("The 'IS' object does not have a 'disconnect' method.")
        except Exception as e:
            logging.error(f"Error disconnecting from APRS: {e}")
