# Ku Download and Parse App

**Author: dedtadeas**

This application is designed to download and process KU (Cadastre Units) files from a specified URL. The downloaded KU files are then extracted and processed to be uploaded to a Geodatabase (GDB) using ArcPy. The application consists of three main components: KuDownloader, KUParser, and the main script.

## Installation

To install the required packages, create a Conda environment using the provided 'requirements.txt' file:

```bash
conda create --name ku_app --file requirements.txt
```

## Usage

To download and process KUs, run the 'main.py' script:

```bash
python main.py
```

## Components

### KuDownloader

A class to download KUs from a specified URL using Selenium and Chrome WebDriver.

Dependencies:

- Selenium: For web automation.
- pathlib: For working with file paths.
- tqdm: For displaying download progress.
- yaml: For loading configuration from 'config.yaml'.

### KUParser

A class to parse and process downloaded KU files.

Dependencies:

- zipfile: For extracting files from zip archives.
- pathlib: For working with file paths.
- tqdm: For displaying extraction and processing progress.
- yaml: For loading configuration from 'config.yaml'.
```