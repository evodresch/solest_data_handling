import os
from bs4 import BeautifulSoup
import requests
import zipfile
import logging
import config
import gzip
import shutil

# Constants
# DWD irradiation data url
url = config.BASE_URL_TEMPERATURE_DWD
# Path where the downloaded files will be saved
save_path = config.SAVE_PATH_TEMPERATURE_DWD
# Min and max years with data
min_year = config.MIN_YEAR_TEMPERATURE_DWD
max_year = config.MAX_YEAR_TEMPERATURE_DWD

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def list_directories(base_url):
    """List all directories within the base URL"""
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return [base_url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith('/')]


def extract_gz(gz_path, extract_to):
    """Extract a .gz file"""
    with gzip.open(gz_path, 'rb') as f_in:
        with open(extract_to, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(gz_path)


# Define list of relevant files according to the years to be downloaded
def get_relevant_file_links(url, first_year, last_year):
    """Get the links to relevant global radiation files
    First year will be the first year of the data to be downloaded
    Last year (until december) will be downloaded"""
    page = requests.get(url).text

    # Pattern to get the files for the chosen years
    relevant_months = [f"{str(yr)}{str(month).zfill(2)}" for month in range(1, 13) for yr in range(first_year,
                                                                                                   last_year + 1)]
    soup = BeautifulSoup(page, 'html.parser')

    return [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith('.gz') and \
            node.get('href').split('.')[-3].split('_')[-1] in relevant_months]


def download_file(url, filename, save_path):
    """Download an individual file from the DWD website with error handling"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Will raise an exception for 4XX/5XX status
        file_path = os.path.join(save_path, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f'Downloaded {filename}')
    except requests.exceptions.RequestException as e:
        logging.error(f'Failed to download {filename}: {str(e)}')
    return file_path


def get_valid_input(prompt, min_year, max_year):
    """Reusable function to get validated user input for year."""
    while True:
        try:
            year = int(input(prompt))
            if min_year <= year <= max_year:
                return year
            else:
                print(f"Please enter a year between {min_year} and {max_year}.")
        except ValueError:
            print("Invalid input. Please enter an integer.")


def main():
    print("This script downloads ambient temperature data from the DWD climate center.")
    print("The monthly data are downloaded from January of the first year until December of the last year.")

    # User input for the first year
    first_year = get_valid_input("Please enter the first year of the data to get downloaded: ",
                                 min_year, max_year - 1)

    # User input for the last year
    last_year = get_valid_input("Please enter the last year of the data to get downloaded: ",
                                min_year + 1, max_year)

    # List all month directories
    month_dirs = list_directories(url)

    for month_dir in month_dirs:
        print(f"Processing directory: {month_dir}")
        gz_files = get_relevant_file_links(month_dir, first_year, last_year)

        for gz_file in gz_files:
            print(f"Downloading {gz_file}")
            filename = gz_file.split('/')[-1]

            gz_path = download_file(gz_file, filename, save_path)

            # Extract the .asc file
            asc_filename = gz_file.split('/')[-1].replace('.gz', '')
            asc_path = os.path.join(save_path, asc_filename)
            extract_gz(gz_path, asc_path)
            print(f"Extracted {asc_path}")


if __name__ == "__main__":
    main()
