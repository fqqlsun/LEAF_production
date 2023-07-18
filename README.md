This is Landscape Evolution And Forecasting (LEAF) production tool developed using the Python programming language and Google Earth Engine (GEE) Python API. It enables users to generate biophysical parameter maps efficiently from the surface reflectance satellite imagery available in GEE. This tool offers two key features: (1) It allows users to define diverse production requirements by configuring a flexible input parameter dictionary. (2) All results can be exported in a batch mode to a specified location,  either Google Drive or Google Cloud Storage. 

The standard outputs of this tool are organized into tiles, which cover an area of 900km x 900km as per the CCRS' tile grid system. In total, there are 26 tiles that encompass the Canadian landmass. However, users also have the option to define a customized polygon to specify a desired spatial area for production. 

This tool currently supports the generation of four types of biophysical products: LAI, fCOVER, fAPAR and Albedo. Each product is associated with a corresponding GeoTiff image in outputs. Additionally, for each tile, there is a QC (Quality Control) map and an acquisition date map. The pixel values in the biophysical maps are represented as 8-bits unsigned integers, with specific rescaling factors applied. For LAI, the rescaling factor is 20, while for the remaining three biophyscal maps, it is 200.

The 8-bits bitmask for the QC map is structured as follows:
   * bit 0: 1 indicates the input is out of range
   * bit 1: 1 represents the output is out of range
   * bit 2, 1 indicates an invalid pixel due to various reasons such as cloud, shadow, snow, ice, water, or saturation.
   * bit 3-7: Correspond to the sensor type code. For Landsat 5, 7, 8, 9, and Sentinel-2, their respective sensor type codes are 40, 56, 64, 72, and 168.

The following figure shows the flowchart of LEAF production tool.
![](/wiki_images/flowchart.png)

For the information on how to set up an environment for running LEAF production tool on Windows platform, please refer to [User Guide](/docs/user_manual.md). To improve or update this tool, please review [code architecture](/docs/code_architecture.md). 
