## LEAF_Mosaic(fun_param_dict, mapBounds)
### Description
This function creates a mosaic image (a ee.Image object) specially for biophysical parameter extraction using the LEAF production tool. Depending on the used satellite images, the mosaic image created by this function contains a different number of bands. When Sentinel-2 data is used, the mosaic image contains 11 bands, 3 imaging geometry (cos(VZA), cos(SZA) and cos(RAA)) bands and 8 spectral bands (B3, B4, B5, B6, B7, B8, B11 and B12). When Landsat 8 data is used, the mosaic image contains 8 bands, 3 imaging geometry bands (the same as above) and 5 spectral bands (B3, B4, B5, B6 and B7). 
### Arguments:
(1) fun_param_dict (dictionary): a dictionary containing a number of parameters. Note that the dictionary used here is different from that used by the “LEAF_tool_main” function. Both dictionaries contain the same number (nine) of parameters, but only a single value is defined for each key in this dictionary. In other words, a dictionary used here is just one combination of the values of the dictionary used by the “LEAF_tool_main” function. 

(2) mapBounds (ee.Geometry): a spatial region for creating a mosaic image (equivalent to the region for biophysical parameter extraction).
### Returns:
This function returns a ee.Image object containing all bands required for biophysical parameter extraction.
