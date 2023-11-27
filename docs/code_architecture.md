## 1. Major Data Structures Used In The LEAF Production Tool

There are three major data structures used in LEAF production tool and all of them are python dictionary objects. Of the three, two are defined as global variables and have been named “COLL_OPTIONS” and “PROD_OPTIONS”, respectively. The third object can be named in any way user want, but must be passed to the main function (“LEAF_tool_main”) of LEAF production tool. The following sections provide detailed descriptions on the objects.
    
### 1.1 Image Collection Options
This python dictionary currently contains TWO "key:value" pairs to store the options associated with Sentinel-2 and Landsat-8 dataset, respectively. The two keys are “COPERNICUS/S2_SR” and “LANDSAT/LC08/C02/T1_SR”, which are the catalog names used by GEE for the two datasets. The values corresponding to the two keys are also python dictionary objects including SEVENTEEN "key:value" pairs. The main contents of the seventeen items include the property names used by a dataset for imaging angles, cloud coverage, and the links to the neural network coefficients to be applied for biophysical parameter extraction. This dictionary is defined in LEAFNets.py.
 
### 1.2 Product Options
This python dictionary object includes EIGHT "key:value" pairs. Four of them are for currently producable biophysical parameters (LAI, fCOVER, fAPAR and Albedo) and rest are for potential developments. Each key:value pair in this dictionary contains the information related to one biophysical parameter product. This dictionary is also defined in LEAFNets.py.



### 1.3 Parameter Dictionary for Running the LEAF Production Tool
To run the LEAF production tool, a number of parameters must be provided. To streamline the provision of these parameters, a Python dictionary is used as a container. An illustration of a parameter dictionary is presented below:

![](/wiki_images/LEAF_param_dict.png)

Specifically, the dictionary includes NINE “key:value” pairs, each of which is detailed as follows:

(1) 'sensor': a string denoting a satellite sensor and data unit. The valid values for this key currently are 'L8_SR' and 'S2_SR', representing Landsat 8/9 and Sentinel-2 surface reflectance data (for vegetation biophysical parameter estimation, the input images must be surface reflectance), respectively. 

(2) 'year' : a 4-digits integer, identifying the year of the image acquisitions (e.g., 2020).

(3) 'months' : a list of integers (1 to 12) representing the monthes of a year (e.g., [6, 7, 8] denote June, July and August). With a list of monthes, several monthly biophysical parameter products can be generated through one execution of the LEAF production tool. This list can also include only one negative integer. In this case, the biophysical parameter products corresponding to the peak season (June 15 to September 15) of a year (specified by 'year' key) will be produced.

(4) 'prod_names' : a list of biophysical parameter name strings, which can be a subset or all of the elements in ['LAI', 'fCOVER', 'Albedo', 'fAPAR', 'QC', 'date', 'partition'].

(5) 'tile_names' : a set of strings representing tile names. The regular spatial unit of the LEAF production tool is a tile, defined by the Canadian tile griding system and covering a 900km x 900km area. Providing a list of tile names allows for the creation of biophysical parameter products for multiple tiles in a single execution of the LEAF production tool. Note that to generate biophysical parameter maps for a custom region, another "key:value" pair must be added into this parameter dictionary (refer to the details on 'custom_region' key). 

(6) 'spatial_scale' : an integer that defines the spatial resolution (in meter) of the exported products.

(7) 'location' : a string specifying the location to export the products. The valid string for this parameter could be either 'drive' or 'storage', representing Google Drive (GD) and Google Cloud Storage (GCS), respectively.

(8) 'bucket' : a customized name string of a bucket on GCS. This parameter only is used when the exporting location is GCS (when value corresponding to 'location' is 'storage'). Note that a bucket with this name must exist on your GCS before exporting products. 

(9) 'out_folder' : the folder name on GD or GCS for holding the exported biophysical parameter products. If you do not want the products for different tiles are exported in the same folder, just leave an empty string for this key. In this case, the LEAF production tool will automatically create separate folders for the products of different tiles using a tile name and the image acquisition year specified in the dictionary items with ‘tile_names’ and “year” as keys.

Of the NINE items of an input parameter dictionary, six (with 'sensor', 'year', 'spatial_scale', 'location', 'bucket' and 'out_folder' as keys) require a single value, while the other three (with 'months', 'prod_name' and 'tile_names' as keys) need a list. Obviously, with the different combinations between the lists, various production scenarios can be carried out. For instance, to generate monthly (e.g., July and August) biophysical parameter maps for multiple tiles (e.g., 'tile41', 'tile42' and 'tile43'), two lists, [7, 8] and ['tile41', 'tile42', 'tile43'], should be specified for 'months' and 'tile_names' keys.

## 2. Function Call Graph Of The LEAF Production Tool

The LEAF production tool mainly consists of 12 functions. The names and call graph of these functions are shown as follows:
![](/wiki_images/LEAF_function_call_graph.png)

## 3. Brief Descriptions on LEAF Functions
[LEAF_tool_main(exe_param_dict)](/docs/LEAF_tool_main.md)

[LEAF_Mosaic(fun_param_dict, mapBounds)](/docs/LEAF_mosaic.md)

[one_LEAF_product(mosaic, fun_param_dict, mapBounds, output, tasl_list)](/docs/one_LEAF_product.md)

[export_ancillaries(mosaic, fun_param_dict, mapBounds, task_list)](/docs/export_ancillaries.md)

[invalidInput(sl2pDomain, bandList, mosaic)](/docs/invalidInput.md)

[make_DNet_arr(all_nets, numClasses, paramID)](/docs/make_DNet_arr.md)

[wrapperNNets(networks, partition, prod_options, coll_options, suffix_name, image)](/docs/wrapperNNets.md)

[export_products(fun_param_dict, mapBounds, estimateImage, errorImage, task_list)](/docs/export_products.md)

[FNet_to_DNet(feature_list, class_ID)](/docs/FNet_to_DNet.md)

[makeIndexLayer(partition, numb_classes, legend, network_IDs)](/docs/makeIndexLayer.md)

[applyNet(image, net_list, band_names, band_scales, net_indx, output_name)](/docs/applyNet.md)

[getCoefs(netData, index)](/docs/getCoefs.md)
