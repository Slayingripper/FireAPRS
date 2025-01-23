# fire_aprs_cli/config.py

import logging
from configparser import ConfigParser
from pathlib import Path

class Config:
    def __init__(self, config_path='config.ini'):
        self.config = self.load_config(config_path)
        self.validate_config()

    @staticmethod
    def load_config(config_path):
        config = ConfigParser()
        if not Path(config_path).is_file():
            raise FileNotFoundError(f"Configuration file '{config_path}' not found.")
        config.read(config_path)
        return config

    def validate_config(self):
        required_sections = {
            'viirs': ['url', 'filepath', 'latitude1', 'latitude2', 'longitude1', 'longitude2'],
            'aprssend': ['callsign', 'password', 'comment', 'symbol', 'port'],
            'AQI': ['authtoken'],
            'newsfeed': ['link', 'keyword'],
            'logging': ['level', 'log_file']
        }

        for section, keys in required_sections.items():
            if not self.config.has_section(section):
                raise ValueError(f"Missing section '{section}' in config.ini")
            for key in keys:
                if not self.config.has_option(section, key):
                    raise ValueError(f"Missing option '{key}' in section '{section}' of config.ini")

    def get_viirs_config(self):
        return {
            'url': self.config.get('viirs', 'url'),
            'filepath': self.config.get('viirs', 'filepath'),
            'latitude1': self.config.getfloat('viirs', 'latitude1'),
            'latitude2': self.config.getfloat('viirs', 'latitude2'),
            'longitude1': self.config.getfloat('viirs', 'longitude1'),
            'longitude2': self.config.getfloat('viirs', 'longitude2'),
        }

    def get_aprs_config(self):
        return {
            'callsign': self.config.get('aprssend', 'callsign'),
            'password': self.config.get('aprssend', 'password'),
            'comment': self.config.get('aprssend', 'comment'),
            'symbol': self.config.get('aprssend', 'symbol'),
            'port': self.config.getint('aprssend', 'port'),
        }

    def get_aqi_config(self):
        return {
            'authtoken': self.config.get('AQI', 'authtoken'),
        }

    def get_newsfeed_config(self):
        return {
            'link': self.config.get('newsfeed', 'link'),
            'keyword': self.config.get('newsfeed', 'keyword'),
        }

    def get_logging_config(self):
        return {
            'level': self.config.get('logging', 'level'),
            'log_file': self.config.get('logging', 'log_file'),
        }
