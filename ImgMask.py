import ee

import Image as Img
import eoAuxData as eoAD



CLEAR_MASK = 1
WATER_MASK = 2
SNOW_MASK  = 3
SATU_MASK  = 4   #Radiometric satuation




#############################################################################################################
# Description: This function creates a clear-sky pixel mask for a given image (Image) based on the comparison
#              with a MODIS mosaic image (MODIS_mosaic).
#
# Revision history:  2023-Apr-14  Lixin Sun  Initial creation
#                    2023-May-25  Lixin Sun  Treat high spatial resolution vegetated and non-vegetated 
#                                            pixels differently.
#############################################################################################################
def mask_from_MODIS(Image, SsrData, MODIS_mosaic): 
  '''This function creates a clear-sky pixel mask for a given image (Image) based on the comparison with a
     MODIS mosaic image (MODIS_mosaic)

     Args:
       Image(ee.Image): a given Sentinel-2 or Landsat image;
       SsrData(Dictionary): an sensor data dictionary;
       MODIS_mosaic(ee.Image): an compariable MODIS mosaic image.'''    
  #==========================================================================================================
  # Apply gain and offset to both MODIS and S2/LS images
  #==========================================================================================================
  modis_ssrData = Img.SSR_META_DICT['MOD_SR']
  modis = Img.apply_gain_offset(MODIS_mosaic, modis_ssrData, 100.0, False)
  image = Img.apply_gain_offset(Image, SsrData, 100.0, False)

  #==========================================================================================================
  # Obtain related bands in high-resolution image and then calculate NDVI map
  #==========================================================================================================
  s2ls_blu  = image.select(SsrData['BLU'])
  s2ls_red  = image.select(SsrData['BLU'])
  s2ls_nir  = image.select(SsrData['NIR'])
  ndvi      = s2ls_nir.subtract(s2ls_red).divide(s2ls_nir.add(s2ls_red))

  #==========================================================================================================
  # Create two adjustment maps for BLUE and NIR bands, respectively 
  # For a high-resolution vegetated pixel, its blu <= MODIS_blue
  # For a high-resolution non-vegetated pixel, its blu >= MODIS_blue
  # For a high-resolution vegetated pixel, its NIR >= MODIS_NIR
  # For a high-resolution non-vegetated pixel, its NIR <= MODIS_NIR
  #==========================================================================================================
  blu_adjust = s2ls_blu.multiply(0).add(2)
  blu_adjust = blu_adjust.where(ndvi.lt(0.4), blu_adjust.add(3)) 
  
  nir_adjust = s2ls_nir.multiply(0).add(5)
  nir_adjust = nir_adjust.where(ndvi.lt(0.4), blu_adjust.subtract(3))

  #==========================================================================================================
  # Apply blue and NIR adjustment images to MODIS blue and NIR bands, respectively
  #==========================================================================================================
  modis_blu = modis.select(modis_ssrData['BLU']).add(blu_adjust)
  modis_nir = modis.select(modis_ssrData['NIR']).subtract(nir_adjust)

  #==========================================================================================================
  # Create a pixel mask
  #==========================================================================================================
  mask = s2ls_blu.multiply(0)
  
  cond = s2ls_blu.gt(modis_blu).Or(s2ls_nir.lt(modis_nir))
  mask = mask.where(cond, ee.Image(1))

  return cond




#############################################################################################################
# Description: Returns a clear-sky mask (1 indicates cloud/cloud shadow) for a given Sentinel-2 image
#
# Revision history:  2023-Dec-02  Lixin Sun  Created for usable in the "map" function
# 
#############################################################################################################
def S2_ClearMask(inImg, inUnit):
  # For Sentinel-2, only two bands, 'QA60' and 'SCL', include mask information  
  qa  = inImg.select(['QA60']).uint16()

  scl = ee.Image.constant(0)
  scl = scl.where(ee.Number(inUnit).eq(2), inImg.select(['SCL']))

  cloud  = ee.Image.constant(1 << 10)   # Opaque clouds
  cirrus = ee.Image.constant(1 << 11)   # Cirrus clouds

  mask = qa.bitwiseAnd(cloud).Or(qa.bitwiseAnd(cirrus))
  return mask.Or(scl.eq(3)).Or(scl.eq(8)).Or(scl.eq(9)).Or(scl.eq(10))

  

#############################################################################################################
# Description: Returns a clear-sky mask (1 indicates cloud/cloud shadow) for a given Landsat image
#
# Revision history:  2023-Dec-02  Lixin Sun  Created for usable in the "map" function
# 
#############################################################################################################
def LS_ClearMask(inImg):
  # For Landsat series images, only 'QA_PIXEL' band includes mask information  
  qa = inImg.select(['QA_PIXEL']).uint16()
  dilated = ee.Image.constant(1 << 1)
  cirrus  = ee.Image.constant(1 << 2)
  cloud   = ee.Image.constant(1 << 3)
  shadow  = ee.Image.constant(1 << 4)
  
  return qa.bitwiseAnd(dilated).Or(qa.bitwiseAnd(cirrus)).Or(qa.bitwiseAnd(cloud)).Or(qa.bitwiseAnd(shadow))
      


#############################################################################################################
# Description: Returns a clear-sky mask (1 indicates cloud/cloud shadow) for a given HLS image
#
# Revision history:  2023-Dec-02  Lixin Sun  Created for usable in the "map" function
# 
#############################################################################################################
def HLS_ClearMask(inImg):
  # For a harminized Landsat Sentinel image, only 'Fmask' band includes mask information  
  qa = inImg.select(['Fmask']).uint8()            
  cloud  = ee.Image.constant(1 << 1)
  AdjCS  = ee.Image.constant(1 << 2)
  shadow = ee.Image.constant(1 << 3) 
  AOT    = ee.Image.constant(1 << 7)

  return qa.bitwiseAnd(cloud).Or(qa.bitwiseAnd(shadow))  #.Or(qa.bitwiseAnd(AdjCS)).Or(qa.bitwiseAnd(AOT))
  #return qa.bitwiseAnd(cloud).Or(qa.bitwiseAnd(AdjCS)).Or(qa.bitwiseAnd(shadow)).Or(qa.bitwiseAnd(AOT))





#############################################################################################################
# Description: This function extracts a type of mask from the specific bands in a given image. The masks were
#              created by the image provider.
#
# Note:        The returned mask is a 0/1 image with 1 represening specified targets (e.g., cloud, cirrus,
#              shadow, water or snow/ice). This is in reverse with the required mask for "updateMask" function
#              of ee.Image object.
#
# Revision history:  2022-Jun-22  Lixin Sun  Initial creation
#                    2023-Jan-11  Lixin Sun  Added MODIS sensor code option and MODIS mosaic image.
#                    2023-Nov-30  Lixin Sun  Added mask option for harmonized Landsat and Sentinel-2 images
#
#############################################################################################################
def Img_VenderMask(Image, SsrData, MaskType, MODIS_mosaic = None):
  '''This function extracts a specified mask from the intrinsic QA band of a given Landsat image.

     Args:
       Image(ee.Image): a given image with the bands of a specified sensor;
       SsrData(Dictionary): a dictionary containing some info on a sensor  (LS 5/7/8/9 and S2);       
       MaskType(int): the mask type code (CLEAR_MASK, WATER_MASK, SNOW_MASK and SATU_MASK);
       MODIS_mosaic(ee.Image): An optional MODIS mosaic image.'''         
 
  ssr_code  = SsrData['SSR_CODE']
  data_unit = SsrData['DATA_UNIT']
  mask_type = int(MaskType)  

  if ssr_code == Img.MOD_sensor:  # For MODIS image
    cloudShadow = ee.Image.constant(1 << 2)
    cirrus1     = ee.Image.constant(1 << 8)
    cirrus2     = ee.Image.constant(1 << 9)
    cloud       = ee.Image.constant(1 << 10)
    snow        = ee.Image.constant(1 << 12)
    cloud2      = ee.Image.constant(1 << 13)
    snow2       = ee.Image.constant(1 << 15)

    qa = Image.select('StateQA')
    # Both flags should be set to zero, indicating clear conditions.
    mask = qa.bitwiseAnd(cloudShadow).Or(qa.bitwiseAnd(cirrus1)).Or(qa.bitwiseAnd(cirrus2)) \
          .Or(qa.bitwiseAnd(cloud)).Or(qa.bitwiseAnd(snow)).Or(qa.bitwiseAnd(cloud2)).Or(qa.bitwiseAnd(snow2))
    
    return mask
  elif ssr_code > Img.MAX_LS_CODE and ssr_code < Img.MOD_sensor:  # For Sentinel-2 image
    if mask_type == CLEAR_MASK:
      return S2_ClearMask(Image, data_unit)
    else:
      scl = ee.Image.constant(0)
      scl = scl.where(ee.Number(data_unit).eq(2), Image.select(['SCL']))

      if mask_type == WATER_MASK:
        return scl.eq(6)
      elif mask_type == SNOW_MASK:
        return scl.eq(11)
      elif mask_type == SATU_MASK:
        return scl.eq(1)
      else:
        return ee.Image.constant(0)
      
  elif ssr_code < Img.MAX_LS_CODE:   # For both BOA and TOA reflectance data of Landsat 5/7/8/9
    # For Landsat, only 'QA_PIXEL' band includes mask information
    if mask_type == CLEAR_MASK:
      return LS_ClearMask(Image)
    
    else:
      qa = Image.select(['QA_PIXEL']).uint16()
      if mask_type == WATER_MASK:
        water = ee.Image.constant(1 << 7)
        return qa.bitwiseAnd(water)   # Bit 7: Water
      elif mask_type == SNOW_MASK:
        snow = ee.Image.constant(1 << 5)
        return qa.bitwiseAnd(snow)    # Bit 5: Snow
      elif mask_type == SATU_MASK:
        sa = Image.select(['QA_RADSAT']).uint8()
        mask = sa.bitwiseOr(0)
        return mask.where(mask.gt(0), ee.Image.constant(1))
        
  elif ssr_code == Img.HLS_sensor:    
    if mask_type == CLEAR_MASK:
      return HLS_ClearMask(Image)
    else:
      qa = Image.select(['Fmask']).uint8()            
      if mask_type == WATER_MASK:
        water = ee.Image.constant(1 << 5)
        return qa.bitwiseAnd(water)   # Bit 7: Water
      elif mask_type == SNOW_MASK:
        snow   = ee.Image.constant(1 << 4)
        return qa.bitwiseAnd(snow)    # Bit 5: Snow        
      else:
        return ee.Image.constant(0)    
    




#############################################################################################################
# Description: This function creates a value-invalid pixel mask (1 => invalid value pixels) for an image.
# 
# Revision history:  2023-Nov-10  Lixin Sun  Initial creation
#
#############################################################################################################
def Img_ClearMask(Image, SsrData):
  '''Creates a value-invalid pixel mask (1 => value_invalid pixel) for an image.

     Args:
       Image(ee.Image): a given ee.Image object;
       SsrData(Dictionary): A Dictionary with metadata for a sensor and data unit;
       MaxRef(int): a maximum reflectance value (1 or 100).'''
  ssr_code  = SsrData['SSR_CODE']
  
  if ssr_code > Img.MAX_LS_CODE: # for Sentinel-2 data   
    img_foot = Image.geometry()
    csPlus   = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED').filterBounds(img_foot)
    
    img      = Image.linkCollection(csPlus, ['cs'])

    return img.select('cs').lt(0.6)
  
  else: # for Landsat data
    return Img_VenderMask(Image, SsrData, CLEAR_MASK)






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
# Description: This function creates a snow/ice pixel mask (1 => snow/ice) for a given image containing 
#              spectral bands with standard names, such as blue, green, red, NIR, SWIR1 and SWIR2.
#
# Revision history:  2024-Apr-15  Lixin Sun  Initial creation
# 
#############################################################################################################
def STDImg_SnowCloudMask(inSTD_Img, MaxRef):
  '''Creates a snow/ice pixel mask (1 => snow/ice) for an image.

     Args:
       inSTD_Img(ee.Image): a given ee.Image object containing spectral bands with standard names;
       MaxRef(int): a maximum reflectance value (1 or 100).'''
    
  blu = inSTD_Img.select('blue')
  grn = inSTD_Img.select('green')
  red = inSTD_Img.select('green')
  nir = inSTD_Img.select('nir')
  sw1 = inSTD_Img.select('swir1')
  sw2 = inSTD_Img.select('swir2')  

  max_SV = blu.max(grn)
  max_SW = sw1.max(sw2)

  ndwi = max_SV.subtract(max_SW).divide(max_SV.add(max_SW))
  
  nir_thresh = 10 if MaxRef > 10 else 0.1
  snow_mask = ee.Image(ndwi.gt(0.5).And(nir.gt(nir_thresh)))

  HOT        = blu.subtract(red.multiply(0.5).add(8))
  cloud_mask = ee.Image(HOT.gt(0).And(max_SV.gt(20)))

  return snow_mask.where(cloud_mask.gt(0), cloud_mask)
  
 



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

  #print('clear_mask bands = ', clear_mask.bandNames().getInfo())
  #print('satue_mask bands = ', satur_mask.bandNames().getInfo())
  #print('value_mask bands = ', value_mask.bandNames().getInfo())


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




##############################################################################################################
# Description: This function extracts a water map from Global water map based on boundary of a given image.
#
##############################################################################################################
def WaterMask(img):
  GL_water = eoAD.get_GlobWater(10)
  GL_water = GL_water.where(GL_water.gt(0), ee.Image.constant(1))

  water_mask = img.select([0]).multiply(0)
  return water_mask.add(GL_water)