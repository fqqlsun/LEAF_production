## makeIndexLayer(partition, numb_classes, legend, network_IDs)
### Description
This function creates a single band image (ee.Image object) named “networkID” that maps the network IDs to be applied to each pixel. The network ID for each pixel is determined by its land cover type.  
### Arguments:
(1) partition(ee.Image): an existing land cover map covering ROI.

(2) numb_classes(ee.Number): the total number of the classes in the land cover map.

(3) legend(ee.FeatureCollection): the legends of land cover types.

(4) network_IDs(ee.FeatureCollection): the legends of network IDs.
### Returns:
A single band image (ee.Image object) named “networkIDs” and mapping the network IDs to be applied to each pixel. 
