## 1. Set Up an Environment for Running the LEAF Production Tool

The prerequisites of running the LEAF production tool on a local/client computer with Windows Operating System are listed as follows:

*  A registered Google Cloud Account and a valid authentication. These are mandentory requirments for accessing GEE API;
*  Installed [Anaconda](https://www.anaconda.com/) and [GEE Python API](https://developers.google.com/earth-engine/tutorials/community/intro-to-python-api-guiattard) on an user's local computer. Anaconda is a widely used Python distribution for most data science applcations;
* Clone or download a copy of the LEAF production tool from GitHub and save it within an independent directory on the local computer. 

### 1.1 Create a Google Cloud Account and Obtain an Authentication Credential
See [link](https://cloud.google.com/apigee/docs/hybrid/v1.1/precog-gcpaccount) for the steps to create a Google Cloud account.

To enable your accessment to GEE servers, you have to obtain an authentication credential from Google. Within your activated conda viryual environment (will be explained in next section), run `earthengine authenticate` command and follow the instructions. A URL will be provided that generates an authorization code upon agreement. Copy the authorization code and enter it as the input of the command line.

### 1.2 Install Anaconda and EE python API
The installation of Anaconda on a local computer is a straightforward process. Just go to the [website](https://www.anaconda.com/) of Anaconda and follow the given instructions. After the installation, open a Windows terminal or **Anaconda Prompt**, so that some conda commands can be issued from there. 

It is highly recommended to create a dedicated conda virtual environment for installing EE Python API and executing the LEAF production tool. The following command line can be used to create a dedicated conda vitual environment ('leaf_prod' is used here to name the environment, but you can use any other name you like):

`conda create -n leaf_prod`

The following two command lines can be used to activate the environment and install EE Python API to the environment:

`conda activate leaf-prod`

`conda install -c conda-forge earthengine-api`

### 1.3 Obtain a copy of the LEAF production tool from GitHub
There are two ways in which you can obtain the source code hosted on Github.

1. Download the source code from the option you can see when you land on github source code.

2. Clone the repo on your desktop (which is same as downloading on desktop but in a GIT way). You just have to run only one command which is git clone https://github.com/username/repo-url.
* Copy the url which is given in your clone with HTTPS box.

* Open you terminal/command prompt and paste the url and hit enter

* The source code is copied or downloaded on your preferred location.

## 2. Run LEAF Production Tool
 
Running LEAF production tool is straightforward. Only a few python statements are needed. The following python program is a typical sample to execute LEAF production tool.

![](/wiki_images/leaf_tool_code.jpg)

Note that this code assumes that you have already obtained an authentication cetdential. The key of running the LEAF production tool is to define an input parameter dictionary (here referred to as "LEAF_PARAMS"). For the details on how to set the values for diffrent keys of an input parameter dictionary, please see section 1.3 in [code architecture](/docs/code_architecture.md).

