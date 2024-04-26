from osgeo import gdal
import os
import config
import numpy as np
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_unprocessed_files(raw_data_path, processed_path):
    """
    Identify files in the raw data directory that haven't been processed yet.

    Args:
    raw_data_path (str): Path to the directory containing raw data files.
    processed_path (str): Path to the directory where processed files are stored.

    Returns:
    list: A list of filenames (without extension) that have not been processed.
    """
    processed_files = [f.split('.')[0] for f in os.listdir(processed_path) if os.path.isfile(os.path.join(processed_path, f))]
    raw_files = [f.split('.')[0] for f in os.listdir(raw_data_path) if os.path.isfile(os.path.join(raw_data_path, f)) and f.split('.')[-1] == 'asc']
    unprocessed_files = [f for f in raw_files if f not in processed_files]
    return unprocessed_files

def parse_ascii_grid(file_path):
    """
    Parse the ASCII grid file to separate the header and data sections.

    Args:
    file_path (str): The full path to the ASCII file.

    Returns:
    tuple: A dictionary containing header key-value pairs and a list of data rows.
    """
    header = {}
    data = []
    with open(file_path, 'r') as file:
        line = file.readline()
        while line.strip() and not line.startswith("[ASCII-Raster-Format]"):
            if '=' in line:
                key, value = line.strip().split('=', 1)
                header[key] = value
            line = file.readline()

        for line in file:
            n_cells = len(line.split(" "))

            # ascii raster info
            if n_cells == 2:
                key, value = line.strip().split(' ', maxsplit=1)
                header[key] = value

            else:
                data.append(list(map(float, line.split(" "))))
    return header, data

def create_geotiff_from_data(header, data, output_filename):
    """
    Create a GeoTIFF file from parsed ASCII grid data and header information.

    Args:
    header (dict): Dictionary containing header information of the ASCII file.
    data (list): List of data rows (each row is also a list).
    output_filename (str): Path to save the output GeoTIFF file.
    """
    array = np.array(data)
    nrows, ncols = array.shape
    xllcorner = float(header['XLLCORNER'])
    yllcorner = float(header['YLLCORNER'])
    cellsize = float(header['CELLSIZE'])
    nodata = float(header['NODATA_VALUE'])

    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(output_filename, ncols, nrows, 1, gdal.GDT_Float32, ["COMPRESS=LZW"])
    dataset.SetGeoTransform([xllcorner, cellsize, 0, yllcorner, 0, -cellsize])
    dataset.SetProjection('EPSG:31467')

    band = dataset.GetRasterBand(1)
    band.SetNoDataValue(nodata)
    band.WriteArray(array)
    dataset.FlushCache()
    dataset = None  # Properly close the dataset

def main():
    """
    Main function to process unprocessed ASCII files into compressed GeoTIFF format.
    """
    logging.info("Starting to process raw files from the DWD folder.")
    unprocessed_files = get_unprocessed_files(config.SAVE_PATH_GLOBAL_DWD, config.SAVE_PATH_GLOBAL_DWD_PROCESSED)
    for file_name in unprocessed_files:
        filepath_raw = os.path.join(config.SAVE_PATH_GLOBAL_DWD, f"{file_name}.asc")
        filepath_processed = os.path.join(config.SAVE_PATH_GLOBAL_DWD_PROCESSED, f"{file_name}.tif")
        logging.info(f"Processing file: {filepath_raw}")
        header, data = parse_ascii_grid(filepath_raw)
        create_geotiff_from_data(header, data, filepath_processed)
        logging.info(f"Processed and saved to: {filepath_processed}")

if __name__ == "__main__":
    main()
