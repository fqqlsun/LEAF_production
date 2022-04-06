## 1. Major Data Structures Used In LEAF Production Tool

There are three major data structures used in LEAF production tool and all of them are python dictionary objects. Of the three, two are defined as global variables and have been named “COLL_OPTIONS” and “PROD_OPTIONS”, respectively. The third object can be named in any way user want, but must be passed to the main function (“LEAF_tool_main”) of LEAF production tool. The following sections provide detailed descriptions on the objects.
    
### 1.1 Image Collection Options
This python dictionary currently contains two key:value pairs for storing the options associated with Sentinel-2 and Landsat-8 dataset, respectively. The two keys are “COPERNICUS/S2_SR” and “LANDSAT/LC08/C02/T1_SR”, which are the catalog names used by GEE for the two datasets. The values corresponding to the two keys are also python dictionary objects including 18 key:value pairs. 
 
### 1.2 Product Options
This python dictionary object includes eight key:value pairs. Each key:value pair contains the information related to one biophysical parameter product. Currently, four biophysical parameters (LAI, fCOVER, fAPAR and Albedo) can be generated with the LEAF production tool  



### 1.3 Parameter Dictionary for Running LEAF Production Tool
The execution of the LEAF production tool requires a number of parameters. To facilitate the transfer of the parameters, a python dictionary structure is utilized as a container. An example of the parameter dictionary is displayed below:

![](/wiki_images/LEAF_param_dict.png)

Specifically, the dictionary includes 9 “key : value” pairs, which are described in detail as follows:

(1) 'sensor: a single integer that represents a satellite sensor. The valid values for this key are 5, 7, 8, 9 and 101, which stand for Landsat 5, 7, 8, 9 and Sentinel-2, respectively. 

(2) 'year' : a 4 digits integer, identifying the year of image acquisition (e.g., 2020).

(3) 'months' : a list of integers (e.g., [6, 7, 8] represent June, July and August). With a list of integers within the range of 1 to 12, several monthly biophysical parameter products can be generated through one execution of the LEAF production tool. If the list contains only one integer with its value outside the range, the biophysical parameter products corresponding to the peak season (June 15 to September 15) of a year (specified by 'year' key) will be produced.

(4) 'prod_names' : a list of strings standing for different biophysical parameters. Currently, LEAF production tool can be used to generate a subset or a full set of 4 biophysical parameters ['LAI', 'fCOVER', 'Albedo', 'fAPAR'].

(5) 'tile_names' : a list of strings representing different tiles. The basic spatial unit of the LEAF production tool is a tile, which is a 900km x 900km area and defined by the Canadian tile griding system. Providing a list of tile names means the biophysical parameter products for multiple tiles can be generated through one execution of the LEAF production tool.

(6) 'spatial_scale' : a single integer defining the spatial resolution (in meter) of exported product maps.

(7) 'location' : a single string specifying the location to export the product maps. There are two valid strings for this parameter, 'drive' and 'storage', representing Google Drive (GD) and Google Cloud Storage (GCS), respectively.

(8) 'bucket' : the name string of a bucket on GCS. This parameter only is used when the value corresponding to the 'location' key is 'storage'.

(9) 'out_folder' : the folder name on GD or GCS for holding a set of exported biophysical parameter maps corresponding to one tile and one year. An empty string for this key means a folder name will be created automatically with a tile name (an element of the list associated with the ‘tile_names’ key) and the acquisition year (the value corresponding to the “year” key).

In summary, of the 9 key:value pairs of the input dictionary, six keys ('sensor', 'year', 'spatial_scale', 'location', 'bucket' and 'out_folder') require a single value, while the other three need a list. With the different combinations between the lists, various production scenarios can be carried out. For instance, to generate monthly (e.g., July and August) biophysical parameter maps for multiple tiles (e.g., 'tile41', 'tile42' and 'tile43'), two lists, [7, 8] and ['tile41', 'tile42', 'tile43'], should be provided for 'months' and 'tile_names' keys.

## 2. Function Call Graph Of LEAF Production Tool

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
