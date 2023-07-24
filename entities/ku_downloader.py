from selenium import webdriver
from selenium.webdriver.common.by import By

from pathlib import Path
from tqdm import tqdm
import yaml

class KuDownloader:
    """
    A class to download KUs from a specified URL using Selenium and Chrome WebDriver.

    The KuDownloader class loads the configuration from 'config.yaml', which includes:
    - download_path: The directory path to store downloaded files.
    - chrome_driver_path: The path to the Chrome WebDriver executable.
    - download_list: A list of KU numbers used to filter and download specific KUs.

    The class provides methods to download all KUs available on the specified URL and
    download specific KUs based on the download_list. It uses Selenium to interact with the webpage.

    Dependencies:
    - Selenium: For web automation.
    - pathlib: For working with file paths.
    - tqdm: For displaying download progress.
    - yaml: For loading configuration from 'config.yaml'.
    - ku_parser.KUParser: A class to parse and process downloaded KU files.

    Usage:
    - Create an instance of the KuDownloader class.
    - Call the 'download_all_kus()' method to download all KUs available on the URL.
    - Call the 'download_kus_for_list()' method to download specific KUs based on the download_list.
    """
    
    
    def __init__(self):
        """
        Initialize the KuDownloader class by loading the configuration from the 'config.yaml' file.

        Configuration includes:
        - download_path: The directory path to store downloaded files.
        - chrome_driver_path: The path to the Chrome WebDriver executable.
        """
        config_file_path = Path(
            __file__).resolve().parent.parent / 'config.yaml'
        with open(config_file_path, 'r') as file:
            config = yaml.safe_load(file)

        self.download_path = Path(config['download_path']).resolve()
        if not self.download_path.exists():
            d_path = Path(__file__).parent.parent/self.download_path
            d_path.mkdir()

        options = webdriver.ChromeOptions()
        prefs = {'download.default_directory': str(self.download_path)}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)
        self.download_list = config['download_list']

    def download_all_kus(self):
        """
        Download all KUs available on the specified URL.

        KUs will be downloaded to the 'download_path' directory specified in the configuration.
        """
        try:
            self.driver.get('https://services.cuzk.cz/shp/ku/epsg-5514/')
            x = self.driver.find_elements(By.CSS_SELECTOR, 'a')
            for link in tqdm(x[2:], desc='Downloading KUs', unit='KU'):
                link.click()
        except Exception as e:
            raise Exception(f"Error occurred while downloading KUs. Error: {e}") from e
