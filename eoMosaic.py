######################################################################################################
# Description: The code in this file was initially created with JavaScript and then was converted to
#              to Python in April 2021. Modifications were also made after the code conversion.
#
######################################################################################################
import ee 


import eoImage as eoImg
import eoImgSet as eoImgSet
import eoImgMask as eoIM
import eoTileGrids as eoTileGD
import eoWaterMap as eoWaterMap
import eoClassfyUtils as eoCU
import eoGapFilling as eoGF
import eoAuxData as eoAD


# The integer code for the band types to be attached to images
EXTRA_NONE  = 0
EXTRA_ANGLE = 1
EXTRA_NDVI  = 2



######################################################################################################
# Description: This function creates a map with all the pixels having an identical time score for a
#              given image. Time score is calculated based on the date gap between the acquisition
#              date of the given image and a reference date (midDate parameter), which normally is
#              the middle date of a time period (e.g., a peak growing season).
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def get_time_score(image, midDate, ssr_code):
  '''Return a time score image corresponding to a given image
  
     Args:
        image (ee.Image): A given ee.Image object to be generated a time score image.
        midData (ee.Date): The centre date of a time period for a mosaic generation.
        ssr_code (int): The sensor type code.'''
  #==================================================================================================
  # Calculate the date difference betwen the given image and a reference date
  #==================================================================================================
  img_date   = ee.Date(image.date()).millis().divide(86400000)
  refer_date = ee.Date(midDate).millis().divide(86400000)
  date_diff  = img_date.subtract(refer_date).abs()

  #==================================================================================================
  # Calculatr time score according to sensor type (Sentinel-2: sensor_code > 100
  # Landsat: ssr_code < 100)
  #==================================================================================================
  ssr_code = int(ssr_code)

  factor  = ee.Image(50) if ssr_code > eoImg.MAX_LS_CODE else ee.Image(100)  
  one_img = image.select([0]).multiply(ee.Image(0)).add(ee.Image(1.0))

  return one_img.divide((ee.Image(date_diff).divide(ee.Image(factor))).exp())





######################################################################################################
# Description: This function creates a pixel score image corresponding to vegetation targets
#
# Note:        This function assumes the value range of the given image is between 0 and 100
#
# Revision history:  2022-Mar-15  Lixin Sun  Initial creation
#
######################################################################################################
def get_veg_score(blu, grn, red, nir, sw2, data_unit):
  '''Return a pixel score image corresponding to vegetation targets
  
  Args:
  '''  
  #==================================================================================================
  # Calculate main spectral score
  #==================================================================================================
  blu_offset = ee.Image(5.0) if ee.Number(data_unit).eq(2) else ee.Image(0.0)
  veg_score  = nir.divide(blu.add(blu_offset))
  
  #==================================================================================================
  # Calculate greeness score and incorporate it into spectral score
  ##==================================================================================================
  grn_score    = grn.divide(blu).add(grn.divide(red)).divide(ee.Image(2.0))
  invalid_cond = grn_score.gt(ee.Image(3.0)).Or(grn_score.lt(ee.Image(1.0)))
  
  grn_score    = grn_score.where(invalid_cond, ee.Image(0.0))
  veg_score    = veg_score.where(veg_score.gt(grn_score), veg_score.add(grn_score))

  #==================================================================================================
  # Calculate blue band penalty and incorporate it into spectral score
  #==================================================================================================
  model_offset = ee.Image(1.2) if ee.Number(data_unit).eq(2) else ee.Image(6.2)
  blu_refer    = sw2.multiply(ee.Image(0.17)).add(model_offset)
  blue_penalty = blu.subtract(blu_refer).abs().divide(ee.Image(2.0))
  
  return veg_score.subtract(blue_penalty)





######################################################################################################
# Description: This function creates a pixel score image corresponding to vegetation targets
#
# Note:        This function assumes the value range of the given image is between 0 and 100
#
# Revision history:  2022-Mar-15  Lixin Sun  Initial creation
#                    
######################################################################################################
def get_nonveg_score(blu, grn, red, sw1, median_blu):
  '''Return a pixel score image corresponding to vegetation targets
  
  Args:
  '''
  #==================================================================================================
  # Calculate main spectral score
  #==================================================================================================
  min_visible = blu.min(grn).min(red)
  max_visible = blu.max(grn).max(red)
  
  non_veg_score   = sw1.subtract(min_visible).divide(sw1.add(min_visible))
  max_visible_sw1 = sw1.subtract(max_visible).divide(sw1.add(max_visible))
  max_score       = ee.Image(1.1).subtract(max_visible_sw1.abs()).multiply(ee.Image(-1.0))
  
  non_veg_score = non_veg_score.where(min_visible.lt(ee.Image(2.0)), max_score)

  #==================================================================================================
  # Apply blue band penalty for bright targets in blue band
  #==================================================================================================  
  blue_penalty = blu.subtract(median_blu).abs().divide(ee.Image(5.0))
  
  #condition = blu.gt(ee.Image(15.0)).And(median_blu.lt(ee.Image(30.0)))
  non_veg_score = non_veg_score.where(blu.gt(ee.Image(15.0)), non_veg_score.subtract(blue_penalty))
  
  #==================================================================================================
  # Apply dark penalty
  #==================================================================================================
  min_sw1       = ee.Image(20.0)
  dark_penalty  = sw1.subtract(min_sw1).abs().divide(ee.Image(5.0))
  
  non_veg_score = non_veg_score.where(sw1.lt(min_sw1), non_veg_score.subtract(dark_penalty))
  
  #==================================================================================================
  # Dealing with ice/snow. !!!The following code should be applied because it will affect the mosaic
  # results of bright urban targets!!!
  #==================================================================================================
  #ir_mean  = nir.add(sw1).add(sw2).divide(ee.Image(3.0))
  #ice_snow = blu.gt(ee.Image(15.0)).And(max_visible_sw1.lt(ee.Image(0.0)))
  
  #non_veg_score = non_veg_score.where(ice_snow, ir_mean.multiply(-1.0))
  
  return non_veg_score





def get_water_score(nir, sw1, sw2):
  IR_mean     = (nir.add(sw1).add(sw2)).divide(ee.Image(3.0))

  #water_score = blu.divide(red).subtract(IR_mean).subtract(ee.Image(1.0))  
  #water_score = water_score.where(blu.lt(ee.Image(0.5)), water_score.multiply(-1.0))
  
  return IR_mean.multiply(ee.Image(-1.0))






######################################################################################################
# Description: This function creates a combined (spectral and time) score map for a given image
#              (either TOA or surface reflectance).
#
# Note:        (1) This function assumes the value range of the given image is between 0 and 100
#              (2) The value range of "median_blue" is already in between 0 and 100
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#                    2022-Mar-15  Lixin Sun  
######################################################################################################
def get_score_map(median_blue, inMidDate, ssr_code, data_unit, image):
  '''Return a pixel score image corresponding to a given image
  
  Args:      
      median_blue(ee.Image): The blue band of a median mosaic. Could be used as the blue reference for non-veg pixels.   
      inMidDate(ee.Date): The centre date of a time period for a mosaic generation.
      ssr_code(int): The sensor type code.
      data_unit(int): The integer representing data unit (1 and 2 => TOA and surface reflectance).
      image(ee.Image): A given ee.Image object to be generated a time score image.
  '''
  #==================================================================================================
  # Create a new image (STD_img) that contains only SIX critical bands, meanwhile rename the bands
  #==================================================================================================
  STD_img = eoImg.get_STD_image(image, ssr_code, data_unit)
  STD_img = eoImg.apply_gain_offset(STD_img, ssr_code, data_unit, 100, True).toFloat()

  #==================================================================================================
  # Update the mask of "STD_img" to mask out cloud, shadow, saturated and out-of-range pixels.
  # 
  # Note: (1) in 'valid_mask', invalid pixels are marked with 1, while "updateMask" function requires
  #           invalid pixels are marked with 0. 
  #       (2) "valid_mask" is created based on "image", which is a raw ee.Image object, meaning 
  #           image's value range exceeds [0, 100]. So 1000 is given as the last parameter to 
  #           "Img_ValidMask" function. 
  #==================================================================================================  
  valid_mask = eoIM.Img_ValidMask(image, ssr_code, data_unit, 1000).Not()

  STD_img    = STD_img.updateMask(valid_mask) # 1 represents valid/clear-sky pixels 

  #==================================================================================================
  # Create separate references for each of the SIX bands
  #==================================================================================================
  blu = STD_img.select('blue')
  grn = STD_img.select('green')
  red = STD_img.select('red')
  nir = STD_img.select('nir')
  sw1 = STD_img.select('swir1')
  sw2 = STD_img.select('swir2')

  #print('<get_score_map> STD image bands after updating mask = ', STD_img.bandNames().getInfo())
  #==================================================================================================
  # Calculate cloud coverage score
  #==================================================================================================
  #ssr_props   = eoImg.get_sensor_properties(ssr_code)
  #cloud_cover = image.getNumber(ssr_props['Cloudcover'])
  #cld_score   = ee.Image(ee.Number(100).subtract(ee.Number(cloud_cover)))

  veg_score_map    = get_veg_score(blu, grn, red, nir, sw2, data_unit) #.add(cld_score.divide(ee.Image(100)))
  nonveg_score_map = get_nonveg_score(blu, grn, red, sw1, median_blue) #.add(cld_score.divide(ee.Image(200)))

  NDVI_img  = nir.subtract(red).divide(nir.add(red))
  score_map = veg_score_map.where(NDVI_img.lt(ee.Image(0.3)), nonveg_score_map)
  
  #==================================================================================================
  # Adjust the scores of some invalid (extremely bright) or shadow (NDVI < 0) pixels
  #==================================================================================================
  max_ref   = ee.Image(100.0)
  min_ref   = ee.Image(1.0) 

  bad_pixs  = blu.gt(max_ref).Or(grn.gt(max_ref)).Or(red.gt(max_ref)) \
             .Or(blu.lt(min_ref)).Or(grn.lt(min_ref)).Or(red.lt(min_ref)) 
             #.Or(NDVI_img.lt(ee.Image(0.0)))

  score_map = score_map.where(bad_pixs, blu.multiply(ee.Image(-1.0)))
  score_map = score_map.add(NDVI_img)

  #==================================================================================================
  # Apply time scores to vegetation targets 
  #==================================================================================================
  time_score = get_time_score(image, inMidDate, ssr_code)
  score_map  = score_map.multiply(time_score)

  #==================================================================================================
  # For water/icy pixels apply water/ice scores (mean infrared, this step must be done last)
  #==================================================================================================
  water_mask  = eoWaterMap.WaterMask(image)    
  water_score = get_water_score(nir, sw1, sw2)

  return score_map.where(water_mask, water_score)





######################################################################################################
# Description: This function creates a combined (spectral and time) score map for a given image
#              (either TOA or surface reflectance).
#
# Note:        This function assumes the value range of the given image is between 0 and 100
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#                    2022-Mar-15  Lixin Sun  
######################################################################################################
def mosaic_score_map(image, ssr_code, data_unit):
  '''Return a pixel score image corresponding to a given image
  
  Args:      
      image(ee.Image): A given ee.Image object to be generated a time score image;
      ssr_code(int): The sensor type code;
      data_unit(int): The integer representing data unit (1 and 2 => TOA and surface reflectance).'''

  #==================================================================================================
  # Create a new image (STD_img) that contains only SIX critical bands, meanwhile rename the bands
  #==================================================================================================
  STD_img  = eoImg.get_STD_image(image, ssr_code, data_unit)
  #STD_max  = STD_img.reduce(ee.Reducer.max())
  #pix_mask = STD_max.gt(ee.Image(0.1))

  #==================================================================================================
  # Create separate references for each of the SIX critical bands
  #==================================================================================================
  blu = STD_img.select('blue')
  grn = STD_img.select('green')
  red = STD_img.select('red')
  nir = STD_img.select('nir')
  sw1 = STD_img.select('swir1')
  sw2 = STD_img.select('swir2')
  
  #==================================================================================================
  # Calculate cloud coverage score
  #==================================================================================================
  veg_score_map  = get_veg_score(blu, grn, red, nir, sw2, data_unit) #.add(cld_score.divide(ee.Image(100)))
  zero_score_map = sw2.multiply(ee.Image(0.0)) #.add(cld_score.divide(ee.Image(200)))

  NDVI_img  = nir.subtract(red).divide(nir.add(red))
  score_map = veg_score_map.where(NDVI_img.lt(ee.Image(0.3)), zero_score_map)
  
  #==================================================================================================
  # Adjust the scores of some invalid (extremely bright) or shadow (NDVI < 0) pixels
  #==================================================================================================
  max_ref   = ee.Image(100.0)
  min_ref   = ee.Image(1.0) 

  bad_pixs  = blu.gt(max_ref).Or(grn.gt(max_ref)).Or(red.gt(max_ref)) \
             .Or(blu.lt(min_ref)).Or(grn.lt(min_ref)).Or(red.lt(min_ref)) 

  score_map = score_map.where(bad_pixs, blu.multiply(ee.Image(-1.0)))
  score_map = score_map.add(NDVI_img)

  #==================================================================================================
  # For water/icy pixels apply water/ice scores (mean infrared, this step must be done last)
  #==================================================================================================
  water_mask  = eoWaterMap.WaterMask(image)    
  water_score = get_water_score(nir, sw1, sw2)

  return score_map.where(water_mask, water_score)





'''
def get_neg_blue_map(ssr_code, data_unit, image):  
  #==================================================================================================
  # Create a new image cube (STD_img) that contains only SIX critical bands, meanwhile rename bands
  #==================================================================================================
  valid_mask = eoImgMsk.ValidMask (image, ssr_code, data_unit)
  STD_img    = eoImg.get_STD_image(image, ssr_code, data_unit)
  STD_img    = eoImg.apply_gain_offset(STD_img, ssr_code, data_unit, 100, True).toFloat()
  STD_img    = STD_img.updateMask(valid_mask)  

  #==================================================================================================
  # Create a reference image for each of the SIX critical bands
  #==================================================================================================
  blu_img = STD_img.select('blue')
  
  #==================================================================================================
  # Adjust blue band according to data unit (TOA or surface reflectance)
  #==================================================================================================
  if data_unit == eoImg.sur_ref: 
    blu_img = blu_img.add(ee.Image(5.0))
  
  return blu_img.multiply(ee.Image(-1.0))
'''

               

######################################################################################################
# Description: This function attachs a smoothed score image to the given image
#
# Note:        The value range of "median_blue" is already in between 0 and 100
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def attach_Score(median_blue, midDate, ssr_code, data_unit, image):
  '''Attach a score image to a given image.
  
  Args:
      median_blue(ee.Image): The blue band of a median mosaic. Will be used as the blue reference for buildings.   
      midDate(ee.Date): The centre date of a time period for a mosaic generation.
      ssr_code(int): The sensor type code.
      data_unit(int): The integer representing data unit (1 and 2 => TOA and surface reflectance).
      image(ee.Image): A given ee.Image object to be generated a time score image.'''

  #==================================================================================================
  # Create a map that combines spectral and time scores
  #==================================================================================================
  #neg_blu_map = get_neg_blue_map(ssr_code, data_unit, image)
  score_map  = get_score_map(median_blue, midDate, ssr_code, data_unit, image)

  # Define a boxcar or low-pass kernel.
  boxcar = ee.Kernel.circle(radius = 2, units = 'pixels', normalize = True)

  # Smooth the image by convolving with the boxcar kernel.
  smoothed_score_map = score_map.convolve(boxcar)

  return image.addBands(smoothed_score_map.select([0], [eoImg.pix_score]))
             




######################################################################################################
# Description: This function attaches a score, acquisition date and some specified bands to each image
#              of a collection.
#
# Revision history:  2021-Jun-10  Lixin Sun  Initial creation
#                    2021-Aug-17  Lixin Sun  Fixed the bug after "if addGeometry == True:" statement.
#                    2020-Aug-10  Lixin Sun  Changed 'addGeometry' parameter to 'ExtraBandCode', so 
#                                            that various different bands can be attached to each
#                                            scored image.
######################################################################################################
def score_collection(collection, ssr_code, data_unit, midDate, ExtraBandCode):
  '''Attaches a score, acquisition date and some specified bands to each image of a collection.
  
  Args:
     collection(ee.ImageCollection): A given image collection;
     ssr_code(int): Sensor code integer;
     data_unit(int): Data unit integer;
     midDate(ee.Date): The centre date of a time period for a mosaic generation;
     ExtraBandCode(int): The integer code representing band type to be added additionally.'''
  #print('<score_collection> band names of 1st image = ', collection.first().bandNames().getInfo())
  #print('<score_collection> the given collection = ', collection.size().getInfo())
  #==================================================================================================
  # Create a reference blue band
  #==================================================================================================
  blue_name = eoImg.get_BandName(eoImg.BLU_band, ssr_code, data_unit)
  #print('<score_collection> blue band name = ', blue_name)

  def get_blue(img) :
    #valid_mask = eoImgMsk.ValidMask(img, ssr_code, data_unit).Not() 
    return img.select([blue_name])  #.updateMask(valid_mask) # Applying mask is important here
  
  blue_coll   = collection.map(lambda image: get_blue(image))
  blue_mosaic = blue_coll.median()

  median_blue = eoImg.apply_gain_offset(blue_mosaic, ssr_code, data_unit, 100, True)  
  
  #==================================================================================================
  # Attach a spectral-time score and acquisition date bands to each image in the image collection
  #==================================================================================================
  scored_collection = collection.map(lambda image: attach_Score(median_blue, midDate, ssr_code, data_unit, image)) \
                                .map(lambda image: eoImg.attach_Date(image))

  #==================================================================================================
  # Attach an additional bands as necessary to each image in the image collection
  #==================================================================================================  
  extra_code = int(ExtraBandCode)
  if extra_code == EXTRA_ANGLE:
    scored_collection = scored_collection.map(lambda image: eoImg.attach_AngleBands(image, ssr_code))
  elif extra_code == EXTRA_NDVI:
    scored_collection = scored_collection.map(lambda image: eoImg.attach_NDVIBand(image, ssr_code, data_unit))

  # Return scored image collection  
  return scored_collection




######################################################################################################
# Description: This function creates a mosaic image based on a given image collection. 
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def coll_mosaic(collection, ssr_code, data_unit, midDate, ExtraBandCode):
  '''Create a mosaic image based on a given image collection.
  
  Args:
     collection(ee.ImageCollection): A given image collection;
     ssr_code(int): Sensor code integer;
     data_unit(int): Data unit integer;
     midDate(ee.Date): The centre date of a time period for a mosaic generation;
     addGeometry(boolean): A flag indicating if geometry angle bands need to be attached to each image.
  '''
  #==================================================================================================
  # Create a scored image collection (attach a score image for each image in the given collection)
  #==================================================================================================
  scored_collection = score_collection(collection, ssr_code, data_unit, midDate, ExtraBandCode)

  #==================================================================================================
  # Create and return a mosaic based on associated score maps
  #==================================================================================================  
  mosaic = scored_collection.qualityMosaic(eoImg.pix_score) #.set('system:time_start', midDate.millis())
  
  return mosaic



  

######################################################################################################
# Description: This function merges the mosaics created from the images acquired with the same sensor.
#
# Note: This function assumes the two given mosaics were created from the images acquired by the 
#       same sensor
#     
# Revision history:  2020-Dec-07  Lixin Sun  Initial creation
#
######################################################################################################
def MergeMosaics(BaseMosaic, SecondMosaic, SensorCode, DataUnit, ThreshFactor):
  '''Merge the mosaics created from the images acquired with the same sensor.
  Args:
    BaseMosaic(ee.Image): The base/target mosaic image; 
    SecondMosaic(ee.Image): The secondary mosaic image;
    SensorCode(int):
    DataUnit(int): 
    ThreshFactor(float): A factor for adjusting threshold score.'''
  target = ee.Image(BaseMosaic).selfMask()
  second = ee.Image(SecondMosaic).selfMask()

  #==================================================================================================
  # Fill the masked/missing pixels in targeted year's mosaic with the pixels from another mosaic
  #==================================================================================================
  target = target.unmask(second)

  #==================================================================================================
  # If the quality scores of previous year are significantly higher than target year, then replace
  # target year pixels with that of previousr years
  #==================================================================================================
  SW2_name     = eoImg.get_BandName(6, SensorCode, DataUnit)
  NIR_name     = eoImg.get_BandName(4, SensorCode, DataUnit)

  target_SW2   = target.select(SW2_name)
  target_NIR   = target.select(NIR_name)
  refer_NIR    = second.select(NIR_name)

  target_score = target.select(eoImg.pix_score)
  refer_score  = second.select(eoImg.pix_score)
  thresh_score = target_score.divide(ee.Image(ThreshFactor))
  
  replace_cond = target_SW2.lt(2.5).And(refer_NIR.gt(target_NIR)).And(refer_score.subtract(thresh_score).gt(target_score))
  return target.where(replace_cond, second)




######################################################################################################
# Description: This function merges the mosaics created from the images acquired with different
#              Landsat sensors.
#
# Note:        When merging a Sentinel-2 mosaic with a Landsat mosaic, the Sentinel-2 mosaic must be
#              used as the base mosaic and the Landsat mosaic is used to fill the gaps in base mosaic.  
#
# Revision history:  2022-May-02  Lixin Sun  Initial creation
#                    2022-Oct-20  Lixin Sun  Modified so that this function is not only applicable for
#                                            merging two Landsat mosaics, but also for merging a
#                                            Sentinel-2 mosaic with a Landsat mosaic.  
######################################################################################################
def MergeMixMosaics(MosaicBase, Mosaic2nd, SensorBase, Sensor2nd, DataUnit):
  '''Merge the mosaics created from the images acquired with different Landsat sensors.

  Args:
    MosaicBase(ee.Image): The mosaic that will be used as a base/main one;
    Mosaic2nd(ee.Image): The mosaic that will be used to fill the gaps in the base mosaic;
    SensorBase(int): The sensor code integer of the base/main mosaic;
    Sensor2nd(int): The sensor code integer of the 2nd mosaic to be used to fill the gaps in base mosaic;
    DataUnit(int): The data unit integer.'''  
  #==================================================================================================
  # Determine max reflectance value (max_ref). If the base mosaic was created with Sentinel-2 data,
  # then max_ref must be 100, because the given both mosaics (MosaicBase and Mosaic2nd) are supposed
  # have been converted to range of [0, 100]. If the base mosaic was created from Landsat data, then
  # max_ref must be 1000, meaning all mosaic pixel are with their raw values.
  #==================================================================================================  
  max_ref = 100 if SensorBase > eoImg.MAX_LS_CODE else 1000
  
  print('\n\n<MergeMixMosaics> Sensor code of base mosaic = ', SensorBase)
  print('<MergeMixMosaics> Bands in 1st mosaic = ', MosaicBase.bandNames().getInfo())
  print('<MergeMixMosaics> Bands in 2nd mosaic = ', Mosaic2nd.bandNames().getInfo())
  #==================================================================================================
  # Attach a sensor code band to each mosaic image
  # Note: pixel masks of both mosaic must be applied to their corresponding sensor code images 
  #==================================================================================================  
  virtual_ssr = Sensor2nd if SensorBase > eoImg.MAX_LS_CODE else SensorBase
  pix_mask1 = eoIM.Img_ValueMask(MosaicBase, virtual_ssr, DataUnit, max_ref).Not()
  pix_mask2 = eoIM.Img_ValueMask(Mosaic2nd,  Sensor2nd,   DataUnit, max_ref).Not()

  ssr_code_img1 = pix_mask1.multiply(SensorBase).rename([eoImg.mosaic_ssr_code])
  ssr_code_img2 = pix_mask2.multiply(Sensor2nd ).rename([eoImg.mosaic_ssr_code])

  mosaic1 = MosaicBase.addBands(ssr_code_img1)
  mosaic2 = Mosaic2nd.addBands(ssr_code_img2)
  print('<MergeMixMosaics> Bands in 1st mosaic = ', mosaic1.bandNames().getInfo())
  print('<MergeMixMosaics> Bands in 2nd mosaic = ', mosaic2.bandNames().getInfo())
  #==================================================================================================
  # Fill the gaps in base mosaic with the valid pixels in the 2nd mosaic
  #==================================================================================================
  mosaic1 = mosaic1.unmask(mosaic2)

  diff_thresh = 1.2 if SensorBase > eoImg.MAX_LS_CODE else 0.7
  score1 = mosaic1.select(eoImg.pix_score).add(diff_thresh)
  score2 = mosaic2.select(eoImg.pix_score)  
  
  mosaic = mosaic1.where(score2.gt(score1), mosaic2) 
  return ee.Image(mosaic.selfMask())





###################################################################################################
# Description: This function creates a mosaic image for a defined region using the images acquired
#              by one sensor during a time period.
#
# Revision history:  2021-Jun-02  Lixin Sun  Initial creation
#                    2021-Oct-05  Lixin Sun  Added an output option 
###################################################################################################
def HomoPeriodMosaic(SensorCode, DataUnit, Region, TargetYear, NbYears, StartDate, StopDate, ExtraBandCode):
  '''Creates a mosaic image for a region using the images acquired during a period of time. 
     
  Args:
      SensorCode(int): A sensor type integer (e.g., 5, 8 and 101 for LS 5, 8 and S2, respectively);
      DataUnit(int): Data unit code integer. 1 and 2 represent TOA and surface reflectance, respectively;
      Region(ee.Geometry): The spatial polygon of a ROI;
      TargetYear(int): A targeted year (must be an integer);
      NbYears(int): The number of years
      StartDate(ee.Date or string): The start Date (e.g., '2020-06-01');
      StopDate(ee.Date or string): The stop date (e.g., '2020-06-30');
      ExtraBandCode(int): A integr code representing band type be aatached additionally. '''  
  # Cast some input parameters 
  nb_years = int(NbYears)
  start    = ee.Date(StartDate).update(TargetYear)
  stop     = ee.Date(StopDate).update(TargetYear)

  #==========================================================================================================
  # Get a mosaic image corresponding to a given time window in a targeted year
  #==========================================================================================================
  coll_target    = eoImgSet.getCollection(SensorCode, DataUnit, Region, start, stop)
  midDate_target = eoImgSet.period_centre(start, stop)
  mosaic_target  = coll_mosaic(coll_target, SensorCode, DataUnit, midDate_target, ExtraBandCode)

  if nb_years == 1:
    return mosaic_target

  elif nb_years == 2: 
    # Create a mosaic image for the year before the target
    PrevYear = TargetYear - 1
    start    = start.update(PrevYear)
    stop     = stop.update(PrevYear)

    coll_before    = eoImgSet.getCollection(SensorCode, DataUnit, Region, start, stop)
    midDate_before = eoImgSet.period_centre(start, stop)
    mosaic_before  = coll_mosaic(coll_before, SensorCode, DataUnit, midDate_before, ExtraBandCode)

    # Merge the two mosaic images into one and return it  
    return MergeMosaics(mosaic_target, mosaic_before, SensorCode, DataUnit, 3.0)

  else: 
    # Create mosaic image for the year after the target
    AfterYear = TargetYear + 1
    start     = start.update(AfterYear)
    stop      = stop.update(AfterYear)

    coll_after    = eoImgSet.getCollection(SensorCode, DataUnit, Region, start, stop)
    midDate_after = eoImgSet.period_centre(start, stop)
    mosaic_after  = coll_mosaic(coll_after, SensorCode, DataUnit, midDate_after, ExtraBandCode)

    mosaic_target = MergeMosaics(mosaic_target, mosaic_after, SensorCode, DataUnit, 3.0)

    # Create mosaic image for the year before the target
    PrevYear = TargetYear - 1
    start    = start.update(PrevYear)
    stop     = stop.update(PrevYear)

    coll_before    = eoImgSet.getCollection(SensorCode, DataUnit, Region, start, stop)
    midDate_before = eoImgSet.period_centre(start, stop)
    mosaic_before  = coll_mosaic(coll_before, SensorCode, DataUnit, midDate_before, ExtraBandCode)
    
    return MergeMosaics(mosaic_target, mosaic_before, SensorCode, DataUnit, 3.0)  





##########################################################################################################
# Description: This function creates an mosaic image for a region using the images acquired during one to 
#              three peak seasons (from June 15 to September 15).
#
# Revision history:  2021-Jul-07  Lixin Sun  Initial creation using JavaScript
#                    
##########################################################################################################
def HomoPeakMosaic(SensorCode, DataUnit, Region, TargetYear, NbYears, ExtraBandCode):
  '''Creates a mosaic image for a region using the images acquired during one, two or three
     peak-growing seasons (from June 15 to September 15). 
     
  Args:
      SensorCode(int): A sensor type code integer (5,7,8,9 or 101);
      DataUnit(int): A data unit code integer (1 and 2 represent TOA and surface reflectance, respectively);
      Region(ee.Geometry): A spatial region of a ROI;
      TargetYear(int): An integer representing a targeted year (e.g., 2020);
      NbYears(int): The number of peak seasons (1, 2 or 3);
      ExtraBandCode(int): A integer representing the band type to be attached to image.'''  
  # Cast some input parameters 
  n_years = int(NbYears)

  # Get a peak season mosaic for targeted year
  start, stop = eoImgSet.summer_range(TargetYear)
  
  return HomoPeriodMosaic(SensorCode, DataUnit, Region, TargetYear, n_years, start, stop, ExtraBandCode)




###################################################################################################
# Description: This function creates a mosaic image for a specified region using all the LANDSAT
#              images acquired during a period of time.
#
# Revision history:  2022-May-02  Lixin Sun  Initial creation
#
###################################################################################################
def LSMix_PeriodMosaic(DataUnit, Region, Year, StartDate, StopDate, ExtraBandCode):
  '''Creates a mosaic image for a region using the images acquired during a period of time. 
     
  Args:
      DataUnit(int): Data unit code integer. 1 and 2 represent TOA and surface reflectance, respectively;
      Region(ee.Geometry): The spatial polygon of a ROI;
      Year(int): A specified target year (must be a regular integer);
      Startdate(ee.Date or string): The start date string (e.g., '2020-06-01') or ee.Date object;
      StopDate(ee.Date or string): The end date string (e.g., '2020-06-30') or ee.Date object;
      ExtraBandCode(int): A integer code representing band type to be attached additionaly.
  '''
  #================================================================================================
  # Determine two Landsat sensor codes based on a given targeted year
  #================================================================================================
  year      = int(Year)

  ssr_code1 = 8 if year > 2013 else (5 if year > 2004 and year < 2013 else 7)
  ssr_code2 = 9 if year >= 2022 else (7 if year > 2004 and year < 2022 else 5)
  print('<LSMix_PeriodMosaic> sensor code1 and code2 = ', ssr_code1, ssr_code2)

  #================================================================================================
  # Determine a proper time period based on a given targeted year and an initial period 
  #================================================================================================
  data_unit = int(DataUnit)
  start     = ee.Date(StartDate).update(Year)
  stop      = ee.Date(StopDate).update(Year)
  midDate   = eoImgSet.period_centre(start, stop)

  #================================================================================================
  # Create two Landsat mosaics
  #================================================================================================
  img_coll1 = eoImgSet.getCollection(ssr_code1, data_unit, Region, start, stop)
  mosaic1   = coll_mosaic(img_coll1, ssr_code1, data_unit, midDate, ExtraBandCode)  

  img_coll2 = eoImgSet.getCollection(ssr_code2, data_unit, Region, start, stop)
  mosaic2   = coll_mosaic(img_coll2, ssr_code2, data_unit, midDate, ExtraBandCode)  

  #================================================================================================
  # Deal with the case when Landsat 7 needs to be merged with Landsat 8 data 
  #================================================================================================
  if ssr_code1 == eoImg.LS8_sensor and ssr_code2 == eoImg.LS7_sensor:
    temp_ls7_mosaic = mosaic2.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']) \
                             .rename(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'])

    ls7_mosaic = mosaic2.select(['SR_B1']).addBands(temp_ls7_mosaic)

    # Add rest other bands
    if ExtraBandCode == EXTRA_ANGLE:
      mosaic1 = mosaic1.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'cosVZA', 'cosSZA', 'cosRAA', eoImg.pix_score, eoImg.pix_date])
      rest_bands = ['cosVZA', 'cosSZA', 'cosRAA', eoImg.pix_score, eoImg.pix_date]
    elif ExtraBandCode == EXTRA_NDVI:
      mosaic1 = mosaic1.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', eoImg.pix_date, eoImg.PARAM_NDVI, eoImg.pix_score])
      rest_bands = [eoImg.pix_date, eoImg.PARAM_NDVI, eoImg.pix_score]
    else:
      mosaic1 = mosaic1.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', eoImg.pix_date, eoImg.pix_score])
      rest_bands = [eoImg.pix_date, eoImg.pix_score]

    ls7_mosaic = ls7_mosaic.addBands(mosaic2.select(rest_bands))

    test_ls7_mosaic = ls7_mosaic.focal_mean(1, 'circle', 'pixels', 10)
    mosaic2         = ls7_mosaic.unmask(test_ls7_mosaic)

  return MergeMixMosaics(mosaic1, mosaic2, ssr_code1, ssr_code2, data_unit)




###################################################################################################
# Description: This function creates an at-surface reflectance mosaic image for a specified region
#              using all available Sentinel-2 and LANDSAT data acquired during a time period.
#
# Note:        This function rescales the pixel values of the involved mosaics, because Sentinel-2
#              and Landsat have different scaling factors and must be converted to the same value
#              range before merging/gap filling.              
#
# Revision history:  2022-Oct-20  Lixin Sun  Initial creation
#
###################################################################################################
def S2LS_Mix_PeriodMosaic(Region, Year, StartDate, StopDate, ExtraBandCode):
  '''Creates a mosaic image for a region using the images acquired during a period of time. 
     
  Args:
      Region(ee.Geometry): The spatial polygon of a ROI;
      Year(int): A specified target year (must be a integer);
      Startdate(ee.Date or string): The start date string (e.g., '2020-06-01') or ee.Date object;
      StopDate(ee.Date or string): The end date string (e.g., '2020-06-30') or ee.Date object;
      ExtraBandCode(int): A integer code representing band type to be attached additionaly.
  '''
  #================================================================================================
  # Ensure the given year is after 2019, because Sentinel-2 surface reflectance data is available
  # only after 2019  
  #================================================================================================
  year = int(Year)
  if year < 2019:
    year = 2019

  #================================================================================================
  # Set up proper data unit and time window
  #================================================================================================
  data_unit = 2  #This function is only applicable to at-surface reflectance data
  start     = ee.Date(StartDate).update(Year)
  stop      = ee.Date(StopDate).update(Year)
  print("<S2LS_Mix_PeriodMosaic> start and stop dates of a time period = ", start.format().getInfo(), stop.format().getInfo())
  #================================================================================================
  # Create a mosaic with mixed available Landsat data
  #================================================================================================
  ls_mosaic = LSMix_PeriodMosaic(data_unit, Region, year, start, stop, ExtraBandCode)
  ls_mosaic = eoImg.apply_gain_offset(ls_mosaic, eoImg.LS8_sensor, data_unit, 100, False)

  #================================================================================================
  # Create a mosaic with available Sentinel-2 data
  #================================================================================================
  s2_mosaic = HomoPeriodMosaic(eoImg.ST2A_sensor, data_unit, Region, year, 1, start, stop, ExtraBandCode)
  s2_mosaic = eoImg.apply_gain_offset(s2_mosaic, eoImg.ST2A_sensor, data_unit, 100, False)

  #================================================================================================
  # Match a subset of Sentinel-2 bands to Landsat-8 bands and also extract required extra bands 
  #================================================================================================
  mosaic_base = s2_mosaic.select(['B1', 'B2', 'B3', 'B4', 'B8A', 'B11', 'B12']) \
                         .rename(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'])
  
  if ExtraBandCode == EXTRA_ANGLE:
    mosaic2nd = ls_mosaic.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'cosVZA', 'cosSZA', 'cosRAA', eoImg.pix_score, eoImg.pix_date])
    rest_bands = ['cosVZA', 'cosSZA', 'cosRAA', eoImg.pix_score, eoImg.pix_date]
  elif ExtraBandCode == EXTRA_NDVI:
    mosaic2nd = ls_mosaic.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', eoImg.pix_date, eoImg.PARAM_NDVI, eoImg.pix_score])
    rest_bands = [eoImg.pix_date, eoImg.PARAM_NDVI, eoImg.pix_score]
  else:
    mosaic2nd  = ls_mosaic.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', eoImg.pix_date, eoImg.pix_score])
    rest_bands = [eoImg.pix_date, eoImg.pix_score]

  mosaic_base = mosaic_base.addBands(s2_mosaic.select(rest_bands))
  print('<S2LS_Mix_PeriodMosaic> Bands in base mosaic = ', mosaic_base.bandNames().getInfo())
  print('<S2LS_Mix_PeriodMosaic> Bands in 2nd mosaic = ',  mosaic2nd.bandNames().getInfo())

  return MergeMixMosaics(mosaic_base, mosaic2nd, eoImg.ST2A_sensor, eoImg.LS8_sensor, data_unit)





######################################################################################################
# Description: This function creates a mosaic image for a region using the images acquired within one
#              peak season. In the case of Landsat data is used, a mixed mosaic will be created.
#
# Revision history:  2022-Aug-10  Lixin Sun  Initial creation
#
######################################################################################################
def MixPeakMosaic(SensorCode, DataUnit, Year, Region, ExtraBandCode):
  '''Create a mosaic image for a region using the images acquired within one peak-growing season.

  Args:
      SensorCode(int): A sensor type code (one of 5, 7, 8 or 101/102);
      DataUnit(int):  The product level of used images. 1 and 2 represent TOA and surface reflectance;
      Year(int): A targeted year integer;
      Region(ee.Geometry): The geospatial region of a specified ROI/mosaic;
      ExtraBandCode(int): A imteger representing the band type to be attached to each image.'''
  ssr_code  = int(SensorCode)
  data_unit = int(DataUnit)
  region    = ee.Geometry(Region)

  #return HomoPeakMosaic(ssr_code, data_unit, region, Year, 1, ExtraBandCode)
  #==================================================================================================
  # Create a scored image collection (attach a score image for each image in the given collection)
  #==================================================================================================
  if ssr_code < eoImg.MAX_LS_CODE:  #For Landsat imagery, gap filling with different sensors can be applied 
    start, stop = eoImgSet.summer_range(Year)
    return LSMix_PeriodMosaic(data_unit, region, Year, start, stop, ExtraBandCode)
  else:  # For Sentinel-2, no gap filling can be done 
    return HomoPeakMosaic(ssr_code, data_unit, region, Year, 1, ExtraBandCode)





#############################################################################################################
# Description: Creates a mosaic image specially for vegetation parameter extraction with LEAF tool.
#
# Note:        The major difference between a mosaic for LEAF tool and general-purpose mosaic is the 
#              attachment of three imaging geometrical angle bands. 
#  
# Revision history:  2021-May-19  Lixin Sun  Initial creation
#                    2022-Jan-14  Lixin Sun  Modified so that every value in "fun_Param_dict" dictionary
#                                            is a single value.  
#                    2022-May-25  Lixin Sun  Added different-sensor gap filling option for Landsat imagery.
#############################################################################################################
def LEAF_Mosaic(fun_param_dict, region):
  '''Creates a mosaic image specially for vegetation parameter extraction with LEAF tool.
     
     Args:
       fun_param_dict({}): a function parameter dictionary containing various single parameters;    
       region(ee.Geometry): the spatial region of a mosaic image.'''
  #==========================================================================================================
  # Determine time period based on the given year and month
  #==========================================================================================================
  year  = int(fun_param_dict['year'])
  month = int(fun_param_dict['month'])
  start, stop = eoImgSet.month_range(year, month)

  #==========================================================================================================
  # Create an image colection based on specified filtering parameters/criteria
  #==========================================================================================================
  ssr_code  = int(fun_param_dict['sensor'])
  data_unit = eoImg.sur_ref

  if ssr_code < eoImg.MAX_LS_CODE:  #For Landsat imagery, gap filling with different sensors can be applied 
    mosaic = LSMix_PeriodMosaic(data_unit, region, year, start, stop, EXTRA_ANGLE)
  else:  # For Sentinel-2, no gap filling can be done 
    img_coll = eoImgSet.getCollection(ssr_code, data_unit, region, start, stop)

    # Create a mosaic image including all the band images required by vegetation parameter extraction
    midDate = eoImgSet.period_centre(start, stop)
    mosaic  = coll_mosaic(img_coll, ssr_code, data_unit, midDate, EXTRA_ANGLE)

  #==========================================================================================================
  # Convert value range of spectral values to [0, 1].
  # Imaging angle bands do not need value range conversion, since their ranges are already right
  #==========================================================================================================
  return eoImg.apply_gain_offset(mosaic, ssr_code, data_unit, 1, False)






#############################################################################################################
# Description: This function creates a monthly mosaic image with gaps partially filled. The gaps are filled 
#              with the images acquired within the months before and after the targeted month.
#
# Note:        (1) This function is originally developed for LEAF production.
#              (2) The following coefficients can be uesed to harmonizate ETM+ data to OLI data 
#                  (https://developers.google.com/earth-engine/tutorials/community/landsat-etm-to-oli-harmonization)
# coefficients = {
#  itcps: ee.Image.constant([0.0003, 0.0088, 0.0061, 0.0412, 0.0254, 0.0172]).multiply(10000),
#  slopes: ee.Image.constant([0.8474, 0.8483, 0.9047, 0.8462, 0.8937, 0.9071])
# }
#
# Revision history:  2022-May-25  Lixin Sun  Initial creation
#
#############################################################################################################
def MonthlyMosaicGapFill(SensorCode, DataUnit, Year, Month, TileName, ExtraBandCode):
  '''Creates a monthly mosaic image for a region with gaps partially filled.

  Args:
      SensorCode(int): A sensor type code (one of 5, 7, 8 or 101/102);
      DataUnit(int): The product level of used images. 1 and 2 represent TOA and surface reflectance;
      Year(int or string): A targeted year of mosaicing;
      Month(int or string): A targeted month of mosaicing;
      TileName(string): The name string of a tile;
      ExtraBandCode(boolean): A flag indicating the type of extra bands to be attached.'''  
  #==========================================================================================================
  # Cast input parameter to right data types and obtain ROI
  #==========================================================================================================
  ssr_code  = int(SensorCode)
  data_unit = int(DataUnit)
  year      = int(Year)
  month     = int(Month) 
  tile_name = str(TileName) 
  region    = eoTileGD.PolygonDict.get(tile_name)

  #==========================================================================================================
  # Create a peak season mosaic image and then do unsupervised clustering
  #==========================================================================================================
  mosaic   = HomoPeakMosaic(ssr_code, data_unit, region, year, 1, ExtraBandCode)
  
  samples  = 4000
  clusters = 20
  Scale    = 30
  cluster_map = eoCU.mosaic_clustering(mosaic, ssr_code, data_unit, Scale, region, samples, clusters).rename(eoCU.cluster_name)
  
  #==========================================================================================================
  # Create two (target and next months) monthly mosaic images 
  #==========================================================================================================
  valid_bands = eoImg.get_out_BandNames(ssr_code, data_unit)
  # Create a mosaic image for targeted month  
  start, stop  = eoImgSet.month_range(year, month)  
  mosaic_targt = HomoPeriodMosaic(ssr_code, data_unit, region, year, 1, start, stop, ExtraBandCode).select(valid_bands)
  mosaic_targt = eoImg.apply_gain_offset(mosaic_targt, ssr_code, data_unit, 100, True)
  
  # Create a mosaic image for the month after the target month
  start, stop  = eoImgSet.month_range(year, month+1)  
  mosaic_after = HomoPeriodMosaic(ssr_code, data_unit, region, year, 1, start, stop, ExtraBandCode).select(valid_bands)
  mosaic_after = eoImg.apply_gain_offset(mosaic_after, ssr_code, data_unit, 100, True)    
  
  estimate_after = eoGF.refer_to_estimate(mosaic_after, mosaic_targt, region, cluster_map, clusters, Scale)
                                         
  #==========================================================================================================
  # Create an estimated mosaic image based on ONE or TWO reference mosaic images
  #==========================================================================================================
  raw_band_names = eoImg.get_raw_OptiBandNames(ssr_code, data_unit)

  if month > 5:  # The case for months after May
    #--------------------------------------------------------------------------------------------------------
    # Create a mosaic image for the month before the targeted month 
    #--------------------------------------------------------------------------------------------------------
    start, stop   = eoImgSet.month_range(year, month-1)
    mosaic_before = HomoPeriodMosaic(ssr_code, data_unit, region, year, 1, start, stop, ExtraBandCode).select(valid_bands)
    mosaic_before = eoImg.apply_gain_offset(mosaic_before, ssr_code, data_unit, 100, True)
   
    #--------------------------------------------------------------------------------------------------------
    # Create two estimated mosaic images for the targeted month from two reference monthly mosaic images
    #--------------------------------------------------------------------------------------------------------
    estimate_before = eoGF.refer_to_estimate(mosaic_before, mosaic_targt, region, cluster_map, clusters, Scale)
    #print('<MonthlyMosaicGapFill> band names in estimate_before = ', estimate_before.bandNames().getInfo())
    
    estimate_before = estimate_before.rename(raw_band_names)
    before_score    = mosaic_score_map(estimate_before, ssr_code, data_unit).rename([eoImg.pix_score])
    estimate_before = estimate_before.addBands(before_score)

    estimate_after  = estimate_after.rename(raw_band_names)
    after_score     = mosaic_score_map(estimate_after, ssr_code, data_unit).rename([eoImg.pix_score])
    estimate_after  = estimate_after.addBands(after_score)
    
    estimate = MergeMosaics(estimate_after, estimate_before, SensorCode, DataUnit, 1.5)
  else:  # The case for months before May
    estimate_after  = estimate_after.rename(raw_band_names)
    after_score = mosaic_score_map(estimate_after, ssr_code, data_unit).rename([eoImg.pix_score])
    estimate    = estimate_after.addBands(after_score)
    #print('estimate mosaic band names = ', estimate.bandNames().getInfo())    
  
  print('\n\n<MonthlyMosaicGapFill> bands in estimated image = ', estimate.bandNames().getInfo())
  #==========================================================================================================
  # Merge estimated mosaic image into the target image 
  #==========================================================================================================
  targt_score  = mosaic_score_map(mosaic_targt, ssr_code, data_unit).rename([eoImg.pix_score])
  mosaic_targt = mosaic_targt.addBands(targt_score)
  print('<MonthlyMosaicGapFill> bands in mosaic target = ', mosaic_targt.bandNames().getInfo())

  #return mosaic_targt.unmask(estimate)
  return MergeMosaics(mosaic_targt, estimate, SensorCode, DataUnit, 2.0)




#############################################################################################################
# Description: This function performs temporal gap filling using all available multispectral images, 
#              such as Landsat and Sentinel-2, acquired during a time period.
#              
#############################################################################################################
def MixMosaicGapFill(Region, Year, StartDate, StopDate, ExtraBandCode):
  '''Performs temporal gap filling using all available multispectral images, such as Landsat and Sentinel-2, 
     acquired during a time period.

    Args:
      Region(ee.Geometry): The spatial polygon of a ROI;
      Year(int): A targeted year of mosaicing;
      Startdate(ee.Date or string): The start date string (e.g., '2020-06-01') or ee.Date object;
      StopDate(ee.Date or string): The end date string (e.g., '2020-06-30') or ee.Date object;
      TileName(string): The name string of a tile;
      ExtraBandCode(boolean): A flag indicating the type of extra bands to be attached.'''  
  #==========================================================================================================
  # Cast input parameter to right data types and obtain ROI
  #==========================================================================================================
  ssr_code  = eoImg.LS8_sensor
  data_unit = 2
  year      = int(Year)
  region    = ee.Geometry(Region)

  #==========================================================================================================
  # Create a park season mosaic image for unsupervised clustering
  #==========================================================================================================
  peak_start, peak_stop = eoImgSet.summer_range(year)
  peak_mosaic = S2LS_Mix_PeriodMosaic(region, year, peak_start, peak_stop, ExtraBandCode)
  
  samples  = 4000
  clusters = 20
  Scale    = 30
  cluster_map = eoCU.mosaic_clustering(peak_mosaic, eoImg.LS8_sensor, data_unit, Scale, region, samples, clusters).rename(eoCU.cluster_name)
  
  #==========================================================================================================
  # Create two (target and next months) period mixed mosaic images 
  #==========================================================================================================
  valid_bands = eoImg.get_out_BandNames(ssr_code, data_unit)
  # Create a mosaic image for targeted month  
  targt_start = ee.Date(StartDate).update(Year)
  targt_stop  = ee.Date(StopDate).update(Year) 
  time_diff   = targt_stop.difference(targt_start, 'day').add(1)
  mosaic_targt = S2LS_Mix_PeriodMosaic(region, year, targt_start, targt_stop, ExtraBandCode).select(valid_bands)
  
  # Create a mosaic image for the month after the target month
  after_start = targt_start.advance(time_diff, 'day')  
  after_stop  = targt_stop.advance (time_diff, 'day')
  mosaic_after = S2LS_Mix_PeriodMosaic(region, year, after_start, after_stop, ExtraBandCode).select(valid_bands)
  
  estimate_after = eoGF.refer_to_estimate(mosaic_after, mosaic_targt, region, cluster_map, clusters, Scale)

  return estimate_after                                         
  #==========================================================================================================
  # Create an estimated mosaic image based on ONE or TWO reference mosaic images
  #==========================================================================================================
  raw_band_names = eoImg.get_raw_OptiBandNames(ssr_code, data_unit)

  if month > 5:  # The case for months after May
    #--------------------------------------------------------------------------------------------------------
    # Create a mosaic image for the month before the targeted month 
    #--------------------------------------------------------------------------------------------------------
    start, stop   = eoImgSet.month_range(year, month-1)
    mosaic_before = HomoPeriodMosaic(ssr_code, data_unit, region, year, 1, start, stop, ExtraBandCode).select(valid_bands)
    mosaic_before = eoImg.apply_gain_offset(mosaic_before, ssr_code, data_unit, 100, True)
   
    #--------------------------------------------------------------------------------------------------------
    # Create two estimated mosaic images for the targeted month from two reference monthly mosaic images
    #--------------------------------------------------------------------------------------------------------
    estimate_before = eoGF.refer_to_estimate(mosaic_before, mosaic_targt, region, cluster_map, clusters, Scale)
    #print('<MonthlyMosaicGapFill> band names in estimate_before = ', estimate_before.bandNames().getInfo())
    
    estimate_before = estimate_before.rename(raw_band_names)
    before_score    = mosaic_score_map(estimate_before, ssr_code, data_unit).rename([eoImg.pix_score])
    estimate_before = estimate_before.addBands(before_score)

    estimate_after  = estimate_after.rename(raw_band_names)
    after_score     = mosaic_score_map(estimate_after, ssr_code, data_unit).rename([eoImg.pix_score])
    estimate_after  = estimate_after.addBands(after_score)
    
    estimate = MergeMosaics(estimate_after, estimate_before, SensorCode, DataUnit, 1.5)
  else:  # The case for months before May
    estimate_after  = estimate_after.rename(raw_band_names)
    after_score = mosaic_score_map(estimate_after, ssr_code, data_unit).rename([eoImg.pix_score])
    estimate    = estimate_after.addBands(after_score)
    #print('estimate mosaic band names = ', estimate.bandNames().getInfo())    
  
  print('\n\n<MonthlyMosaicGapFill> bands in estimated image = ', estimate.bandNames().getInfo())
  #==========================================================================================================
  # Merge estimated mosaic image into the target image 
  #==========================================================================================================
  targt_score  = mosaic_score_map(mosaic_targt, ssr_code, data_unit).rename([eoImg.pix_score])
  mosaic_targt = mosaic_targt.addBands(targt_score)
  print('<MonthlyMosaicGapFill> bands in mosaic target = ', mosaic_targt.bandNames().getInfo())

  #return mosaic_targt.unmask(estimate)
  return MergeMosaics(mosaic_targt, estimate, SensorCode, DataUnit, 2.0)






#############################################################################################################
# Description: This function exports a given mosaic image to a specified location (either Google Drive or
#              Google Cloud Storage). The filenames of the exported images will be automatically generated 
#              based on tile name, image acquisition time and spatial resolution.
#
# Revision history:  2022-Mar-30  Lixin Sun  Initial creation 
#
#############################################################################################################
def export_mosaic(fun_Param_dict, mosaic, out_band_list, polygon, task_list):
  '''Exports one set of LEAF products to either Google Drive or Google Cloud Storage

     Args:
       fun_Param_dict(dictionary): a dictionary storing other required running parameters;
       mosaic(ee.Image): the mosaic image to be exported;
       out_band_list([]): The name list of the bands to be exported;
       polygon(ee.Geometry): the spatial region of interest;
       task_list([]): a list storing the links to exporting tasks. '''
  #==========================================================================================================
  # Obtain some parameters from the given parameter dictionary
  #==========================================================================================================
  print('\n<export_mosaic> fun_Param_dict = ', fun_Param_dict)
  year_str     = str(fun_Param_dict['year'])   
  nb_years     = int(fun_Param_dict['nbYears'])
  tile_str     = str(fun_Param_dict['tile_name'])
  Scale        = str(fun_Param_dict['resolution'])
  given_folder = str(fun_Param_dict['folder'])
  out_location = str(fun_Param_dict['location']).lower()

  #=================================================================================================== 
  # Create an expanded boundary polygon
  #===================================================================================================
  exp_polygon = eoTileGD.expandPolygon(polygon, 0.02) 

  #==========================================================================================================
  # Create an exporting folder name or use a given one
  #==========================================================================================================
  form_folder  = tile_str + '_' + year_str
  exportFolder = form_folder if len(given_folder) < 2 else given_folder  

  #==========================================================================================================
  # Create prefix filenames for peak or monthly mosaic band images 
  #==========================================================================================================
  filePrefix = form_folder
  if nb_years < 0:  # monthly mosaic
    month      = int(fun_Param_dict['month'])
    month_name = eoImg.get_MonthName(month)
    filePrefix = filePrefix + '_' + month_name    

  #==========================================================================================================
  # Export LEAF products to a Google Drive directory 
  #========================================================================================================== 
  myCRS      = 'EPSG:3979'
  max_pixels = 1e11
  export_dict = {'folder': exportFolder, 
                 'scale': int(Scale),
                 'crs': myCRS,
                 'maxPixels': max_pixels,
                 'region': exp_polygon}

  if out_location.find('drive') > -1:  # Export to Google Drive
    print('<export_mosaic> Exporting to Google Drive......')  
    for item in out_band_list:
      filename  = filePrefix + '_' + item + '_' + str(Scale) + 'm'

      export_dict['image'] = mosaic.select(item).multiply(ee.Image(100)).toInt16()
      export_dict['description'] = filename
      export_dict['fileNamePrefix'] = filename

      task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())
    
  elif out_location.find('storage') > -1:  # Exporting to Google Cloud Storage
    print('<export_mosaic> Exporting to Google Cloud Storage......')  
    export_dict['bucket'] = str(fun_Param_dict['bucket'])    
    for item in out_band_list:
      filename  = filePrefix + '_' + item + '_' + str(Scale) + 'm'
      
      export_dict['image'] = mosaic.select(item).multiply(ee.Image(100)).toInt16()
      export_dict['description'] = filename
      export_dict['fileNamePrefix'] = filename

      task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())

  elif out_location.find('asset') > -1:
    print('<export_mosaic> Exporting to Google Earth Assets......')      
    for item in out_band_list:
      filename  = filePrefix + '_' + item + '_' + str(Scale) + 'm'
      
      export_dict['image'] = mosaic.select(item).multiply(ee.Image(100)).toInt16()
      export_dict['description'] = filename
      export_dict['assetId'] = exportFolder + '/' + filename

      task_list.append(ee.batch.Export.image.toAsset(**export_dict).start())






#############################################################################################################
# Description: The start/main function for operationally producing tile mosaic maps using Landsat or 
#              Sentinel2 data
#
# Revision history:  2021-Oct-28  Lixin Sun  Initial creation 
#                    2021-Nov-19  Lixin Sun  Modified so that customized spatial regions can also be handled
#                                            in the same way as regular tiles.
#############################################################################################################
def Mosaic_production(exe_Param_dict, ExtraBandCode):
  '''Produces various mosaic products for one or more tiles using Landsat or Sentinel2 images
     Args:
       Param_dict(Dictionary): A dictionary storing required parameters.
       ExtraBandCode(int): A integer(EXTRA_NONE, EXTRA_ANGLE, EXTRA_NDVI) representing extra bands to be attached to each image.'''
  #==========================================================================================================
  # Create an initial "fun_Param_dict" dictionary, which will contain one combination of the elements of the
  # 'exe_Param_dict' dictionary and iteratively be paased directly to 'LEAF_Mosaic', 'one_LEAF_Product' and
  # 'export_ancillaries' functions, as well as subsequently their subroutines.
  #==========================================================================================================
  fun_Param_dict = {'sensor':     exe_Param_dict['sensor'],
                    'year':       exe_Param_dict['year'],
                    'nbYears':    exe_Param_dict['nbYears'],
                    'resolution': exe_Param_dict['resolution'],
                    'location':   exe_Param_dict['location'],
                    'bucket':     exe_Param_dict['bucket'],
                    'folder':     exe_Param_dict['folder']}

  #==========================================================================================================
  # Start to generate required mosaic images and then export them to specific location
  #==========================================================================================================  
  ssr_code  = int(exe_Param_dict['sensor'])
  unit_code = int(exe_Param_dict['unit'])
  year      = int(exe_Param_dict['year'])
  nYears    = int(exe_Param_dict['nbYears'])  
  out_bands = eoImg.get_out_BandNames(ssr_code, unit_code)

  task_list = []  
  # Loop through each tile
  for tile_name in exe_Param_dict['tile_names']:
    fun_Param_dict['tile_name'] = tile_name

    # Create a mosaic region ee.Geometry object 
    if eoTileGD.is_valid_tile_name(tile_name) == True:
      region = eoTileGD.PolygonDict.get(tile_name)      
    else:
      region = eoTileGD.custom_RegionDict.get(tile_name)

    if nYears > 0:  # Create a peak-season mosaic for a specific region/tile
      mosaic = HomoPeakMosaic(ssr_code, unit_code, region, year, nYears, ExtraBandCode)
      mosaic = eoImg.apply_gain_offset(mosaic, ssr_code, unit_code, 100, False)
      # Export spectral mosaic images  
      export_mosaic(fun_Param_dict, mosaic, out_bands, region, task_list)

    else:  # Create a monthly mosaic for a specific region/tile
      for month in exe_Param_dict['months']:
        fun_Param_dict['month'] = month
        start_date, stop_date = eoImgSet.month_range(year, month)
        mosaic = HomoPeakMosaic(ssr_code, unit_code, region, start_date, stop_date, ExtraBandCode)
        mosaic = eoImg.apply_gain_offset(mosaic, ssr_code, unit_code, 100, False)
        # Export spectral mosaic images
        export_mosaic(fun_Param_dict, mosaic, out_bands, region, task_list)

  return task_list