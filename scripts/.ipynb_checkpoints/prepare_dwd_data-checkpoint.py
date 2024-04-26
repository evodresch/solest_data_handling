from osgeo import gdal
import os
import config

# Constants
# Path where the raw global irradiation files are
raw_path_global = config.SAVE_PATH_GLOBAL_DWD
# Path where the prepared irradiation files will go
prepared_path_global = config.SAVE_PATH_GLOBAL_DWD_PREPARED

# This script will prepare the dwd raw data to be used in SolEst later on

# 0. Get the actual data from the ascii file and parse the header
def parse_ascii_grid(file_path):
    header_info = {}
    ascii_raster_info = {}
    data = []

    with open(file_path, 'r') as file:
        # Read header section
        line = file.readline()
        while line.strip() and not line.startswith("[ASCII-Raster-Format]|[header]"):
            if '=' in line:
                key, value = line.strip().split('=', 1)
                header_info[key] = value
            line = file.readline()

        # Read ascii raster info and grid data section
        for line in file:
            n_cells = line.strip(" ")

            # ascii raster info
            if n_cells == 2:
                key, value = line.strip().split(' ', maxsplit=1)
                ascii_raster_info[key] = value

            else:
                data.append(list(map(float, line.split(" "))))

    return header_info, ascii_raster_info, data



# 1. Reducing spatial resolution
# Since there is no real need to have a 1 km x 1 km spatial resolution in SolEst, we will reduce
# the resolution by half using gdal

def aggregate_grid(input_file, output_file, factor):
    ds = gdal.Open(input_file)
    gdal.Translate(output_file, ds, xRes=factor*1000, yRes=factor*1000, resampleAlg='average')
    ds = None


# 2. Convert to GeoTIFF to compress the data
# This allows for a more efficient way to store the data

def convert_to_geotiff(input_file, output_file):
    ds = gdal.Open(input_file)
    gdal.Translate(output_file, ds, format='GTiff', creationOptions=["COMPRESS=LZW"])
    ds = None


# 3. Function to prepare the dwd ascii files

def prepare_dwd_data(input_directory, output_directory):
    files = [f for f in os.listdir(input_directory) if f.endswith('asc')]
    for f in files:
        output_file = f"{output_directory}{f}"
        aggregate_grid(f"{input_directory}{f}", output_file, 2)
        convert_to_geotiff(output_file, output_file)


# Prepare irradiation data
# prepare_dwd_data(raw_path_global,
#                 prepared_path_global)