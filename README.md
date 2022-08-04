This is Landscape Evolution And Forecasting (LEAF) production tool implemented with Python programming language and Google Earth Engine (GEE) python API. With this tool, users can efficiently produce biophysical parameter maps with associated uncertainty estimates from the surface reflectance satellite imagery hosted in GEE. The two major features of this tool are: (1) various production requirements can be defined by configuring a flexible input parameter dictionary; (2) all results can be exported automatically to a specified location (either Google Drive or Google Cloud Storage) in a batch mode. 

The regular output spatial unit of this tool is a 900km x 900km tile, which is defined by the Canadian geospatial tile griding system (there are 26 tiles covering the Canadian landmass). However, a customized polygon can also be utilized to define the spatial area of a production. Currently, four types of biophysical products (LAI, fCOVER, fAPAR and Albedo) can be generated with this tool. For each product, there are three associated GeoTiff images, estimated biophysical parameter map, uncertainty map and QC map, with all pixel values are 8-bits unsigned integers. A rescaling factors applied LAI and other three parameters are 20 and 200, respectively. The 8-bits bitmask for QC map is configured as follows:
   * bit 0: imput out of range
   * bit 1: output out of range
   * bit 2, invalid pixel due to one of the reasons such as cloud, shadow, snow, ice, water or saturation
   * bit 3-7: sensor type code. For Landsat 5, 7, 8, 9 and Sentinel-2, their sensor type codes are 40, 56, 64, 72 and 168, respectively

The following figure shows the flowchart of LEAF production tool.
![](/wiki_images/flowchart.png)

For the information on how to set up an environment for running LEAF production tool on Windows platform, please refer to [User Guide](/docs/user_manual.md). To improve or update this tool, please review [code architecture](/docs/code_architecture.md). 
