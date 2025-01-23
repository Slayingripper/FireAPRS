# FireAPRS

![APRS World](icon/aprs_world_5in.png)

FireAPRS utilizes NASA's VIIRS satellite data to monitor and plot the locations of active fires within a specified geographical area on the APRS network over the past 24 hours. This tool offers flexibility through its configuration file, allowing users to define any geographical "box" of interest and customize various operational parameters.

## Table of Contents

- [FireAPRS](#fireaprs)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [Configuration File Structure](#configuration-file-structure)
      - [**Section Descriptions:**](#section-descriptions)
    - [Environment Variables (Recommended for Sensitive Data)](#environment-variables-recommended-for-sensitive-data)
  - [Usage](#usage)
    - [Command-Line Arguments](#command-line-arguments)
    - [Running the Tool](#running-the-tool)
    - [Example APRS Messages](#example-aprs-messages)
  - [Environment Variables](#environment-variables)
  - [Logging](#logging)
  - [Troubleshooting](#troubleshooting)
    - [**1. Invalid Uncompressed Location Error on aprs.fi**](#1-invalid-uncompressed-location-error-on-aprsfi)
    - [**2. API Response Error for AQI**](#2-api-response-error-for-aqi)
    - [**3. Empty RSS Feed Warning**](#3-empty-rss-feed-warning)
    - [**4. APRS Disconnect Error**](#4-aprs-disconnect-error)
  - [License](#license)

## Features

- **Fire Detection:** Automatically downloads and processes VIIRS satellite data to identify active fires within the defined geographical area.
- **APRS Integration:** Sends APRS messages to plot fire locations on the APRS network, providing real-time fire monitoring.
- **Optional AQI and News Fetching:** 
  - **Air Quality Index (AQI):** Fetches AQI data for fire locations to provide additional environmental context.
  - **News Links:** Retrieves relevant news articles related to fire incidents.
- **Customizable Messages:** Sends tailored APRS messages based on available data, including a default "No fires today" message when no active fires are detected.
- **Configurable Scheduling:** Allows users to set the interval (in minutes) for periodic data fetching and APRS messaging.
- **Flexible Configuration:** Easily define the geographical area of interest and adjust operational parameters via the `config.ini` file.
- **Robust Logging:** Maintains detailed logs for monitoring and troubleshooting purposes.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/FireAPRS.git
   cd FireAPRS
   ```

2. **Create a Virtual Environment (Optional but Recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create Necessary Directories:**

   ```bash
   mkdir -p data
   ```

## Configuration

FireAPRS is configured via the `config.ini` file located in the project root directory. This file defines various settings, including APRS credentials, VIIRS data source, AQI API token, news feed URL, and logging preferences.

### Configuration File Structure

```ini
[aprssend]
callsign = YOUR_CALLSIGN
password = YOUR_PASSWORD
comment = Fire Alert!!!
symbol = T  # 'T' represents a tree in APRS symbols
port = 14580

[viirs]
url = https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_Global_24h.csv
filepath = data/SUOMI_VIIRS_C2_Global_24h.csv
latitude1 = 35.844535  # Top-left latitude
latitude2 = 34.511083  # Bottom-right latitude
longitude1 = 31.816406  # Top-left longitude
longitude2 = 34.661865  # Bottom-right longitude

[AQI]
authtoken = YOUR_AQI_AUTHTOKEN

[newsfeed]
link = YOUR_RSS_FEED_URL
keyword = fire

[logging]
level = INFO
log_file = fire_aprs.log
```

#### **Section Descriptions:**

- **[aprssend]:** APRS server connection details.
  - `callsign`: Your APRS callsign.
  - `password`: Your APRS password.
  - `comment`: Comment field in APRS packets.
  - `symbol`: APRS symbol representing the data (default is 'T' for tree).
  - `port`: Port number for APRS connection (default is `14580`).

- **[viirs]:** VIIRS satellite data settings.
  - `url`: URL to download the latest VIIRS active fire data.
  - `filepath`: Local path to save the downloaded CSV file.
  - `latitude1` & `longitude1`: Coordinates for the top-left corner of the geographical area.
  - `latitude2` & `longitude2`: Coordinates for the bottom-right corner of the geographical area.

- **[AQI]:** Air Quality Index settings.
  - `authtoken`: Your AQI API token from [World Air Quality Index (WAQI) API](https://aqicn.org/data-platform/token/#/).

- **[newsfeed]:** News feed settings.
  - `link`: URL to the RSS feed for fetching news related to fires.
  - `keyword`: Keyword to filter relevant news articles (e.g., `fire`).

- **[logging]:** Logging preferences.
  - `level`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
  - `log_file`: Path to the log file.

### Environment Variables (Recommended for Sensitive Data)

To enhance security, it's advisable to store sensitive information like APRS passwords and AQI tokens as environment variables instead of plain text in `config.ini`.

1. **Modify `config.ini` to Use Placeholders:**

   ```ini
   [aprssend]
   callsign = YOUR_CALLSIGN
   password = ${APRS_PASSWORD}
   comment = Fire Alert!!!
   symbol = T
   port = 14580

   [AQI]
   authtoken = ${AQI_AUTHTOKEN}
   ```

2. **Update `config.py` to Read Environment Variables:**

   ```python
   # fire_aprs_cli/config.py

   import os
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

           # Additional validation for coordinates
           latitude_limits = (-90.0, 90.0)
           longitude_limits = (-180.0, 180.0)

           for coord, (min_val, max_val) in [
               ('latitude1', latitude_limits),
               ('latitude2', latitude_limits),
               ('longitude1', longitude_limits),
               ('longitude2', longitude_limits)
           ]:
               value = self.config.getfloat('viirs', coord)
               if not (min_val <= value <= max_val):
                   raise ValueError(f"Invalid value for '{coord}': {value}. Must be between {min_val} and {max_val}.")

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
               'password': os.getenv('APRS_PASSWORD', self.config.get('aprssend', 'password')),
               'comment': self.config.get('aprssend', 'comment'),
               'symbol': self.config.get('aprssend', 'symbol'),
               'port': self.config.getint('aprssend', 'port'),
           }

       def get_aqi_config(self):
           return {
               'authtoken': os.getenv('AQI_AUTHTOKEN', self.config.get('AQI', 'authtoken')),
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
   ```

3. **Set Environment Variables:**

   ```bash
   export APRS_PASSWORD=your_aprs_password
   export AQI_AUTHTOKEN=your_aqi_token
   ```

   *Ensure these environment variables are set in your shell or defined in your deployment environment.*

## Usage

FireAPRS can be executed via the command line, offering flexibility through various flags to enable or disable certain features.

### Command-Line Arguments

- `-i`, `--interval`:  
  **Description:** Set the interval in minutes between data fetches.  
  **Default:** `60` minutes.

- `--no-aqi`:  
  **Description:** Disable fetching Air Quality Index (AQI) data.  
  **Default:** Enabled.

- `--no-news`:  
  **Description:** Disable fetching news links related to fires.  
  **Default:** Enabled.

### Running the Tool

1. **Basic Execution with All Features Enabled:**

   ```bash
   python main.py
   ```

   *This command fetches fire data, AQI information, and news links at the default interval of 60 minutes.*

2. **Disable AQI Fetching:**

   ```bash
   python main.py --no-aqi
   ```

   *Fetches fire data and news links without retrieving AQI information.*

3. **Disable News Fetching:**

   ```bash
   python main.py --no-news
   ```

   *Fetches fire data and AQI information without retrieving news links.*

4. **Disable Both AQI and News Fetching:**

   ```bash
   python main.py --no-aqi --no-news
   ```

   *Fetches only fire data and sends minimal APRS messages.*

5. **Set a Custom Interval (e.g., Every 5 Minutes):**

   ```bash
   python main.py --interval 5
   ```

6. **Combine Flags (e.g., Disable News and Set Interval to 30 Minutes):**

   ```bash
   python main.py --no-news --interval 30
   ```

### Example APRS Messages

- **With AQI and News Enabled:**

  ```
  5B4ANU-12>APDR15,TCPIP*,qAC,T2STRAS:=3443.56N/03318.99E:AQI Temp: 25°C, News: http://newslink.com/article
  ```

- **Without AQI and News:**

  ```
  5B4ANU-11>APDR15,TCPIP*,qAC,T2STRAS:=3400.00N/3100.00E:Fire detected
  ```

- **No Fires Detected:**

  ```
  5B4ANU-11>APDR15,TCPIP*,qAC,T2STRAS:=3400.00N/3100.00E:T No fires today
  ```

*Ensure that the coordinates are correctly formatted to avoid invalid location errors on APRS clients.*

## Environment Variables

For enhanced security, sensitive information such as APRS passwords and AQI tokens should be stored as environment variables.

- **Set Environment Variables:**

  ```bash
  export APRS_PASSWORD=your_aprs_password
  export AQI_AUTHTOKEN=your_aqi_token
  ```

- **Access in `config.ini`:**

  ```ini
  [aprssend]
  password = ${APRS_PASSWORD}

  [AQI]
  authtoken = ${AQI_AUTHTOKEN}
  ```

*Ensure these environment variables are set in your shell or deployment environment before running FireAPRS.*

## Logging

FireAPRS maintains detailed logs to assist with monitoring and troubleshooting.

- **Log File:** `fire_aprs.log`  
  *Located in the project root directory.*

- **Log Levels:**  
  - `DEBUG`: Detailed information, typically of interest only when diagnosing problems.
  - `INFO`: Confirmation that things are working as expected.
  - `WARNING`: An indication that something unexpected happened.
  - `ERROR`: Due to a more serious problem, the software has not been able to perform some function.
  - `CRITICAL`: A serious error, indicating that the program itself may be unable to continue running.

*Configure the desired log level in the `[logging]` section of `config.ini`.*

## Troubleshooting

### **1. Invalid Uncompressed Location Error on aprs.fi**

**Issue:**  
APRSSF displays the message:  
`Fire detected [Invalid uncompressed location]`

**Cause:**  
Incorrect formatting of latitude and longitude coordinates in APRS messages.

**Solution:**  
Ensure that the `format_coordinates` method in `aprs_sender.py` correctly converts decimal degrees to the `DDMM.mmN/S` and `DDDMM.mmE/W` formats.

**Verification Steps:**

1. **Check `format_coordinates` Method:**

   Ensure it correctly converts coordinates. Example implementation:

   ```python
   def format_coordinates(self, latitude, longitude):
       # Convert decimal degrees to degrees and minutes
       lat_deg = int(latitude)
       lat_min = (latitude - lat_deg) * 60
       lon_deg = int(longitude)
       lon_min = (longitude - lon_deg) * 60

       # Determine N/S and E/W
       lat_direction = 'N' if lat_deg >= 0 else 'S'
       lon_direction = 'E' if lon_deg >= 0 else 'W'

       # Absolute degrees for formatting
       lat_deg_abs = abs(lat_deg)
       lon_deg_abs = abs(lon_deg)

       # Format with leading zeros and two decimal places
       formatted_lat = f"{lat_deg_abs:02d}{lat_min:05.2f}{lat_direction}"
       formatted_lon = f"{lon_deg_abs:03d}{lon_min:05.2f}{lon_direction}"

       return formatted_lat, formatted_lon
   ```

2. **Run the Tool and Verify APRS Messages:**

   After correcting, run FireAPRS and check aprs.fi for valid location markers.

### **2. API Response Error for AQI**

**Issue:**  
```
API response error for city 'Mari': Invalid key
Could not retrieve AQI temperature for city: Mari
```

**Cause:**  
Invalid or expired AQI API key.

**Solution:**  

1. **Obtain a Valid AQI API Key:**
   - Register at the [World Air Quality Index (WAQI) API](https://aqicn.org/data-platform/token/#/) to obtain a valid API token.

2. **Update `config.ini`:**
   - Replace the placeholder with your valid AQI API token.

   ```ini
   [AQI]
   authtoken = YOUR_VALID_AQI_AUTHTOKEN
   ```

3. **Restart FireAPRS:**

   ```bash
   python main.py
   ```

### **3. Empty RSS Feed Warning**

**Issue:**  
```
WARNING - Encountered issues parsing the RSS feed: <unknown>:2:-1: Document is empty
INFO - Keyword 'fire' not found in any entry titles.
```

**Cause:**  
The RSS feed URL is invalid, empty, or not returning expected data.

**Solution:**

1. **Verify RSS Feed URL:**
   - Ensure the `link` in the `[newsfeed]` section of `config.ini` is correct and accessible.
   - Test the URL in a web browser or using `curl`:

     ```bash
     curl -I YOUR_RSS_FEED_URL
     ```

2. **Update `config.ini` if Necessary:**
   - Replace with a valid RSS feed URL that provides news related to fires.

   ```ini
   [newsfeed]
   link = https://example.com/fire-news.rss
   keyword = fire
   ```

3. **Handle Empty or Invalid Feeds Gracefully:**
   - FireAPRS already sends a default APRS message when no news links are found.

4. **Restart FireAPRS:**

   ```bash
   python main.py
   ```

### **4. APRS Disconnect Error**

**Issue:**  
```
ERROR - Error disconnecting from APRS: 'IS' object has no attribute 'disconnect'
```

**Cause:**  
The `aprslib.IS` object may not have a `disconnect` method due to an outdated library version or incorrect usage.

**Solution:**

1. **Upgrade `aprslib`:**

   ```bash
   pip install --upgrade aprslib
   ```

2. **Verify `disconnect` Method:**

   In your Python environment, check if `aprslib.IS` has the `disconnect` method:

   ```python
   import aprslib
   print(hasattr(aprslib.IS, 'disconnect'))
   ```

   *This should output `True`.*

3. **Update `aprs_sender.py`:**

   Ensure the `disconnect` method is correctly implemented with proper error handling.

   ```python
   def disconnect(self):
       try:
           if hasattr(self.ais, 'disconnect'):
               self.ais.disconnect()
               logging.info("Disconnected from APRS.")
           else:
               logging.warning("The 'IS' object does not have a 'disconnect' method. Attempting manual socket closure.")
               if hasattr(self.ais, 'sock'):
                   self.ais.sock.close()
                   logging.info("Manually closed the APRS connection.")
               else:
                   logging.error("The 'IS' object does not have a 'sock' attribute.")
       except Exception as e:
           logging.error(f"Error disconnecting from APRS: {e}")
   ```

4. **Restart FireAPRS:**

   ```bash
   python main.py
   ```

## License

This project is licensed under the [GNU](LICENSE).

---
