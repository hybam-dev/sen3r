[![DOI](https://zenodo.org/badge/233877233.svg)](https://zenodo.org/badge/latestdoi/233877233)
[![PyPI version](https://badge.fury.io/py/sen3r.svg)](https://badge.fury.io/py/sen3r)
## SEN3R - Sentinel 3 Reflectance Retrieval over Rivers

SEN3R is a stand-alone command-line utility inspired by [MOD3R](https://hybam.obs-mip.fr/software-2/) and made to simplify the pipeline of image 
processing over ESA's Sentinel-3 mission. 
<br>
<br>
⚠️ GDAL is a requirement for the installation, therefore, 
usage of a conda environment 
([Anaconda.org](https://www.anaconda.com/products/individual)) 
is strongly recommended. Unless you know what you are doing (-:

## Installation
Create a Conda environment (python versions above 3.7 were not tested but they should also be compatible):
```
conda create --name sen3r python=3.7
```
Activate your conda env:
```
conda activate sen3r
```
Install GDAL before installing `requirements.txt` to avoid dependecy error with pyshp:
```
conda install -c conda-forge gdal
```
Install the requirements:
```
python -m pip install -r requirements.txt
```
We recommend you to run the internal setup (more up-to-date) but you can also use PyPI `pip install sen3r`:
```
python setup.py install 
```
Do a quick test:
```
sen3r -h 
```
If all runs well, you should see:
```
(sen3r) D:\user_path\sen3r>sen3r -h
usage: sen3r [-h] [-i INPUT] [-o OUT] [-r ROI] [-p PRODUCT] [-c CAMS]
             [-k CLUSTER] [-s] [-v]

SEN3R (Sentinel-3 Reflectance Retrieval over Rivers) enables extraction of
reflectance time series from Sentinel-3 L2 WFR images over water bodies.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        The products input folder. Required.
  -o OUT, --out OUT     Output directory. Required.
  -r ROI, --roi ROI     Region of interest (SHP, KML or GeoJSON). Required
  -p PRODUCT, --product PRODUCT
                        Currently only WFR is available.
  -c CAMS, --cams CAMS  Path to search for auxiliary CAMS file. Optional.
  -min IRMIN, --irmin IRMIN
                        Default bottom dropping threshold for IR. Optional.
  -max IRMAX, --irmax IRMAX
                        Default upper dropping threshold for IR. Optional.
  -k CLUSTER, --cluster CLUSTER
                        Which method to use for clustering. Optional.
  -s, --single          Single mode: run SEN3R over only one image instead of
                        a whole directory. Optional.
  -v, --version         Displays current package version.
```

Windows users: For OS compatibility reasons the supported vector formats for `-r` are `.json` and `.geojson`. But if you are under Linux there are implementations in the code to also support `.shp`, `.kml` and `.kmz`. Just check for them inside `commons.py` > `Utils` > `roi2vertex`.

## Usage 

For a folder of WFR files:
```
sen3r -i "C:\PATH\TO\L2_WFR_FILES" -o "C:\sen3r_out" -r "C:\path\to\your_vector.json"
```

For a single WFR file:
```
sen3r -s -i "C:\PATH\TO\L2_WFR_IMG" -o "C:\sen3r_out" -r "C:\path\to\your_vector.json"
```

## Citing
While the official paper is not published you can use the Zenodo citation:

Franca, David, Martinez, Jean-Michel, & Cordeiro, Mauricio. (2021). SEN3R - Sentinel 3 Reflectance Retrieval over Rivers (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.5710870

or the BibTex:
```
@software{franca_david_2021_5710870,
  author       = {Franca, David and Martinez, Jean-Michel and
                  Cordeiro, Mauricio},
  title        = {{SEN3R - Sentinel 3 Reflectance Retrieval over 
                   Rivers}},
  month        = nov,
  year         = 2021,
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.5710870},
  url          = {https://doi.org/10.5281/zenodo.5710870}
}
```
