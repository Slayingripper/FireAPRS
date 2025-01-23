# main.py

import logging
import argparse
import sys
import time

from fire_aprs_cli.config import Config
from fire_aprs_cli.downloader import VIIRSDownloader
from fire_aprs_cli.aqi_fetcher import AQIFetcher
from fire_aprs_cli.news_fetcher import NewsFetcher
from fire_aprs_cli.aprs_sender import APRSSender
from fire_aprs_cli.scheduler import Scheduler

def setup_logging(logging_config):
    level = getattr(logging, logging_config['level'].upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logging_config['log_file']),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logging is set up.")

def process_fire_data(config, enable_aqi=True, enable_news=True):
    logging.info("Starting fire data processing...")

    # Initialize Downloader
    downloader = VIIRSDownloader(config['viirs'])
    downloader.run()
    logging.info("Data downloaded and processed.")

    # Initialize AQI Fetcher if enabled
    if enable_aqi:
        aqi_fetcher = AQIFetcher(config['aqi']['authtoken'])
    else:
        aqi_fetcher = None
        logging.info("AQI fetching is disabled.")

    # Initialize News Fetcher if enabled
    if enable_news:
        news_fetcher = NewsFetcher(config['newsfeed']['link'], config['newsfeed']['keyword'])
    else:
        news_fetcher = None
        logging.info("News fetching is disabled.")

    # Initialize APRS Sender
    aprs_sender = APRSSender(config['aprssend'])

    # Load VIIRS JSON data
    try:
        import json
        with open('viirs.json', 'r') as f:
            fire_data = json.load(f)
        logging.info(f"Loaded viirs.json with {len(fire_data)} records.")
    except Exception as e:
        logging.error(f"Failed to load 'viirs.json': {e}")
        aprs_sender.disconnect()
        return

    if not fire_data:
        logging.info("No fire data available to process. Sending no-fire APRS message.")
        aprs_sender.send_no_fire_message()
        aprs_sender.disconnect()
        logging.info("Fire data processing completed.")
        return

    # Iterate through each fire incident
    for idx, message in enumerate(fire_data, start=1):
        latitude = message.get('latitude')
        longitude = message.get('longitude')

        if latitude is None or longitude is None:
            logging.warning(f"Record {idx}: Missing latitude or longitude. Skipping.")
            continue

        # Fetch AQI Temperature if enabled
        if enable_aqi and aqi_fetcher:
            aqi_temp = aqi_fetcher.get_aqi_temperature(latitude, longitude)
            if aqi_temp is None:
                aqi_temp = "N/A"
                logging.warning(f"Record {idx}: AQI temperature not available.")
        else:
            aqi_temp = None  # AQI data not included

        # Fetch News Link if enabled
        if enable_news and news_fetcher:
            news_link = news_fetcher.find_news_link()
            if news_link == "No link found":
                logging.warning(f"Record {idx}: No news link found.")
        else:
            news_link = None  # News data not included

        # Compose APRS Message
        aprs_message_parts = []
        if aqi_temp is not None:
            aprs_message_parts.append(f"AQI Temp: {aqi_temp}°C")
        if news_link is not None:
            aprs_message_parts.append(f"News: {news_link}")

        # If no AQI and news data, provide minimal info
        if not aprs_message_parts:
            aprs_message_parts.append("Fire detected")

        aprs_message = ", ".join(aprs_message_parts)

        # Send APRS Message
        aprs_sender.send_message(latitude, longitude, aprs_message)
        logging.info(f"Record {idx}: APRS message sent.")

    # Disconnect APRS
    aprs_sender.disconnect()
    logging.info("Fire data processing completed.")

def main():
    parser = argparse.ArgumentParser(description="Fire APRS CLI Tool")
    parser.add_argument(
        '-i', '--interval',
        type=int,
        default=60,
        help='Interval in minutes between data fetches (default: 60)'
    )
    parser.add_argument(
        '--no-aqi',
        action='store_true',
        help='Disable fetching Air Quality Index (AQI) data'
    )
    parser.add_argument(
        '--no-news',
        action='store_true',
        help='Disable fetching news links'
    )
    args = parser.parse_args()

    # Load Configuration
    try:
        config_obj = Config()
        config = {
            'viirs': config_obj.get_viirs_config(),
            'aprssend': config_obj.get_aprs_config(),
            'aqi': config_obj.get_aqi_config(),
            'newsfeed': config_obj.get_newsfeed_config(),
            'logging': config_obj.get_logging_config(),
        }
    except Exception as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)

    # Setup Logging
    setup_logging(config['logging'])

    # Initial Run: Process Fire Data Immediately
    try:
        process_fire_data(
            config,
            enable_aqi=not args.no_aqi,
            enable_news=not args.no_news
        )
    except Exception as e:
        logging.error(f"Error during initial fire data processing: {e}")

    # Initialize Scheduler for Periodic Execution
    scheduler = Scheduler(
        interval_minutes=args.interval,
        job_func=process_fire_data,
        config=config,
        enable_aqi=not args.no_aqi,
        enable_news=not args.no_news
    )

    # Start Scheduler
    scheduler.start()

    # Keep the main thread alive.
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(None, None)

if __name__ == "__main__":
    main()
