# fire_aprs_cli/downloader.py

import logging
import os
from pathlib import Path

import pandas as pd
import requests

class VIIRSDownloader:
    def __init__(self, config):
        self.url = config['url']
        self.file_path = config['filepath']
        self.latitude_pos_1 = config['latitude1']
        self.latitude_pos_2 = config['latitude2']
        self.longitude_pos_1 = config['longitude1']
        self.longitude_pos_2 = config['longitude2']

    def remove_existing_file(self):
        try:
            if Path(self.file_path).is_file():
                Path(self.file_path).unlink()
                logging.info(f"Removed existing file at {self.file_path}.")
        except OSError as e:
            logging.error(f"Error removing file {self.file_path}: {e}")
            raise

    def download_file(self):
        try:
            response = requests.get(self.url, stream=True, timeout=60)
            response.raise_for_status()
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.info(f"Successfully downloaded file from {self.url} to {self.file_path}.")
        except requests.RequestException as e:
            logging.error(f"Failed to download file from {self.url}: {e}")
            raise

    def process_csv(self):
        try:
            df = pd.read_csv(
                self.file_path,
                usecols=['latitude', 'longitude'],
                dtype={'latitude': float, 'longitude': float}
            )
            logging.info(f"CSV file '{self.file_path}' loaded successfully with {len(df)} records.")
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            logging.error(f"Error reading CSV file '{self.file_path}': {e}")
            raise

        # Apply filtering
        filtered_df = df[
            (df['latitude'] <= self.latitude_pos_1) & 
            (df['latitude'] >= self.latitude_pos_2) &
            (df['longitude'] >= self.longitude_pos_1) & 
            (df['longitude'] <= self.longitude_pos_2)
        ]

        logging.info(f"Filtered data contains {len(filtered_df)} records.")
        print(filtered_df)  # Optional: Remove or redirect to logging if not needed

        # Save to JSON
        try:
            filtered_df.to_json(
                "viirs.json",
                orient="records",
                date_format="epoch",
                double_precision=10,
                force_ascii=True,
                date_unit="ms",
                default_handler=None
            )
            logging.info("Filtered data saved to 'viirs.json'.")
        except (TypeError, ValueError) as e:
            logging.error(f"Error saving filtered data to JSON: {e}")
            raise

    def run(self):
        logging.info("VIIRS Downloader started.")
        self.remove_existing_file()
        self.download_file()
        self.process_csv()
        logging.info("VIIRS Downloader finished successfully.")
