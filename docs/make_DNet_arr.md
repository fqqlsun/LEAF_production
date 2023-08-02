## make_DNet_arr(all_nets, numClasses, paramID)
### Description
This function creates an array of LEAF networks, where each of them is an ee.Dictionary objects. These networks can be directly applied to compute one biophysical parameter map for diverse land cover types. Note that the format of the LEAF networks in input and output are different. The LEAF networks in “all_nets” are saved as ee.Feature objects, while the LEAF networks in the returned list are saved as ee.Dictionary objects. Only the networks in ee.Dictionary format can be directly applied in the calculation of biophysical parameters.
### Arguments:
(1) all_nets(ee.FeatureCollection): all the LEAF networks (ee.Feature objects) for different biophysical parameters and various land cover types.

(2) numClasses(ee.Number): the total number of land cover types.

(3) paramID(ee.Number): the ID number of a particular biophysical parameter.
### Returns:
A list of LEAF networks (ee.Dictionary objects) directly applicable in the calculation of one biophysical parameter map for diverse land cover types.
