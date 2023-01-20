######################################################################################################
# Description: The code in this file was initially created with JavaScript and then was converted to
#              to Python in April 2021. Modifications were also made after the code conversion.
#
######################################################################################################
import ee 

import math

import Image as Img
import ImgMask as IM
import ImgSet as IS
import eoTileGrids as eoTG




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

  factor  = ee.Image(50) if ssr_code > Img.MAX_LS_CODE else ee.Image(100)
  one_img = image.select([0]).multiply(0).add(1)

  return one_img.divide((ee.Image(date_diff).divide(ee.Image(factor))).exp())




######################################################################################################
# Description: This function creates a IR-blue ratio image.
#
# Note:        (1) This function assumes the value range of the given image is between 0 and 100;
#              (2) Ratio, rather than subtraction, is a proper way to measure the reflectance 
#                  difference between infrared and blue bands;
#              (3) When input is surface reflectance data, an offset must be applied to the values of 
#                  blue band. Otherwise, very dark shadow pixels could be selected superior to 
#                  clear-sky pixels.    
#
# Revision history:  2022-Mar-15  Lixin Sun  Initial creation
#
######################################################################################################
def IR_Blue_ratio(blu, ir, data_unit):
  #==================================================================================================
  # Calculate main spectral score
  # data_unit = 1: a*data_unit + b = 0 (blu_offset)
  # data_unit = 2: a*data_unit + b = 5 (blu_offset)
  #==================================================================================================
  a = ee.Number(5)
  b = ee.Number(-5)
  blu_offset = a.multiply(data_unit).add(b)

  return ir.divide(blu.add(blu_offset))





######################################################################################################
# Description: This function creates a vegetated pixel score image.
#
# Note:        (1) This function assumes the value range of the given image is between 0 and 100
#              (2) Generally, veg_score is consisted of two components: base score and blue penalty.
#
# Revision history:  2022-Mar-15  Lixin Sun  Initial creation
#
######################################################################################################
def get_veg_score(base_score, blu, grn, red, nir, sw2, data_unit):  
  #==================================================================================================
  # Calculate greeness score and incorporate it into spectral score
  # Note: (1) greenness is useful for excluding the pixels with big NDVI, but is not green
  #       (2) Greenness must be limited within a range, since some dark shadow pixels could have 
  #           high greenness value due to their blue or red reflectance is suppressed very low. 
  #
  # green_score = ((green/blue)+(green/red))/2.0
  #==================================================================================================
  grn_score = grn.divide(blu).add(grn.divide(red)).divide(2)
  grn_score = grn_score.where(grn_score.lt(1.1).Or(grn_score.gt(3)), ee.Image(0))
  blu_diff  = grn.subtract(blu)
  red_diff  = grn.subtract(red)

  veg_score = base_score.where(blu_diff.gt(0.2).And(red_diff.gt(0.2)), base_score.add(grn_score))
  veg_score = veg_score.where(blu_diff.lt(-1).Or(red_diff.lt(-1)),  veg_score.multiply(-1))

  #==================================================================================================
  # Apply dark penalty
  # This criteria can help to exclude SHADOW pixels
  #==================================================================================================
  nir_refer        = ee.Image(20)
  nir_dark_penalty = nir.subtract(nir_refer)
  
  veg_score        = veg_score.where(nir.lt(nir_refer), veg_score.add(nir_dark_penalty))

  #==================================================================================================
  # Calculate blue band penalty and incorporate it into spectral score
  # This penalty is useful for excluding hazy/cloudy pixels
  #
  # data_unit = 1: a*data_unit + b = 6.2 (model_offset)
  # data_unit = 2: a*data_unit + b = 1.2 (model_offset)
  #==================================================================================================
  a = ee.Number(-5)
  b = ee.Number(11.2)
  HOT_offset = a.multiply(data_unit).add(b)
  HOT_gain   = 0.17

  model_blu    = sw2.multiply(HOT_gain).add(HOT_offset)   # estimate blue reference value using HOT transfer
  blue_penalty = blu.subtract(model_blu).abs()
  
  return veg_score.where(blu.gt(model_blu), veg_score.subtract(blue_penalty))







######################################################################################################
# Description: This function creates a water pixel score image
#
# Note: (1) One criteria that can discriminate water pixels from shadow pixels is the relation between 
#           blue and SWIR1 bands. For water pixels, blue values are much bigger than SWIR1 values. 
#           This is the reason why we have the third criteria in "invalid_cond".
#
# Revision history:  2022-Mar-15  Lixin Sun  Initial creation
#                    
######################################################################################################
def get_water_score(blu, grn, nir, sw1, sw2):
  #mNDWI       = mean_vis.subtract(mean_ir).divide(mean_vis.add(mean_ir))
  #water_score = mNDWI.multiply(5).divide(mean_short) 
  mean_vis = blu.add(grn).divide(2)
  mean_ir  = nir.add(sw1).add(sw2).divide(3)

  score_ratio = mean_vis.divide(mean_ir.add(1)) 
  water_score = score_ratio.add(ee.Image.constant(15).divide(mean_vis))

  valid_ratio  = mean_vis.divide(mean_ir)
  invalid_cond = mean_ir.gt(5).Or(mean_vis.gt(15)).Or(valid_ratio.lt(2))
  water_score  = water_score.where(invalid_cond, ee.Image(-100))
  
  return water_score

  





######################################################################################################
# Description: This function creates a non-vegetated pixel score image
#
# Note:        (1) This function assumes the value range of the given image is between 0 and 100
#              (2) The best region for testing the effectivity of non-vege score is northern Canada.
#              (3) Generally, nonveg_score is consisted of two components: base score and two penalties.
#   
# Revision history:  2022-Mar-15  Lixin Sun  Initial creation
#                    
######################################################################################################
def get_nonveg_score(base_score, blu, nir, sw1, median_blu):  
  #==================================================================================================
  # Calculate main spectral score
  #==================================================================================================
  '''
  min_vis = blu.min(grn).min(red)
  max_vis = blu.max(grn).max(red)
  
  min_vis_sw1 = sw1.subtract(min_vis).divide(sw1.add(min_vis))
  max_vis_sw1 = sw1.subtract(max_vis).divide(sw1.add(max_vis))
  max_score   = ee.Image(1.1).subtract(max_vis_sw1.abs()).multiply(-1.0)
  
  score = min_vis_sw1.where(min_vis.lt(2), max_score)
  '''
  #==================================================================================================
  # This criteria can help to exclude some strange pixels
  #==================================================================================================
  sw1_nir_diff = sw1.subtract(nir)  
  #score = base_score.add(sw1_nir_diff)
  score = base_score.where(sw1_nir_diff.lt(0), base_score.add(sw1_nir_diff))   # sw1 is bigger than nir for non-vegetated pixels

  #==================================================================================================
  # Apply blue band penalty to exclude hazy/cloudy pixels
  #==================================================================================================
  blue_model   = sw1.multiply(0.174).subtract(0.082)
  blue_model   = blue_model.where(sw1.gt(35), median_blu)
  blue_penalty = blu.subtract(blue_model).abs().divide(2)
  
  #condition = blu.gt(ee.Image(15.0)).And(median_blu.lt(ee.Image(30.0)))
  score = score.where(blu.gt(blue_model), score.subtract(blue_penalty))
  
  #==================================================================================================
  # Apply dark penalty to exclude shadow pixels
  #==================================================================================================
  min_sw1      = ee.Image(20)
  dark_penalty = sw1.subtract(min_sw1).abs().divide(5)
  
  return score.where(sw1.lt(min_sw1), score.subtract(dark_penalty)) 



'''
def get_nonveg_score(base_score, blu, nir, sw1):  
  #==================================================================================================
  # Apply blue band penalty to exclude Hazy pixels 
  #==================================================================================================  
  model_blu = sw1.pow(2).multiply(0.0148).subtract(sw1.multiply(0.5007)).add(7.1127)
  penalty   = blu.subtract(model_blu).abs().divide(3)

  #score = base_score.where(blu.lt(30).And(blu.gt(model_blu)), base_score.subtract(penalty))   # for excluding hazy pixels
  score = base_score.where(blu.gt(model_blu), base_score.subtract(penalty))   # for excluding hazy pixels

  #score = score.where(blu.gt(30), blu.subtract(30).multiply(-1))   # for excluding hazy pixels

  #==================================================================================================
  # This criteria can help to exclude some strange pixels
  #==================================================================================================
  sw1_nir_diff = sw1.subtract(nir)  
  score = score.where(sw1_nir_diff.lt(0), score.add(sw1_nir_diff))   # sw1 is bigger than nir for non-vegetated pixels
  #score = score.where(blu.lt(model_blu.add(4)), score.add(sw1_nir_diff))   # sw1 is bigger than nir for non-vegetated pixels

  #==================================================================================================
  # Apply dark penalty to exclude SHADOW pixels
  #==================================================================================================
  sw1_bottm        = ee.Image(20)
  sw1_dark_penalty = sw1.subtract(sw1_bottm).abs()
  
  return score.where(sw1.lt(sw1_bottm), score.subtract(sw1_dark_penalty))  # for excluding shadow pixels
'''










######################################################################################################
# Description: This function creates a combined (spectral and time) score map for a given image
#              (either TOA or surface reflectance).
#
# Note:        (1) This function assumes the value range of the given image is between 0 and 100
#              (2) The value range of "median_blue" is already in between 0 and 100
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def get_score_map(median_blu, inMidDate, SsrData, image):
  '''Return a pixel score image corresponding to a given image
  
  Args:      
      median_blue(ee.Image): The blue band of a median mosaic. Could be used as the blue reference for non-veg pixels; 
      inMidDate(ee.Date): The centre date of a time period for a mosaic generation.
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
      image(ee.Image): A given ee.Image object to be generated a time score image.'''
  #==================================================================================================
  # Rescale the pixel values in the given image
  #==================================================================================================
  max_ref = 100
  scaled_img = Img.apply_gain_offset(image, SsrData, max_ref, False)  

  #==================================================================================================
  # Create separate references for each of the SIX bands
  #==================================================================================================
  blu = scaled_img.select(SsrData['BLU'])
  grn = scaled_img.select(SsrData['GRN'])
  red = scaled_img.select(SsrData['RED'])
  nir = scaled_img.select(SsrData['NIR'])
  sw1 = scaled_img.select(SsrData['SW1'])
  sw2 = scaled_img.select(SsrData['SW2'])
  
  #==================================================================================================
  # Calculate base score for both vagetated and non-vegetated targets
  #==================================================================================================  
  data_unit  = SsrData['DATA_UNIT']
  max_ir     = nir.max(sw1)
  base_score = IR_Blue_ratio(blu, max_ir, data_unit)

  #==================================================================================================
  # Calculate vagetated and non-vegetated scores
  #==================================================================================================  
  score_map = get_veg_score(base_score, blu, grn, red, nir, sw2, data_unit) 

  NDVI_img  = nir.subtract(red).divide(nir.add(red))
  score_map = score_map.add(NDVI_img)

  score_map = score_map.where(NDVI_img.lt(0.3), get_nonveg_score(base_score, blu, nir, sw1, median_blu))    

  #==================================================================================================
  # Calculate water score as necessary
  #==================================================================================================
  water_score = get_water_score(blu, grn, nir, sw1, sw2)

  score_map = score_map.max(water_score)
  #score_map = score_map.where(grn.subtract(nir).gt(0.5), get_water_score(blu, grn, nir, sw1, sw2))

  #==================================================================================================
  # Apply time scores to vegetation targets 
  #==================================================================================================
  ssr_code   = SsrData['SSR_CODE']
  time_score = get_time_score(image, inMidDate, ssr_code)
  score_map  = score_map.multiply(time_score)
  
  return score_map  #.where(water_mask, water_score)
  




######################################################################################################
# Description: This function creates a spectral score map for a given mosaic image
#
# Note:        This function assumes the value range of the mosaic image is between 0 and 100
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def mosaic_score_map(mosaic, SsrData):
  '''Return a pixel score image corresponding to a given image
  
  Args:      
      mosaic(ee.Image): A given mosaic ee.Image object;
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit.'''

  #==================================================================================================
  # Create separate references for each of the SIX critical bands
  #==================================================================================================
  blu = mosaic.select(SsrData['BLU'])
  grn = mosaic.select(SsrData['GRN'])
  red = mosaic.select(SsrData['RED'])
  nir = mosaic.select(SsrData['NIR'])
  sw1 = mosaic.select(SsrData['SW1'])
  sw2 = mosaic.select(SsrData['SW2'])
  
  #==================================================================================================
  # Calculate base score for both vagetated and non-vegetated targets
  #==================================================================================================  
  data_unit  = SsrData['DATA_UNIT']
  max_ir     = nir.max(sw1)
  base_score = IR_Blue_ratio(blu, max_ir, data_unit)

  #==================================================================================================
  # Calculate scores for vagetated targets only and set scores for pixels with NDVI < 0.3 to zero
  #==================================================================================================  
  veg_score   = get_veg_score(base_score, blu, grn, red, nir, sw2, data_unit) 

  zero_score  = sw2.multiply(ee.Image(0.0)) #.add(cld_score.divide(ee.Image(200)))
  NDVI_img  = nir.subtract(red).divide(nir.add(red))

  return veg_score.where(NDVI_img.lt(ee.Image(0.3)), zero_score)





######################################################################################################
# Description: This function attachs a smoothed score image to the given image
#
# Note:        The value range of "median_blue" is already in between 0 and 100
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def attach_Score(median_blu, midDate, SsrData, Image):
  '''Attach a score image to a given image.
  
  Args:
      median_blue(ee.Image): The blue band of a median mosaic. Will be used as the blue reference for buildings.   
      midDate(ee.Date): The centre date of a time period for a mosaic generation.
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
      Image(ee.Image): A given ee.Image object to be generated a time score image.'''

  #==================================================================================================
  # Create a map that combines spectral and time scores
  #==================================================================================================
  #neg_blu_map = get_neg_blue_map(ssr_code, data_unit, image)
  score_map = get_score_map(median_blu, midDate, SsrData, Image)

  # Define a boxcar or low-pass kernel.
  boxcar = ee.Kernel.circle(radius = 2, units = 'pixels', normalize = True)

  # Smooth the image by convolving with the boxcar kernel.
  smoothed_score_map = score_map.convolve(boxcar)

  return Image.addBands(smoothed_score_map.select([0], [Img.pix_score]))
             




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
def score_collection(collection, SsrData, midDate, ExtraBandCode):
  '''Attaches a score, acquisition date and some specified bands to each image of a collection.
  
  Args:
     collection(ee.ImageCollection): A given image collection;
     SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
     midDate(ee.Date): The centre date of a time period for a mosaic generation;
     ExtraBandCode(int): The integer code representing band type to be added additionally.'''
  #print('<score_collection> band names of 1st image = ', collection.first().bandNames().getInfo())
  #print('<score_collection> the given collection = ', collection.size().getInfo())
  #==================================================================================================
  # Create a reference blue band
  #==================================================================================================
  blue_name = SsrData['BLU']
  #print('<score_collection> blue band name = ', blue_name)

  def get_blue(img) :
    #valid_mask = eoImgMsk.ValidMask(img, ssr_code, data_unit).Not() 
    return img.select([blue_name])  #.updateMask(valid_mask) # Applying mask is important here
  
  blue_coll   = collection.map(lambda image: get_blue(image))
  blue_mosaic = blue_coll.median()

  median_blue = Img.apply_gain_offset(blue_mosaic, SsrData, 100, True)  
  
  #==================================================================================================
  # Attach a spectral-time score and acquisition date bands to each image in the image collection
  #==================================================================================================
  scored_collection = collection.map(lambda image: attach_Score(median_blue, midDate, SsrData, image)) \
                                .map(lambda image: Img.attach_Date(image))
 
  #==================================================================================================
  # Attach an additional bands as necessary to each image in the image collection
  #==================================================================================================  
  extra_code = int(ExtraBandCode)
  if extra_code == EXTRA_ANGLE:
    scored_collection = scored_collection.map(lambda image: Img.attach_S2AngleBands(image, SsrData))
  elif extra_code == EXTRA_NDVI:
    scored_collection = scored_collection.map(lambda image: Img.attach_NDVIBand(image, SsrData))

  # Return scored image collection  
  return scored_collection




######################################################################################################
# Description: This function creates a mosaic image based on a given image collection. 
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def coll_mosaic(collection, SsrData, midDate, ExtraBandCode):
  '''Create a mosaic image based on a given image collection.
  
  Args:
     collection(ee.ImageCollection): A given image collection;
     SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
     midDate(ee.Date): The centre date of a time period for a mosaic generation;
     addGeometry(boolean): A flag indicating if geometry angle bands need to be attached to each image.'''

  #==================================================================================================
  # Create a scored image collection (attach a score image for each image in the given collection)
  #==================================================================================================
  scored_collection = score_collection(collection, SsrData, midDate, ExtraBandCode)

  #==================================================================================================
  # Create and return a mosaic based on associated score maps
  #==================================================================================================  
  return scored_collection.qualityMosaic(Img.pix_score) #.set('system:time_start', midDate.millis())






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
def LEAF_Mosaic(fun_param_dict, region, CloudRate = -100):
  '''Creates a mosaic image specially for vegetation parameter extraction with LEAF tool.
     
     Args:
       fun_param_dict({}): a function parameter dictionary containing various single parameters;    
       region(ee.Geometry): the spatial region of a mosaic image;
       CloudRate(float): a given cloud coverage rate.'''
  #==========================================================================================================
  # Determine time period based on the given year and month
  #==========================================================================================================
  year  = int(fun_param_dict['year'])
  month = int(fun_param_dict['month'])
  start, stop = IS.month_range(year, month)

  #==========================================================================================================
  # Create a mosaic image including geometry angle images required by vegetation parameter extraction
  # Note: the value range required by LEAF production with S2 and LS data are different.
  # For Sentinel-2 data, the value range must be [0, 1], while for Landsat, just raw value range.
  #==========================================================================================================
  ssr_data = Img.SSR_META_DICT[fun_param_dict['sensor']]
  ssr_code = ssr_data['SSR_CODE']
  
  if ssr_code < Img.MAX_LS_CODE:  #For Landsat data
    return LS89_PeriodMosaic(region, year, start, stop, EXTRA_ANGLE)

  else:  # For Sentinel-2 data
    mosaic = HomoPeriodMosaic(ssr_data, region, year, -1, start, stop, EXTRA_ANGLE)    
    return Img.apply_gain_offset(mosaic, ssr_data, 1, False)






######################################################################################################
# Description: Merges the two mosaics created from the images acquired with the same sensor.
#     
# Revision history:  2020-Dec-07  Lixin Sun  Initial creation
#
######################################################################################################
def MergeMosaics(BaseMosaic, SecondMosaic, SsrData, ThreshFactor):
  '''Merge the mosaics created from the images acquired with the same sensor.
  Args:
    BaseMosaic(ee.Image): The base/target mosaic image; 
    SecondMosaic(ee.Image): The secondary mosaic image;
    SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
    ThreshFactor(float): A factor for adjusting threshold score.'''
  #==================================================================================================
  # Fill the masked/missing pixels in target mosaic with the pixels from the secondary mosaic
  #==================================================================================================
  target = ee.Image(BaseMosaic).selfMask()
  second = ee.Image(SecondMosaic).selfMask()
  target = target.unmask(second)  

  #==================================================================================================
  # If the quality scores of the secondary mosaic are significantly higher than target mosaic, then
  # replace target mosaic pixels with the pixels in the secondary mosaic
  #==================================================================================================
  NIR_name     = SsrData['NIR']
  target_NIR   = target.select(NIR_name)
  refer_NIR    = second.select(NIR_name)

  target_score = target.select(Img.pix_score)
  refer_score  = second.select(Img.pix_score)
  thresh_score = target_score.divide(ee.Image(ThreshFactor))
  
  replace_cond = (refer_NIR.gt(target_NIR)).And(refer_score.subtract(thresh_score).gt(target_score))
  #replace_cond = target_SW2.lt(2.5).And(refer_NIR.gt(target_NIR)).And(refer_score.subtract(thresh_score).gt(target_score))

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
  max_ref = 100 if SensorBase > Img.MAX_LS_CODE else 1000
  
  print('\n\n<MergeMixMosaics> Sensor code of base mosaic = ', SensorBase)
  print('<MergeMixMosaics> Bands in 1st mosaic = ', MosaicBase.bandNames().getInfo())
  print('<MergeMixMosaics> Bands in 2nd mosaic = ', Mosaic2nd.bandNames().getInfo())
  #==================================================================================================
  # Attach a sensor code band to each mosaic image
  # Note: pixel masks of both mosaic must be applied to their corresponding sensor code images 
  #==================================================================================================  
  virtual_ssr = Sensor2nd if SensorBase > Img.MAX_LS_CODE else SensorBase
  pix_mask1 = IM.Img_ValueMask(MosaicBase, virtual_ssr, DataUnit, max_ref).Not()
  pix_mask2 = IM.Img_ValueMask(Mosaic2nd,  Sensor2nd,   DataUnit, max_ref).Not()

  ssr_code_img1 = pix_mask1.multiply(SensorBase).rename([Img.mosaic_ssr_code])
  ssr_code_img2 = pix_mask2.multiply(Sensor2nd ).rename([Img.mosaic_ssr_code])

  mosaic1 = MosaicBase.addBands(ssr_code_img1)
  mosaic2 = Mosaic2nd.addBands(ssr_code_img2)
  print('<MergeMixMosaics> Bands in 1st mosaic = ', mosaic1.bandNames().getInfo())
  print('<MergeMixMosaics> Bands in 2nd mosaic = ', mosaic2.bandNames().getInfo())
  #==================================================================================================
  # Fill the gaps in base mosaic with the valid pixels in the 2nd mosaic
  #==================================================================================================
  mosaic1 = mosaic1.unmask(mosaic2)

  diff_thresh = 1.2 if SensorBase > Img.MAX_LS_CODE else 0.7
  score1 = mosaic1.select(Img.pix_score).add(diff_thresh)
  score2 = mosaic2.select(Img.pix_score)  
  
  mosaic = mosaic1.where(score2.gt(score1), mosaic2) 
  return ee.Image(mosaic.selfMask())






###################################################################################################
# Description: This function creates a mosaic image for a defined region using the images acquired
#              by one sensor during a time period.
#
# Revision history:  2021-Jun-02  Lixin Sun  Initial creation
#                    2021-Oct-05  Lixin Sun  Added an output option 
###################################################################################################
def HomoPeriodMosaic(SsrData, Region, TargetYear, NbYears, StartDate, StopDate, ExtraBandCode):
  '''Creates a mosaic image for a region using the images acquired during a period of time. 
     
  Args:
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
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
  coll_target    = IS.getCollection(SsrData, Region, start, stop)
  #print("<HomoPeriodMosaic> numb of images in collection = ", coll_target.size().getInfo())
  midDate_target = IS.period_centre(start, stop)
  mosaic_target  = coll_mosaic(coll_target, SsrData, midDate_target, ExtraBandCode)

  if nb_years <= 1:
    return mosaic_target

  elif nb_years == 2: 
    # Create a mosaic image for the year before the target
    PrevYear = TargetYear - 1
    start    = start.update(PrevYear)
    stop     = stop.update(PrevYear)

    coll_before    = IS.getCollection(SsrData, Region, start, stop)
    midDate_before = IS.period_centre(start, stop)
    mosaic_before  = coll_mosaic(coll_before, SsrData, midDate_before, ExtraBandCode)

    # Merge the two mosaic images into one and return it  
    return MergeMosaics(mosaic_target, mosaic_before, SsrData, 3.0)

  else: 
    # Create mosaic image for the year after the target
    AfterYear = TargetYear + 1
    start     = start.update(AfterYear)
    stop      = stop.update(AfterYear)

    coll_after    = IS.getCollection(SsrData, Region, start, stop)
    midDate_after = IS.period_centre(start, stop)
    mosaic_after  = coll_mosaic(coll_after, SsrData, midDate_after, ExtraBandCode)

    mosaic_target = MergeMosaics(mosaic_target, mosaic_after, SsrData, 3.0)

    # Create mosaic image for the year before the target
    PrevYear = TargetYear - 1
    start    = start.update(PrevYear)
    stop     = stop.update(PrevYear)

    coll_before    = IS.getCollection(SsrData, Region, start, stop)
    midDate_before = IS.period_centre(start, stop)
    mosaic_before  = coll_mosaic(coll_before, SsrData, midDate_before, ExtraBandCode)
    
    return MergeMosaics(mosaic_target, mosaic_before, SsrData, 3.0)  




##########################################################################################################
# Description: This function creates an mosaic image for a region using the images acquired during one to 
#              three peak seasons (from June 15 to September 15).
#
# Revision history:  2021-Jul-07  Lixin Sun  Initial creation using JavaScript
#                    
##########################################################################################################
def HomoPeakMosaic(Ssrdata, Region, TargetYear, NbYears, ExtraBandCode):
  '''Creates a mosaic image for a region using the images acquired during one, two or three
     peak-growing seasons (from June 15 to September 15). 
     
  Args:
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
      Region(ee.Geometry): A spatial region of a ROI;
      TargetYear(int): An integer representing a targeted year (e.g., 2020);
      NbYears(int): The number of peak seasons (1, 2 or 3);
      ExtraBandCode(int): A integer representing the band type to be attached to image.'''  
  # Cast some input parameters 
  n_years = int(NbYears)

  # Get a peak season mosaic for targeted year
  start, stop = IS.summer_range(TargetYear)
  
  return HomoPeriodMosaic(Ssrdata, Region, TargetYear, n_years, start, stop, ExtraBandCode)





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
  midDate   = IS.period_centre(start, stop)

  #================================================================================================
  # Create two Landsat mosaics
  #================================================================================================
  img_coll1 = IS.getCollection(ssr_code1, data_unit, Region, start, stop)
  mosaic1   = coll_mosaic(img_coll1, ssr_code1, data_unit, midDate, ExtraBandCode)  

  img_coll2 = IS.getCollection(ssr_code2, data_unit, Region, start, stop)
  mosaic2   = coll_mosaic(img_coll2, ssr_code2, data_unit, midDate, ExtraBandCode)  

  #================================================================================================
  # Deal with the case when Landsat 7 needs to be merged with Landsat 8 data 
  #================================================================================================
  if ssr_code1 == Img.LS8_sensor and ssr_code2 == Img.LS7_sensor:
    temp_ls7_mosaic = mosaic2.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']) \
                             .rename(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'])

    ls7_mosaic = mosaic2.select(['SR_B1']).addBands(temp_ls7_mosaic)

    # Add rest other bands
    if ExtraBandCode == EXTRA_ANGLE:
      mosaic1 = mosaic1.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'cosVZA', 'cosSZA', 'cosRAA', Img.pix_score, Img.pix_date])
      rest_bands = ['cosVZA', 'cosSZA', 'cosRAA', Img.pix_score, Img.pix_date]
    elif ExtraBandCode == EXTRA_NDVI:
      mosaic1 = mosaic1.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', Img.pix_date, Img.PARAM_NDVI, Img.pix_score])
      rest_bands = [Img.pix_date, Img.PARAM_NDVI, Img.pix_score]
    else:
      mosaic1 = mosaic1.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', Img.pix_date, Img.pix_score])
      rest_bands = [Img.pix_date, Img.pix_score]

    ls7_mosaic = ls7_mosaic.addBands(mosaic2.select(rest_bands))

    test_ls7_mosaic = ls7_mosaic.focal_mean(1, 'circle', 'pixels', 10)
    mosaic2         = ls7_mosaic.unmask(test_ls7_mosaic)

  return MergeMixMosaics(mosaic1, mosaic2, ssr_code1, ssr_code2, data_unit)




###################################################################################################
# Description: This function attaches FOUR (VZA, VAA, SZA and SAA) geometry angle bands from
#              a Landsat TOA reflectance image to a given Landsat surface reflectance image.
#
# Note:        This function is specifically developed for LEAF production with Landsat 8 images.
# 
# Revision history:  2022-Dec-07  Lixin Sun  Initial creation
#
###################################################################################################
def attach_LSAngleBands(LS_sr_img, LS_toa_img_coll):
  '''attaches FOUR (VZA, VAA, SZA and SAA) geometry angle bands from a Landsat TOA reflectance 
     image to a given Landsat surface reflectance image. 
     
  Args:
      LS_sr_img(ee.Image): A given Landsat surface reflectance image;
      LS_toa_img_coll(ee.ImageCollection): A collection of Landsat TOA reflectance images.'''
  sr_system_indx = LS_sr_img.get('system:index')

  # Extract angle bands from a corresponding TOA reflectance image
  rad = ee.Number(math.pi/180.0)  
  angle_imgs = LS_toa_img_coll.filterMetadata('system:index','equals', sr_system_indx) \
                              .first() \
                              .select(['VZA','VAA','SZA','SAA']) \
                              .multiply(rad)
  
  # Calculate cosin of scattering angle
  def cosScatteringAngle(image):
    image = ee.Image(image)
    sza = image.select(['SZA'])
    vza = image.select(['VZA'])
    #saa = image.select(['SAA'])
    #vaa = image.select(['VAA'])

    return sza.cos().multiply(vza.cos()) \
          .add(sza.sin().multiply(vza.sin()).multiply(sza.cos().subtract(vza.cos())))

  cos_scatter = cosScatteringAngle(angle_imgs).rename(['cosSA'])

  # Calculate cos of the angle images and then attach them to the given surface reflectance image  
  angle_imgs = angle_imgs.cos().rename(['cosVZA','cosVAA','cosSZA','cosSAA'])

  return LS_sr_img.addBands(angle_imgs).addBands(cos_scatter)





###################################################################################################
# Description: This function creates a mosaic image for a specified region using Landsat 8 (and 
#              Landsat 9 if after 2022) images.
#
# Revision history:  2022-Dec-07  Lixin Sun  Initial creation
#
###################################################################################################
def LS89_PeriodMosaic(Region, Year, StartDate, StopDate, ExtraBandCode):
  '''Creates a mosaic image for a region using Landsat 8/9 images acquired during a period of time. 
     
  Args:
      Region(ee.Geometry): The spatial polygon of a ROI;
      Year(int): A specified target year (must be a regular integer);
      Startdate(ee.Date or string): The start date string (e.g., '2020-06-01') or ee.Date object;
      StopDate(ee.Date or string): The end date string (e.g., '2020-06-30') or ee.Date object;
      ExtraBandCode(int): A integer code representing band type to be attached additionaly.''' 

  #================================================================================================
  # Determine the time period based on a given year and period defined by StartDate and StopDate
  #================================================================================================  
  start   = ee.Date(StartDate).update(Year)
  stop    = ee.Date(StopDate).update(Year)
  midDate = IS.period_centre(start, stop)

  #================================================================================================
  # Create surface reflectance image collection for Landsat 8 and attach angle bands from 
  # corresponding TOA images 
  #================================================================================================
  L8_sr_data   = Img.SSR_META_DICT['L8_SR']
  sr_img_coll  = IS.getCollection(L8_sr_data, Region, start, stop)

  L8_toa_data  = Img.SSR_META_DICT['L8_TOA']
  toa_img_coll = IS.getCollection(L8_toa_data, Region, start, stop)
  
  sr_img_coll  = sr_img_coll.map(lambda image: attach_LSAngleBands(image, toa_img_coll))
  
  #================================================================================================
  # For the years after 2021, (1) create surface reflectance image collection for Landsat 9 and 
  # attach angle bands from corresponding TOA images; (2) merge the surface reflectance image 
  # collections of LS8 and LS9.
  #================================================================================================
  if Year > 2021:
    L9_sr_data     = Img.SSR_META_DICT['L9_SR']
    l9_sr_img_coll = IS.getCollection(L9_sr_data, Region, start, stop)

    L9_toa_data     = Img.SSR_META_DICT['L9_TOA']
    l9_toa_img_coll = IS.getCollection(L9_toa_data, Region, start, stop)
  
    l9_sr_img_coll  = l9_sr_img_coll.map(lambda image: attach_LSAngleBands(image, l9_toa_img_coll))
    
    sr_img_coll = sr_img_coll.merge(l9_sr_img_coll)

  return coll_mosaic(sr_img_coll, L8_sr_data, midDate, EXTRA_NONE)




#############################################################################################################
# Description: This function creates a mosaic image containing only SIX standard bands (blue, green,
#              red, NIR, SWIR1 and SWIR2)
#
# Revision history:  2021-Jul-01  Lixin Sun  Initial creation
#                    2021-Nov-22  Lixin Sun  Converted from JavaScript code
#############################################################################################################
def STD_bands_mosaic(inParams):
  '''This function creates a mosaic image containing only SIX standard bands (blue, green, red, NIR, SWIR1 and SWIR2).
     
     Args:
       inParams(Dictionary): A dictionary containing all required parameters. 
  '''
  #===================================================================================================
  # Create a required (annual) mosaic. Note Classification only needs annual mosaic 
  #===================================================================================================
  mosaic_name = inParams['tile_names'][0]
  if eoTG.is_valid_tile_name(mosaic_name) == True:
    region = eoTG.PolygonDict.get(mosaic_name)      
  else:
    region = eoTG.custom_RegionDict.get(mosaic_name)

  ssr_data  = Img.SSR_META_DICT[inParams['sensor']]
  targ_year = int(inParams['year'])
  nb_years  = int(inParams['nbYears'])

  #mosaic    = eoMosaic.HomoPeakMosaic(ssr_code, data_unit, region, targ_year, nb_years, eoMosaic.EXTRA_NONE)
  mosaic    = HomoPeakMosaic(ssr_data, region, targ_year, nb_years, EXTRA_NONE)
  #===================================================================================================
  # Apply gain and offset to the mosaic image
  #===================================================================================================
  mosaic = Img.apply_gain_offset(mosaic, ssr_data, 100, True)
  
  #===================================================================================================
  # Extract SIX standard bands and then rename them
  #===================================================================================================
  six_core_bands = ee.List(ssr_data['SIX_BANDS'])

  return mosaic.select(six_core_bands, Img.STD_6_BANDS)







#############################################################################################################
# Description: This function exports a given mosaic image to a specified location (either Google Drive or
#              Google Cloud Storage). The filenames of the exported images will be automatically generated 
#              based on tile name, image acquisition time and spatial resolution.
#
# Revision history:  2022-Mar-30  Lixin Sun  Initial creation 
#
#############################################################################################################
def export_mosaic(fun_Param_dict, mosaic, SsrData, polygon, task_list):
  '''Exports one set of LEAF products to either Google Drive or Google Cloud Storage

     Args:
       fun_Param_dict(dictionary): a dictionary storing other required running parameters;
       mosaic(ee.Image): the mosaic image to be exported;
       SsrData(Dictionary): A dictionary containing all info on a sensor type;
       polygon(ee.Geometry): the spatial region of interest;
       task_list([]): a list storing the links to exporting tasks.'''
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
  exp_polygon = eoTG.expandSquare(polygon, 0.02) 

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
    month_name = Img.get_MonthName(month)
    filePrefix = filePrefix + '_' + month_name
  
  filePrefix = filePrefix + '_' + SsrData['NAME']

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
  
  out_band_names = SsrData['OUT_BANDS']

  if out_location.find('drive') > -1:  # Export to Google Drive
    print('<export_mosaic> Exporting to Google Drive......')  
    for item in out_band_names:
      filename  = filePrefix + '_' + item + '_' + str(Scale) + 'm'

      export_dict['image'] = mosaic.select(item).multiply(ee.Image(100)).uint16()
      export_dict['description'] = filename
      export_dict['fileNamePrefix'] = filename

      task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())
    
  elif out_location.find('storage') > -1:  # Exporting to Google Cloud Storage
    print('<export_mosaic> Exporting to Google Cloud Storage......')  
    export_dict['bucket'] = str(fun_Param_dict['bucket'])    
    for item in out_band_names:
      filename  = filePrefix + '_' + item + '_' + str(Scale) + 'm'
      
      export_dict['image'] = mosaic.select(item).multiply(ee.Image(100)).uint16()
      export_dict['description'] = filename
      export_dict['fileNamePrefix'] = filename

      task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())

  elif out_location.find('asset') > -1:
    print('<export_mosaic> Exporting to Google Earth Assets......')      
    for item in out_band_names:
      filename  = filePrefix + '_' + item + '_' + str(Scale) + 'm'
      
      export_dict['image'] = mosaic.select(item).multiply(ee.Image(100)).uint16()
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
  ssr_data  = Img.SSR_META_DICT[exe_Param_dict['sensor']]
  year      = int(exe_Param_dict['year'])
  nYears    = int(exe_Param_dict['nbYears'])    

  task_list = []  
  # Loop through each tile
  for tile_name in exe_Param_dict['tile_names']:
    fun_Param_dict['tile_name'] = tile_name

    # Create a mosaic region ee.Geometry object 
    if eoTG.is_valid_tile_name(tile_name) == True:
      region = eoTG.PolygonDict.get(tile_name)      
    else:
      region = eoTG.custom_RegionDict.get(tile_name)

    if nYears > 0:  # Create a peak-season mosaic for a specific region/tile
      mosaic = HomoPeakMosaic(ssr_data, region, year, nYears, ExtraBandCode)
      mosaic = Img.apply_gain_offset(mosaic, ssr_data, 100, False)

      mask   = IM.Img_ValidMask(mosaic, ssr_data, 100).Not()
      mosaic = mosaic.updateMask(mask)

      # Export spectral mosaic images  
      export_mosaic(fun_Param_dict, mosaic, ssr_data, region, task_list)
    else:  # Create a monthly mosaic for a specific region/tile
      for month in exe_Param_dict['months']:
        fun_Param_dict['month'] = month
        start, stop = IS.month_range(year, month)
        mosaic = HomoPeriodMosaic(ssr_data, region, year, nYears, start, stop, ExtraBandCode)
        mosaic = Img.apply_gain_offset(mosaic, ssr_data, 100, False)

        mask   = IM.Img_ValidMask(mosaic, ssr_data, 100).Not()
        mosaic = mosaic.updateMask(mask)

        # Export spectral mosaic images
        export_mosaic(fun_Param_dict, mosaic, ssr_data, region, task_list)   
      '''
      fun_Param_dict['month'] = 8
      start, stop = IS.month_range(year, 8)
      mosaic = HomoPeriodMosaic(ssr_data, region, year, nYears, start, stop, ExtraBandCode)
      mosaic = Img.apply_gain_offset(mosaic, ssr_data, 100, False)

      mask   = IM.Img_ValidMask(mosaic, ssr_data, 100).Not()
      mosaic = mosaic.updateMask(mask)
      return mosaic, mask
      '''
  #return task_list