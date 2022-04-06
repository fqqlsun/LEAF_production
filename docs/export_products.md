## export_products(fun_param_dict, mapBounds, estimateImage, errorImage, task_list)
### Description
This function exports two maps, an estimated biophysical parameter map and an uncertainty map, to a specified location (Google Drive or Google Cloud Storage). The filenames of the exported images will be automatically generated based on tile name, image acquisition time, parameter type and spatial resolution of the product.
### Arguments:
(1) fun_param_dict(dictionary): a python dictionary with parameters saved as “key : value” pairs. Note the values corresponding to the keys are all single values (one combination of the values of “exe_param_dict”). 

(2) mapBounds(ee.Geometry): the spatial region of interest. 

(3) estimateImage(ee.Image): an estimated biophysical parameter map.

(4) errorImage(ee.Image): the uncertainty map corresponding to the estimated biophysical parameter map.

(5) task_list([]): a python list storing the links to all exporting tasks.
### Returns:
Nothing is returned from this function. Instead, “task_list” argument is modified by adding the links to two new exporting tasks. 
