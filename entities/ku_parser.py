from zipfile import ZipFile
from pathlib import Path

from tqdm import tqdm
import yaml
import logging
import arcpy
import shutil

class KUParser:
    """
    A class to parse and process downloaded KU files.

    The KUParser class loads the configuration from 'config.yaml', which includes:
    - download_path: The directory path to store downloaded files.
    - chrome_driver_path: The path to the Chrome WebDriver executable.
    - gdb_path: The path to the Geodatabase (GDB) where data will be uploaded.

    The class provides methods to extract specific files from the downloaded zip and
    store them in a directory named 'unpacked'. It also processes individual KU folders
    and uploads the data to the specified Geodatabase (GDB).

    Dependencies:
    - zipfile.ZipFile: For extracting files from zip archives.
    - pathlib: For working with file paths.
    - tqdm: For displaying extraction and processing progress.
    - yaml: For loading configuration from 'config.yaml'.
    - logging: For logging warnings during extraction.
    - arcpy: For processing and uploading data to the Geodatabase.

    Usage:
    - Create an instance of the KUParser class.
    - Call the 'extract_zip_files()' method to extract specific files from the downloaded zip.
    - Call the 'upload_data_to_gdb()' method to upload extracted data to the Geodatabase.
    - Call the 'remove_zip_files()' method to remove all zip files in the download_path directory.
    - Call the 'process_single_ku()' method to process a single KU folder in the unpacked directory.
    """
    
    def __init__(self):
        """
        Initialize the KuDownloader class by loading the configuration from the 'config.yaml' file.

        Configuration includes:
        - download_path: The directory path to store downloaded files.
        - chrome_driver_path: The path to the Chrome WebDriver executable.
        - download_list: A list of KUs to be downloaded.
        """
        config_file_path = Path(
            __file__).resolve().parent.parent / 'config.yaml'
        with open(config_file_path, 'r') as file:
            config = yaml.safe_load(file)
        
        self.download_path = Path(config['download_path']).resolve()
        self.unpacked_path = self.download_path / "unpacked"
        self.gdb_path = Path(config['gdb_path']).resolve()
    
    def remove_zip_files(self, ku_list=None):
        """
        Remove all zip files in the download_path directory.

        If ku_list is specified, only the zip files with filenames present in ku_list will be removed.
        """
        if ku_list is None:
            ku_list = self.download_path.glob('*.zip')
        for ku in tqdm(ku_list, desc='Removing zip files', unit='zip'):
            try:
                ku.unlink()
            except Exception as e:
                logging.warning(f'Error removing zip file: {ku}. Error: {e}')
        return
    
    def remove_unpacked_files(self):
        """
        Remove unpacked folder
        """
        try:
            shutil.rmtree(self.unpacked_path)
            print(f'Removed unpacked folder: {self.unpacked_path}')
        except Exception as e:
            logging.warning(f'Error removing unpacked folder: {self.unpacked_path}. Error: {e}')
        return
            
    def extract_zip_file(self, zip_file, to_extract):
        """
        Extract specific files from a downloaded zip file and store them in the 'unpacked' directory.

        Args:
            zip_file (str): Path to the zip file to extract from.
            to_extract (list): List of filenames to extract from the zip file.
        """
        with ZipFile(zip_file) as zf:
            files_to_extract = filter(lambda x: x.filename.split('/')[-1] in to_extract,
                                      zf.infolist())
            zf.extractall(path=self.unpacked_path,
                          members=files_to_extract)
        zf.close()
        return

    def extract_zip_files(self):
        """
        Extract specific files from the downloaded zip and store them in a directory named 'unpacked'.
        """
        self.unpacked_path = self.download_path / "unpacked"
        self.unpacked_path.mkdir(exist_ok=True)

        to_extract = ['PARCELY_KN_DEF.cpg',
                      'PARCELY_KN_DEF.dbf',
                      'PARCELY_KN_DEF.prj',
                      'PARCELY_KN_DEF.shp',
                      'PARCELY_KN_DEF.shx',
                      'PARCELY_KN_P.cpg',
                      'PARCELY_KN_P.dbf',
                      'PARCELY_KN_P.prj',
                      'PARCELY_KN_P.shp',
                      'PARCELY_KN_P.shx',
                      ]

        zip_files = self.download_path.glob('*.zip')
        for zip_file in tqdm(zip_files,
                             desc='Unpacking zip files',
                             unit='zip',
                             ):
            try:
                self.extract_zip_file(zip_file, to_extract)
            except Exception as e:
                logging.warning(f'Error extracting zip file: {zip_file}')
        return
        
    def process_single_ku(self, ku_number=None):
        """
        Process a single KU folder in the 'unpacked' directory.

        Args:
            ku_number (str): The KU number to process. If None, the user will be prompted to enter the KU number.
        """
        if ku_number is None:
            ku_number = input('Enter KU number: ')

        target_fc = self.unpacked_path / ku_number / 'PARCELY_KN_P.shp'
        join_fc = self.unpacked_path / ku_number / 'PARCELY_KN_DEF.shp'
        arcpy.analysis.SpatialJoin(str(target_fc.resolve()), 
                                   str(join_fc.resolve()), 
                                   'in_memory/spatial_join',
                                    'JOIN_ONE_TO_ONE', 
                                   )
        if arcpy.Exists(f'KU'):
            arcpy.Append_management('in_memory/spatial_join', f'KU')
        else:
            arcpy.management.CopyFeatures('in_memory/spatial_join', f'KU')
            
        arcpy.Delete_management('in_memory/spatial_join')
        
        return

        
    def upload_data_to_gdb(self):
        """
        Upload data from unpacked KU folders to the Geodatabase (GDB).

        The data will be uploaded to a feature class named 'KU' in the specified GDB.
        """
        if not self.gdb_path.exists():
            arcpy.CreateFileGDB_management(str(self.gdb_path.parent), self.gdb_path.name)
        else:
            arcpy.arcpy.Delete_management('KU')
        arcpy.env.workspace = str(self.gdb_path)
        arcpy.env.XYDomain = "-916406 -1234597 -419902 -738093"
        sr = arcpy.SpatialReference("S-JTSK_Krovak_East_North")

        # Allow overwriting of output
        arcpy.env.overwriteOutput = True

        # Setting up parallel processing
        arcpy.env.parallelProcessingFactor = "100%"
        
        ku_names = self.unpacked_path.glob('*')
        for ku in tqdm(ku_names, desc='Uploading data to GDB', unit='KU'):
            try:
                self.process_single_ku(ku.name)
            except Exception as e:
                logging.warning(f'Error processing KU: {ku.name}. Error: {e}')

        # Print the gdb file path
        print(f'Resulting GDB file path: {self.gdb_path}')
        
        return
    
    