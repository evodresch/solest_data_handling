import os
from bs4 import BeautifulSoup
import requests
import zipfile
import logging
import config

# Constants
# DWD irradiation data url
url = config.BASE_URL_GLOBAL_DWD
# Path where the downloaded files will be saved
save_path = config.SAVE_PATH_GLOBAL_DWD
# Min and max years with data
min_year = config.MIN_YEAR_GLOBAL_DWD
max_year = config.MAX_YEAR_GLOBAL_DWD

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    relevant_file_links = [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href') and \
                 node.get('href').split('.')[-2].split('_')[-1] in relevant_months]
    return relevant_file_links


def download_file(url, filename, save_path):
    """Download an individual file from the DWD website with error handling"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Will raise an exception for 4XX/5XX status
        with open(os.path.join(save_path, filename), 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f'Downloaded {filename}')
    except requests.exceptions.RequestException as e:
        logging.error(f'Failed to download {filename}: {str(e)}')


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
    print("This script downloads global irradiation data from the DWD climate center.")
    print("The monthly data are downloaded from January of the first year until December of the last year.")

    # User input for the first year
    first_year = get_valid_input("Please enter the first year of the data to get downloaded: ",
                  min_year, max_year - 1)

    # User input for the last year
    last_year = get_valid_input("Please enter the last year of the data to get downloaded: ",
                  min_year + 1, max_year)

    file_list = get_relevant_file_links(url, first_year=first_year, last_year=last_year)

    for file_name in file_list:
        # Extract the zip file name from the strings in the list (links)
        zip_file = file_name.split('/')[-1]
        download_file(file_name, zip_file, save_path)

        zip_file_path = save_path + zip_file
        with zipfile.ZipFile(zip_file_path) as file:
            file.extractall(path=save_path)
        os.remove(zip_file_path)

if __name__ == "__main__":
    main()
