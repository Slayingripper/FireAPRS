# Fire APRS
![](/icon/aprs_world_5in.png)

# FireAPRS
FireAPRS uses the nasa VIIRS sattelite data to plot the position of fires on the APRS network in the last 24 hours.
The configuration file of the FireAPRS allows it to be confgured for any geographhical area. 

## Configuration

To configure FIreAPRS , we first need to create a geographical "box" using 4 coordinates. This allows us to define the area of interest.

```

[aprssend]
callsign = 
password = 
comment =  Fire Alert!!!
symbol = :

[viirs]
url = https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_Global_24h.csv
filepath = SUOMI_VIIRS_C2_Global_24h.csv
latitude1 = latitude position of the top left corner of the area
latitude2 = latitude position of the bottom right corner of the area
longitude1 = longitude position of the top left corner of the area
longitude2 = longitude position of the bottom right corner of the area

[firejson] to be added
host = localhost
port = 8273

```

