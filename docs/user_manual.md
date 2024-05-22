## 1. Create Accounts and an Environment

To run the LEAF production tool on a local computer, the following prerequisites need to be fulfilled:

*  A registered Google Account and an approval to access Google Earth Engine (GEE). These are mandentory requirments to access GEE Python API.
*  Installation of [Anaconda](https://www.anaconda.com/) and [GEE Python API](https://developers.google.com/earth-engine/tutorials/community/intro-to-python-api-guiattard) on the user's local computer. Anaconda is a widely-used Python distribution suitable for most data science applcations.
* Clone or download the LEAF production tool from GitHub and save it in a dedicated directory on your local drive. 

Go to [Account and Environment](/docs/prepare_environment.md) to get the detailed steps for fullfilling these prerequisites.

## 2. Run the LEAF Production Tool from Jupyter Notebook
 
It is recommended to run LEAF tool using the Notebook provided with this LEAF tool package. To do so, follow the following steps:

(1) Open **Anaconda Prompt** and **activate your conda virtual environment dedicated for LEAF production tool**, if you have not done these yet. 

(2) Issue **`jupyter notebook`** command within **Anaconda Prompt** to start Jupyter Notebook Home Page in your default web browser. Note that ensure **jupyter notebook** command is issued from the local drive where you store the LEAF production tool package, otherwise using **`cd drive`** command to go to the desired local drive.

(3) Within the Jupyter Notebook Home Page, you should be able to see all the directories on your desired local drive. Go to the directory where you stored the LEAF production tool package and double click "LeafProdTool.ipynb" file.

(4) Within LeafProdTool notebook webpage, go to the seconf code cell and modify some input parameters as need. The second code cell includes a Python Dictionary data structure, which contains all required input parameters for executing LEAF production tool. The key to run the LEAF production tool is to adjust input parameters according to your production need. For detailed information on this, please refer to section 1.3 in [code architecture](/docs/code_architecture.md).

## 3. Troubleshooting 

## 4. Download Results from Google Drive or Google Cloud Storage
 
The LEAF production tool can export products to either Google Drive or Google Cloud Storage. Depending on your choice of export destination, the process for downloading the product files will vary. The detailed steps for downloading the product files from these places can be found in [Download Results from Google Drive and Google Cloud Storage](/docs/download_products.md)   

## 5. Check Results using PCI or QGIS
 
Once you downloaded the product files to your local drive, you can check the results using either PCI focus or QGIS.
