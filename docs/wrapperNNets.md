## wrapperNNets(networks, partition, prod_options, coll_options, suffix_name, image)
### Description
This function applies a set of shallow LEAF networks to an image based on a given land cover map covering the same region.
### Arguments:
(1) networks(ee.List): a 2-dimensional matrix of LEAF networks (ee.Dictionary objects) with rows and columns corresponding to different biophysical parameters and land cover types, respectively.

(2) partition(ee.Image): a land cover classification map covering ROI.

(3) prod_options(ee.Dictionary): a dictionary containing information related to a selected parameter type.

(4) coll_options(ee.Dictionary): a dictionary containing information related to a selected satellite type.

(5) suffix_name(string): a suffix name of outputs.

(6) image(ee.Image): a given mosaic image from which a biophysical parameter map will be extracted.
### Returns:
This function returns a resultant image (ee.Image object) containing three bands, a biophysical parameter map, a land cover map and a network index map. 
