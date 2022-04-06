## applyNet(image, net_list, band_names, band_scales, net_indx, output_name)
### Description
This function applies a specified LEAF network to a subset of pixels determined by the network index (equivalent to one land cover type).
### Arguments:
(1) image(ee.Image): a given mosaic image with an additional “networkID” band attached.

(2) net_list(ee.List): a list of LEAF networks for one bio-parameter and multiple land covers.

(3) band_names(ee.List): the name list of the bands in the given mosaic image.

(4) band_scales(ee.List): a list of scaling factors for the bands in the given mosaic image.

(5) net_indx(ee.Number): the index of a specified LEAF network in “net_list”.

(6) output_name(ee.String): the name of the band containing output results.
### Returns:
A single band image named by “output_name” and containing output results.
