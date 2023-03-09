import ee

import Image as Img
import eoAuxData as eoAD



CLEAR_MASK = 1
WATER_MASK = 2
SNOW_MASK  = 3
SATU_MASK  = 4   #Radiometric satuation




#############################################################################################################
# Description: This function extracts a type of mask from the specific bands in a given image. The masks were
#              created by the image provider.
#
# Revision history:  2022-Jun-22  Lixin Sun  Initial creation
#
#############################################################################################################
def Img_VenderMask(Image, SsrData, MaskType):
  '''This function extracts a specified mask from the intrinsic QA band of a given Landsat image.

     Args:
       Image(ee.Image): a given image with the bands of a specified sensor;
       SensorCode(int): an integer representing a sensor (LS 5, 7, 8, 9 and S2);
       DataUnit(int): an integer representing a data unit (TOA or surface reflectance);
       MaskType(int): the mask type code (CLEAR_MASK, WATER_MASK, SNOW_MASK and SATU_MASK) .'''         
  ssr_code  = SsrData['SSR_CODE']
  data_unit = SsrData['DATA_UNIT']
  mask_type = int(MaskType)  

  if ssr_code > Img.MAX_LS_CODE:  # For Sentinel-2 image
    # For Sentinel-2, only two bands, 'QA60' and 'SCL', include mask information  
    qa  = Image.select(['QA60']).uint16()
    scl = Image.select(['SCL']) if data_unit == 2 else qa.multiply(0)
  
    if mask_type == CLEAR_MASK:
      cloud_mask  = ee.Image.constant(1 << 10)
      cirrus_mask = ee.Image.constant(1 << 11)

      mask = qa.bitwiseAnd(cloud_mask).Or(qa.bitwiseAnd(cirrus_mask))
      return mask.Or(scl.eq(3)).Or(scl.eq(8)).Or(scl.eq(9)).Or(scl.eq(10))
    elif mask_type == WATER_MASK:
      return scl.eq(6)
    elif mask_type == SNOW_MASK:
      return scl.eq(11)
    elif mask_type == SATU_MASK:
      return scl.eq(1)
    else:
      return qa.multiply(ee.Image(0))
  else:   # For Landsat image
    # For Landsat, only one band, 'QA_PIXEL', includes mask information
    qa = Image.select(['QA_PIXEL']).uint16()

    if mask_type == CLEAR_MASK:
      return qa.bitwiseAnd(30)   # extract bit info from 1,2,3,4 bit
    elif mask_type == WATER_MASK:
      return qa.bitwiseAnd(256)
    elif mask_type == SNOW_MASK:
      return qa.bitwiseAnd(64)
    #elif mask_type == SATU_MASK:
      #sa = Image.select(['QA_RADSAT']).uint8()
      #return sa.bitwiseAnd(127)
      #return sa.multiply(0)
    else:
      return qa.multiply(0)





#############################################################################################################
# Description: This function creates a value-invalid pixel mask (1 => invalid value pixels) for an image.
# 
# Revision history:  2022-Nov-11  Lixin Sun  Initial creation
#                    2022-Nov-15  Lixin Sun  Removed the limit that maximum reflectance value must be 100.
#
#############################################################################################################
def Img_ValueMask(Image, SsrData, MaxRef):
  '''Creates a value-invalid pixel mask (1 => value_invalid pixel) for an image.

     Args:
       Image(ee.Image): a given ee.Image object;
       SsrData(Dictionary): A Dictionary with metadata for a sensor and data unit;
       MaxRef(int): a maximum reflectance value (1 or 100).'''
  #===========================================================================================================
  # Extract optical bands 
  #===========================================================================================================
  band_names = SsrData['OUT_BANDS']
  used_img   = Image.select(band_names) 

  #===========================================================================================================
  # Create valid value mask
  #===========================================================================================================
  max_val = ee.Number(1.05).multiply(MaxRef)
  min_val = ee.Number(-0.005).multiply(MaxRef)
  
  mask = used_img.lt(min_val).Or(used_img.gt(max_val))

  return mask.reduce(ee.Reducer.max()).rename(['ValMask'])




#############################################################################################################
# Description: This function creates a vegetation pixel mask (1 => vegetation) for an image.
#
# Revision history:  2022-Nov-11  Lixin Sun  Initial creation
#                    2022-Nov-15  Lixin Sun  Removed the limit that maximum reflectance value must be 100.
# 
#############################################################################################################  
def Img_VegMask(Image, SsrData):
  '''Creates a vegetation pixel mask (1 => vegetation) for an image.

     Args:
       Image(ee.Image): a given ee.Image object;
       SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit.'''
 
  blu  = Image.select(SsrData['BLU'])
  grn  = Image.select(SsrData['GRN'])
  red  = Image.select(SsrData['RED'])

  ndvi = Image.normalizedDifference([SsrData['NIR'], SsrData['RED']])

  return ee.Image(ndvi.gt(ee.Image(0.3)).And(grn.gt(blu)).And(grn.gt(red)))
  





#############################################################################################################
# Description: This function creates a non-vegetated pixel mask (1 => non-vegetated pixels) for an image.
#
# Revision history:  2021-Jul-07  Lixin Sun  Initial creation.
#                    2022-Nov-15  Lixin Sun  Removed the limit that maximum reflectance value must be 100.
#
#############################################################################################################
def Img_NonVegMask(Image, SsrData, MaxRef, indx_name):
  '''Creates a non-vegetated pixel mask for an image.

     Args:
       Image(ee.Image): a given ee.Image object;
       SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
       MaxRef(int): a maximum reflectance value (1 or 100);
       indx_name(string): the name string of build-up index.'''

  red = Image.select(SsrData['RED'])
  nir = Image.select(SsrData['NIR'])  
  sw1 = Image.select(SsrData['SW1'])
  sw2 = Image.select(SsrData['SW2'])
  
  img0 = ee.Image(0)

  if indx_name.find('lxi') > -1:  # the index developed by Lixin Sun
    ndvi = Image.normalizedDifference([SsrData['NIR'], SsrData['RED']])
    nir_thresh = ee.Number(0.08).multiply(MaxRef)
    condition = ndvi.lt(ee.Image(0.3)).And(nir.gt(nir_thresh))   # NDVI < 0.1 and NIR > 8
  
    mask = ndvi.multiply(ee.Image(0))  
    return mask.where(condition, ee.Image(1))
    
  elif indx_name.find('nbi') > -1:  # (SWIR*RED)/NIR
    sw = sw1.add(sw2).divide(ee.Image(2))
    return sw.multiply(red).divide(nir)

  elif indx_name.find('ndbi') > -1: # (SWIR1 - NIR)/(SWIR1 + NIR)
    mask = sw1.subtract(nir).divide(sw1.add(nir))
    return mask.where(mask.lt(img0), img0)

  elif indx_name.find('bui') > -1: # NDBI - NDVI
    ndvi = nir.subtract(red).divide(nir.add(red))
    ndbi = sw1.subtract(nir).divide(sw1.add(nir))
    mask = ndbi.subtract(ndvi)
    
    return mask.where(mask.lt(img0).Or(ndvi.lt(img0)), img0)
  else:
    return red.multiply(img0)

  
 


#############################################################################################################
# Description: The function creates a water mask (1 ==> water) for an image.
#
# Revision history:  2021-Jun-13  Lixin Sun  Initial creation
#                    2022-Nov-15  Lixin Sun  Removed the limit that maximum reflectance value must be 100.
#
#############################################################################################################
def Img_WaterMask(Image, SsrData, MaxRef):
  '''This function creates a water mask (1 => water) for an image.

     Args:
       Image(ee.Image): a given ee.Image object;
       SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
       MaxRef(int): a maximum reflectance value (1 or 100).'''
 
  grn = Image.select(SsrData['GRN'])
  nir = Image.select(SsrData['NIR'])
  sw1 = Image.select(SsrData['SW1'])
  sw2 = Image.select(SsrData['SW2'])

  sw_mean = sw1.add(sw2).divide(2.0)

  # calculate NDWI map
  ndwi = grn.subtract(sw_mean).divide(grn.add(sw_mean))

  # create three tests for determining water pixels 
  sw_mean_thresh = ee.Number(0.02).multiply(MaxRef)
  nir_thresh1    = ee.Number(0.15).multiply(MaxRef)
  nir_thresh2    = ee.Number(0.10).multiply(MaxRef)

  test0 = sw_mean.lt(sw_mean_thresh).And(ndwi.gt(0.3))
  test1 = nir.lt(nir_thresh1).And(ndwi.gt(0.3))
  test2 = nir.lt(nir_thresh2).And(ndwi.gt(0.2))

  intrin_mask = Img_VenderMask(Image, SsrData, WATER_MASK)

  return test0.Or(test1).Or(test2).Or(intrin_mask)





#############################################################################################################
# Description: This function creates a snow pixel mask (1 => snow) for an image.
#
# Revision history:  2022-Jun-14  Lixin Sun  Initial creation
#                    2022-Nov-15  Lixin Sun  Removed the limit that maximum reflectance value must be 100.
# 
#############################################################################################################
def Img_SnowMask(Image, SsrData, MaxRef):
  '''Creates a snow/ice pixel mask (1 => snow/ice) for an image.

     Args:
       Image(ee.Image): a given ee.Image object;
       SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
       MaxRef(int): a maximum reflectance value (1 or 100).'''

  grn  = Image.select(SsrData['GRN'])  
  ndsi = Image.normalizedDifference([SsrData['GRN'], SsrData['SW1']])

  grn_thresh = ee.Number(0.1).multiply(MaxRef)
  data_mask = ee.Image(ndsi.gt(0.2).And(grn.gt(grn_thresh)))  
  
  intrin_mask = Img_VenderMask(Image, SsrData, SNOW_MASK)

  return data_mask.Or(intrin_mask)


 



#############################################################################################################
# Description: This function creates a valid pixel mask (mask out cloud, shadow, invalid value and saturated
#              pixels)for an image.
#
# Note:        The given image could be acquired either by a Sentinel-2 or a Landsat sensor.
#
# Revision history:  2020-Dec-20  Lixin Sun  Initial creation.
#                    2022-Jun-24  Lixin Sun  Modified according to the changes of the called functions.
#                    2022_Jul-26  Lixin Sun  Replaced "Img_VenderMask" for CLEAR_MASK with "Img_ClearMask", 
#                                            which includes customized cloud and shadow detections.
#############################################################################################################
def Img_ValidMask(Image, SsrData, MaxRef):
  '''Creates a valid pixel mask (mask out cloud, shadow, invalid value and saturated pixels) for an image.

     Args:
       Image(ee.Image): a given ee.Image object;
       SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
       MaxRef(int): a maximum reflectance value (1 or 100).'''

  clear_mask = Img_VenderMask(Image, SsrData, CLEAR_MASK)
  satur_mask = Img_VenderMask(Image, SsrData, SATU_MASK)
  value_mask = Img_ValueMask (Image, SsrData, MaxRef)

  return clear_mask.Or(satur_mask).Or(value_mask).rename(['ValidMask'])
  #return clear_mask.Or(value_mask).rename(['ValidMask'])




  

#############################################################################################################
# Description: This function creates a mask that mask out the land outside Canada and optionally water based
#              on a land cover map.
#
# Revision history:  2023-Feb-16  Lixin Sun  Initial creation.
#
#############################################################################################################
def Can_land_mask(Year, mask_water):
  '''Creates a mask that mask out the land outside Canada and optionally water.

     Args:      
       Year(int or string): A target year;
       mask_water(Boolean): Flag indicating if water bodies are masked out as well.'''
  #==========================================================================================================
  # Choose a proper land cover image collection based on a given "Year"
  #==========================================================================================================
  Can_LC = eoAD.get_CanLC(int(Year)).uint8()
  
  if mask_water == True:
    Can_LC = Can_LC.where(Can_LC.gt(17), ee.Image(0))  #class ID = 18 and 19 represent water and snow/ice, respectively

  #mask = ccrs_LC.selfMask()  # Mask ouit pixels with value equal to zero
  mask = Can_LC.where(Can_LC.gt(0), ee.Image(1))

  # Perform an erosion followed by a dilation
  box = ee.Kernel.circle(radius = 1, units = 'pixels', normalize = True)
  mask = mask.focalMin(kernel = box, iterations = 1).focalMax(kernel = box, iterations = 1)

  return mask.unmask()
