## 1. Prepare the Environment for Executing the LEAF Production Tool

To run the LEAF production tool on a local computer with the Windows Operating System, the following prerequisites need to be fulfilled:

*  A registered Google Account and an approval to access Google Earth Engine (GEE). These are mandentory requirments to access GEE python API.
*  Installation of [Anaconda](https://www.anaconda.com/) and [GEE Python API](https://developers.google.com/earth-engine/tutorials/community/intro-to-python-api-guiattard) on the user's local computer. Anaconda is a widely-used Python distribution suitable for most data science applcations.
* Clone or download the LEAF production tool from GitHub and save it in a dedicated directory on the local computer. 

### 1.1 Create Google Account and Request Access to Google Earth Engine
The LEAF production tool was built on the basis of GEE Python API. So to be able to run LEAF production tool, you need to follow next steps:

(1) Create a Google Account: If you don't already have one, you'll need to create a Google Acount. See [Create a Google Account](https://cloud.google.com/apigee/docs/hybrid/v1.1/precog-gcpaccount) for the steps to create a Google Account.

(2) Request Access to GEE: Having a Google Account, dose not mean you can access to GEE and its APIs. You need to request access by going to [Request Access to GEE](https://earthengine.google.com/) and clicking on the "Sign Up" or "Request Access" button. Follow the instruction to submit a request for access. 

(3) Approval and Invitation: GEE access requests are typically reviewed by Google, and if approved, you will receive an invitation to use GEE. This may take some time, as access is often granted to researchers, scientists, and organizations working on environmental and geospatial projects. Once you receive an invitation, follow the instructions in the email to accept it. You may be asked to provide additional information about your intended use of GEE.

RefreshError: ('invalid_grant: Token has been expired or revoked.', {'error': 'invalid_grant', 'error_description': 'Token has been expired or revoked.'})

### 1.2 Install Anaconda and GEE Python API
The installation of Anaconda on a local computer is a straightforward process. Just go to [Anaconda Website](https://www.anaconda.com/) of Anaconda and follow the given instructions. After the installation, open a Windows terminal or **Anaconda Prompt**, so that conda commands can be issued from there. 

It is highly recommended to create a dedicated conda virtual environment for installing GEE Python API and executing the LEAF production tool. The following command line can be used to create a dedicated conda vitual environment ('leaf_prod' is used here to name the environment, but you can use any other name you like):

**`conda create -n leaf_prod`**

The following two command lines can be used to activate the virtual environment and install GEE Python API within it:

**`conda activate leaf-prod`**

**`conda install -c conda-forge earthengine-api`**

Lastly, authenticate with GEE by running **`earthengine authenticate`** command and follow the instructions. A URL will be provided that generates an authorization code upon agreement. Copy the authorization code and enter it as the input of the command line.

### 1.3 Make a copy of the LEAF production tool from GitHub
There are two ways to obtain the source code of LEAF production tool from Github.

(1) Download the source code from the option you can see when you land on github source code. After the source code has been downloaded, copy it to a desired location on your local drive and unzip it.

(2) Clone the repo on your desktop (which is same as downloading on desktop but in a GIT way). You just have to run only one command which is git clone https://github.com/username/repo-url.
* Copy the url which is given in your clone with HTTPS box.

* Open you terminal/command prompt and paste the url and hit enter

* The source code is copied or downloaded on your preferred location.

## 2. Run LEAF Production Tool from Jupyter Notebook
 
It is recommanded to run LEAF production tool using a Notebook comes with LEAF production tool package. To do so, follow the next steps:

(1) Open **Anaconda Prompt** and **activate your conda virtual environment dedicated for LEAF production tool**, if you have not done these yet. 

(2) Issue **`jupyter notebook`** command within **Anaconda Prompt** to start Jupyter Notebook Home Page in your default web browser. Note that ensure **jupyter notebook** command is issued from the local drive where you store the LEAF production tool package, otherwise using **`cd drive`** command to go to the desired local drive.

(3) Within the Jupyter Notebook Home Page, you should be able to see all the directories on your desired local drive. Go to the directory where you stored the LEAF production tool package and double click "LeafProdTool.ipynb" file.

(4) Within LeafProdTool notebook webpage, go to the seconf code cell and modify some input parameters as need. The second code cell includes a Python Dictionary data structure, which contains all required input parameters for executing LEAF production tool. The key to run the LEAF production tool is to adjust input parameters according to your production need. For detailed information on this, please refer to section 1.3 in [code architecture](/docs/code_architecture.md).

