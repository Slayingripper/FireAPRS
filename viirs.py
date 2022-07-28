    
from distutils.command.config import config
import pandas as pd
import wget
import os
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

#url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_24h.csv"
url = config.get('viirs','url')

#filePath = 'SUOMI_VIIRS_C2_Global_24h.csv'
filePath = config.get('viirs','filepath')
latitude_pos_1 = config.get('viirs','latitude1')
latitude_pos_2 = config.get('viirs','latitude2')
longitude_pos_1 = config.get('viirs','longitude1')
longitude_pos_2 = config.get('viirs','longitude2')

def download_file(url, filePath):
    # As file at filePath is deleted now, so we should check if file exists or not not before deleting them
    if os.path.exists(filePath):
        os.remove(filePath)

    wget.download(url, filePath)
    csv_file = pd.DataFrame(pd.read_csv(filePath, sep = ",", header = 0, 
                                        index_col = False,usecols= ['latitude', 'longitude']))

    # filteredcsv = csv_file[ (34.511083 > csv_file.latitude > 35.844535) &
    #                         (34.661865 > csv_file.longitude > 31.816406)]
    filteredcsv = csv_file[ (csv_file.latitude <= float(latitude_pos_1)) & (csv_file.latitude >= float(latitude_pos_2)) &
                            (csv_file.longitude >= float(longitude_pos_1)) & (csv_file.longitude <= float(longitude_pos_2))]
    print(filteredcsv)
    filteredcsv.to_json("viirs.json",
                    orient = "records", date_format = "epoch", double_precision = 10, 
                    force_ascii = True, date_unit = "ms", default_handler = None)    
def viirsdownloader():
    download_file(url, filePath)
viirsdownloader()