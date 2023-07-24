from entities.ku_downloader import KuDownloader
from entities.ku_parser import KUParser

def download_and_process_kus():
    try:
        # Create an instance of the downloader
        # Download the KUs zip files
        kd = KuDownloader()
        kd.download_all_kus()

        # Extract target files from the downloaded zip
        kp = KUParser()
        kp.extract_zip_files()
        kp.upload_data_to_gdb()
        
        # Remove the zip files and unpacked files
        kp.remove_zip_files()
        kp.remove_unpacked_files()
        
        print('Done')
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    download_and_process_kus()