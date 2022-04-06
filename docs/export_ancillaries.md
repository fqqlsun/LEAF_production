## export_ancillaries(mosaic, fun_param_dict, mapBounds, task_list)
### Description
This function exports three ancillary maps (Date, QC and Partition) associated with a set of biophysical maps.
### Arguments:
(1) mosaic(ee.Image): a special mosaic image created by “LEAF_mosaic” function.

(2) fun_param_dict(dictionary): a python dictionary storing most required parameters.

(3) mapBounds(ee.Geometry): a spatial region for biophysical parameter extraction.

(4) task_list([]): a python list for storing the exporting tasks.
### Returns:
Nothing will be returned from this function. However, “task_list” argument will be modified by adding the links to two new exporting tasks.
