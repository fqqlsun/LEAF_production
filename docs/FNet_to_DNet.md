## FNet_to_DNet(feature_list, class_ID)
### Description
This function converts a given LEAF network in ee.Feature format to a network in ee.Dictionary format with 8 keys (“inpSlope”, “inpOffset”, “h1wt”, “h1bi”, “h2wt”, “h2bi”, “outSlope”, “outBias”).
### Arguments:
(1) feature_list (ee.List): a list of LEAF networks (with ee.Feature objects as elements) for one biophysical parameter and multiple land cover types.

(2) class_ID (ee.Number): the ID number of a specified land cover type.
### Returns:
This function returns a shallow LEAF neural network saved in a ee.Dictionary object with 8 keys.
