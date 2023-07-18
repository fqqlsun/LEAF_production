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
EXTRA_CODE  = 3     # sensor code


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
#              (3) When input is surface reflectance, the blue values of some pixels could be smaller
#                  than ONE. In this case, One should be added to blue reflectance, so that IR-blue
#                  won't be too large.   
#
# Revision history:  2022-Mar-15  Lixin Sun  Initial creation
#                    2023-Apr-03  Lixin Sun  (1) Introduce a new method for generating blue values
#                                                when the original blue values are extremely low
#                                            (2) Introduce a way for dealing with dark vegetated 
#                                                targets. The reason of doing this is because of 
#                                                blue-band shift strategy does not work well with
#                                                dark vegetated targets. 
######################################################################################################
def IR_Blue_ratio(blu, red, nir, sw1):
  #==================================================================================================
  # Calculate main spectral score
  #==================================================================================================
  #new_blu = blu.where(blu.lt(0.5), ee.Image.constant(0.5))
  #new_blu = new_blu.where(new_blu.lt(red.divide(3)), red.divide(2))   # handle artifact of AC  
  ndvi         = nir.subtract(red).divide(nir.add(red))
  absolute_veg = ndvi.gt(0.85).And(red.gt(0.2))
  min_blue     = ndvi.multiply(0).add(0.333) 
  min_blue     = min_blue.where(absolute_veg, ee.Image(0.1)) 

  max_IR  = nir.max(sw1)
  new_blu = blu.where(blu.lt(min_blue), red.abs().divide(3).min(max_IR.divide(30)).min(min_blue))   # handle artifact of AC 

  shift   = ee.Image.constant(25).divide(max_IR)  
  #shift   = ee.Image.constant(20).subtract(max_IR).divide(ee.Image.constant(3)).exp()  
  #shift = ee.Image.exp(ee.Image.constant(20).subtract(max_IR))  dose not work

  score = max_IR.divide(new_blu.add(shift))
  
  #==================================================================================================
  # Deal with dark vegetated targets.
  # Above blue-band shift does not work well for dark vegetated targets, so there must be a strategy
  # to deal with dark vegetated targets.
  #==================================================================================================
  #return score.where(absolute_veg, max_IR.divide(new_blu).multiply(10))
  return score  #.where(absolute_veg, score.multiply(10))





######################################################################################################
# Description: This function creates a vegetated pixel score image.
#
# Note:        The value range of the given image must be in between 0 and 100
#
# Revision history:  2022-Mar-15  Lixin Sun  Initial creation
#                    2023-Mar-24  Lixin Sun  Finalized scoring system for vegetated targets
#
######################################################################################################
def get_veg_score(blu, grn, red, nir, sw1, sw2):
  #==================================================================================================
  # Calculate base score for vegetated targets. 
  # Note: for vegetated targets, there is also a need to apply "blue band shift" as does for 
  #       non-vegetated targets    
  # 2023-04-06: "nir.multiply(10).divide(STD_blu.multiply(10).add(nir))" does not work 
  #==================================================================================================  
  #score = IR_Blue_ratio(blu, red, nir, sw1)  

  ndvi      = nir.subtract(red).divide(nir.add(red))
  model_blu = sw2.divide(4.0)
  STD_blu   = blu.where(blu.lt(0.1), model_blu)
  shift     = ee.Image.constant(15).divide(nir)   # 15 seems better than 25
  #shift     = shift.where(sw2.gt(1.2).And(ndvi.gt(0.8)).And(nir.gt(13)), ee.Image(0))

  score     = nir.divide(STD_blu.add(shift))

  #==================================================================================================
  # Apply HOT penalty, an important strategy for excluding Hazy pixels over dark vegetated pixels
  # Note: (1) Blue shift is necessary for excluding shadow pixels, but this will cause hazy pixels 
  #           are selected over dense vegetated area.
  #       (2) HOT penalty only needs to be applied to dark and dense (e.g., nir < 15 and ndvi > 0.75)
  #           vegetated targets 
  #==================================================================================================
  haze_pena = blu.subtract(model_blu)
  haze_cond = haze_pena.gt(0).And(haze_pena.lt(0.3)).And(ndvi.gt(0.8))
  score     = score.where(haze_cond, score.subtract(haze_pena.multiply(10)))
  
  #==================================================================================================
  # Apply bottom line for spectral values of vegetated pixels
  #==================================================================================================    
  spec_min = blu.min(grn).min(red).min(nir).min(sw1).min(sw2)
  score    = score.where(spec_min.lt(ndvi.multiply(-1)), ee.Image.constant(-1000))

  return score 




######################################################################################################
# Description: This function creates a score image assuming all pixels are non-vegetated targets.
#
# Note:        The value range of the given image must be in between 0 and 100
#
# Revision history:  2022-Mar-15  Lixin Sun  Initial creation
#
######################################################################################################
def get_nonveg_score(blu, grn, red, nir, sw1, sw2, median_sw1):
  #==================================================================================================
  # Calculate main spectral score
  #==================================================================================================
  #score = IR_Blue_ratio(blu, red, nir, sw1)  
  blu_refer = grn.min(red)
  blu_refer = blu_refer.where(grn.lt(0).Or(red.lt(0)), grn.max(red)).multiply(0.7)

  STD_blue  = blu.where(blu.lt(blu_refer), blu_refer) 

  max_IR    = nir.max(sw1)
  shift     = ee.Image.constant(35).divide(max_IR)
  score     = max_IR.divide(STD_blue.add(shift))

  #==================================================================================================
  # Deal with the logics of spectral shape 
  # For non-vegetated targets, blue value is normally smaller than SWIR1 value 
  #==================================================================================================
  penalty = blu.subtract(sw1).abs()
  score   = score.where(sw1.lt(blu), score.subtract(penalty)) 
  
  '''
  GB_diff  = grn.subtract(blu).abs()
  RG_diff  = red.subtract(grn).abs()
  max_diff = GB_diff.max(RG_diff)
  min_diff = GB_diff.min(RG_diff)
  diff_ratio = max_diff.divide(min_diff.add(0.001))
  
  score   = score.where(diff_ratio.gt(4), score.subtract(diff_ratio)) 
  '''
  
  #==================================================================================================
  # Apply bottom line for spectral values of non-vegetated pixels
  #==================================================================================================  
  spec_min = blu.min(grn).min(red).min(nir).min(sw1).min(sw2)  
  score    = score.where(spec_min.lt(0.5).Or(max_IR.lt(2)), ee.Image.constant(-10000))

  return ee.Image(score)  #.multiply(ee.Image.constant(1000))





######################################################################################################
# Description: This function creates a score image assuming all pixels are land targets.
#
# Note:        The value range of the given image must be in between 0 and 100
#
# Revision history:  2022-Mar-15  Lixin Sun  Initial creation
#                    2023-Apr-03  Lixin Sun  (1) Apply inbalance visible penalty to land targets, no
#                                            matter vegetated or non-vegetated targets; (2) added a 
#                                            filter to exclude pixels with land score less than ONE.
#
######################################################################################################
def get_land_score(blu, grn, red, nir, sw1, sw2, median_sw1):
  #==================================================================================================
  # Calculate main spectral score
  #==================================================================================================
  score = IR_Blue_ratio(blu, red, nir, sw1)  

  #==================================================================================================
  # Apply inbalance visible penalty for non-vegetated targets
  #==================================================================================================
  ndvi      = nir.subtract(red).divide(nir.add(red))
  mean_VIS  = blu.add(grn).add(red).divide(3) 
  inbalance = grn.subtract(blu).abs().add(red.subtract(grn).abs()).divide(mean_VIS)

  score     = score.where(ndvi.lt(0.5), score.subtract(inbalance))

  #==================================================================================================
  # Apply HOT penalty, an important strategy for excluding Hazy pixels over dark vegetated pixels
  #==================================================================================================
  hot       = blu.subtract(red.multiply(0.3))
  hot_score = score.subtract(hot)   #.multiply(ee.Image.constant(1).subtract(hot)).add(ee.Image(1)) 
  score     = score.where(hot.gt(0).And(ndvi.gt(0.85)), hot_score)

  #==================================================================================================
  # Apply bottom line for spectral values of non-vegetated pixels
  #==================================================================================================  
  spec_min = blu.min(grn).min(red).min(nir).min(sw1).min(sw2)  
  score    = score.where(spec_min.lt(ndvi.multiply(-1)), ee.Image.constant(-10000))
  score    = score.where(score.lt(1), ee.Image.constant(-10000))

  return ee.Image(score)




######################################################################################################
# Description: This function creates a water pixel score image
#
# Note: (1) One criteria that can discriminate water pixels from shadow pixels is the relation between 
#           blue and SWIR1 bands. For water pixels, blue values are much bigger than SWIR1 values. 
#           This is the reason why we have the third criteria in "invalid_cond".
#       (2) The water targets need to divided into three types: clean water, muddy water and snow/ice.
#           they must be handled differently.
#  
# Revision history:  2022-Mar-15  Lixin Sun  Initial creation
#                    2023-Apr-03  Lixin Sun  Divided water targets into three subgroups: clean water,
#                                            Muddy water and snow/ice and applied different scoring
#                                            systems for them.
######################################################################################################
def get_water_score(blu, red, grn, nir, sw1, sw2, median_sw1):
  max_VIS = blu.max(grn)
  max_SW  = sw1.max(sw2)
  new_nir = nir.where(nir.lt(0), max_SW)

  VIS_SWR_ratio = max_VIS.multiply(10).divide(max_SW.multiply(10).add(max_VIS))
  VIS_NIR_ratio = max_VIS.multiply(10).divide(new_nir.multiply(10).add(max_VIS))

  return VIS_SWR_ratio.max(VIS_NIR_ratio)
  #===================================================================================================
  # score for clean water (blue < 5): max_ratio
  #===================================================================================================
  max_VIS = blu.max(grn)
  max_SW  = sw1.max(sw2)
  new_nir = nir.where(nir.lt(0), max_SW)

  VIS_SWR_ratio = max_VIS.divide(max_SW.add(0.01))
  VIS_NIR_ratio = max_VIS.divide(new_nir.add(0.01))
  clean_score   = VIS_SWR_ratio.max(VIS_NIR_ratio)

  #===================================================================================================
  # score for muddy water (2 < blue < 15): max_ratio(with shift)/max(max_VIS, max_SW)
  #===================================================================================================
  shift         = max_VIS.multiply(0.1)
  VIS_SWR_ratio = max_VIS.divide(max_SW.add(shift)) 
  VIS_NIR_ratio = max_VIS.divide(new_nir.add(shift))

  muddy_score   = VIS_SWR_ratio.max(VIS_NIR_ratio).divide(max_VIS.max(max_SW))

  #===================================================================================================
  # score for snow/ice (blue > 15): -Blue
  #===================================================================================================
  ice_score = max_VIS.multiply(-1)

  score = clean_score.where(max_VIS.gt(2), muddy_score)
  score = score.where(max_VIS.gt(15), ice_score)

  #===================================================================================================
  # If VISIBLE and NIR bands are lower than 1, then it most likely is a water pixel
  # Note: "median_sw1.lt(5)" means temporal analysis indicated that a location is a water pixel  
  #===================================================================================================  
  max_spec  = blu.max(grn).max(red).max(nir)  #.max(sw1).max(sw2)
  max_score = blu.multiply(0).add(1000)
  abs_water = max_spec.lt(1).And(max_VIS.gt(0.1)).And(median_sw1.lt(5))
  score     = score.where(abs_water, max_score)  #Even when "max_SW" is bigger than "max_VIS"
  
  #==================================================================================================
  # Apply bottom line for spectral values of water pixels
  #==================================================================================================  
  IR_max = nir.max(sw1).max(sw2)
  score  = score.where(IR_max.lt(0), ee.Image.constant(-1000))

  return ee.Image(score) 





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
def get_score_map(median_sw1, inMidDate, SsrData, image):
  '''Return a pixel score image corresponding to a given image
  
  Args:      
      median_blue(ee.Image): The blue band of a median mosaic. Could be used as the blue reference for non-veg pixels; 
      inMidDate(ee.Date): The centre date of a time period for a mosaic generation.
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
      image(ee.Image): A given ee.Image object with cloud/shadow mask applied.'''
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
  #land_score   = ee.Image(get_land_score(blu, grn, red, nir, sw1, sw2, median_sw1))
  veg_score    = ee.Image(get_veg_score(blu, grn, red, nir, sw1, sw2))
  nonveg_score = ee.Image(get_nonveg_score(blu, grn, red, nir, sw1, sw2, median_sw1))  
  water_score  = ee.Image(get_water_score(blu, grn, red, nir, sw1, sw2, median_sw1))

  ndvi  = nir.subtract(red).divide(nir.add(red))  
  score = nonveg_score   #.max(nonveg_score).max(water_score)  
  score = score.where(ndvi.gt(0.5).And(nir.gt(5)), veg_score)
  score = score.max(water_score)
  #score = veg_score
  #==================================================================================================
  # Calculate vagetated and non-vegetated scores
  #==================================================================================================  
  '''
  max_IR    = nir.max(sw1)
  NDVI      = nir.subtract(red).divide(nir.add(red))  
  
  score     = veg_score.multiply(ee.Image.constant(0)).add(ee.Image.constant(-1000))
  score     = score.where(NDVI.gt(0.5).And(max_IR.gt(5)), veg_score)
  score     = score.where(score.lt(-900).And(max_IR.gt(5)), nonveg_score)
  score     = score.where(score.lt(-900), water_score)
  '''

  #==================================================================================================
  # Apply time scores to vegetation targets 
  #==================================================================================================
  ssr_code   = SsrData['SSR_CODE']
  time_score = ee.Image(get_time_score(image, inMidDate, ssr_code))
  #score      = ee.Image(score).multiply(time_score) 
 
  return ee.Image(score)





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
  #data_unit  = SsrData['DATA_UNIT']

  #base_score = IR_Blue_ratio(blu, red, nir, sw1)

  #==================================================================================================
  # Calculate scores for vagetated targets only and set scores for pixels with NDVI < 0.3 to zero
  #==================================================================================================  
  veg_score  = get_veg_score(blu, grn, red, nir, sw2) 

  zero_score = sw2.multiply(ee.Image(0.0)) #.add(cld_score.divide(ee.Image(200)))
  NDVI_img   = nir.subtract(red).divide(nir.add(red))

  return veg_score.where(NDVI_img.lt(ee.Image(0.3)), zero_score)





######################################################################################################
# Description: This function attachs a smoothed score image to the given image
#
# Note:        The value range of "median_blue" is already in between 0 and 100
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def attach_Score(median_sw1, midDate, SsrData, Image):
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
  score_map = get_score_map(median_sw1, midDate, SsrData, Image)

  # Define a boxcar or low-pass kernel.
  #boxcar = ee.Kernel.circle(radius = 2, units = 'pixels', normalize = True)

  # Smooth the image by convolving with the boxcar kernel.
  #smoothed_score_map = score_map.convolve(boxcar)

  return Image.addBands(score_map.select([0], [Img.pix_score]))
             




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
def score_collection(collection, SsrData, midDate, ExtraBandCode, modis_img = None):
  '''Attaches a score, acquisition date and some specified bands to each image of a collection.
  
  Args:
     collection(ee.ImageCollection): A given image collection;
     SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
     midDate(ee.Date): The centre date of a time period for a mosaic generation;
     ExtraBandCode(int): The integer code representing band type to be added additionally.'''
  #print('<score_collection> band names of 1st image = ', collection.first().bandNames().getInfo())
  #print('<score_collection> the given collection = ', collection.size().getInfo())
  #==================================================================================================
  # Apply inherent cloud and shadow masks to each image in thegiven image collection
  # Note: doing mosaic without applying inherent masks will cause some water bodies cannot be 
  #       correctly identified by mosaic algorithm (whatever a mosaic algorithm is used).
  #==================================================================================================
  def apply_mask(image):
    mask = IM.Img_VenderMask(image, SsrData, IM.CLEAR_MASK, modis_img)
    return image.updateMask(mask.Not()) 
  
  masked_ImgColl = collection.map(lambda image: apply_mask(image))
  print('\n\n<score_collection> band names:', masked_ImgColl.first().bandNames().getInfo())

  #==================================================================================================
  # Create a reference SWIR1 band
  #==================================================================================================
  sw1_name = SsrData['SW1']
  print('<score_collection> SWIR1 band name = ', sw1_name)

  def get_blue(img) :
    #valid_mask = eoImgMsk.ValidMask(img, ssr_code, data_unit).Not() 
    return img.select([sw1_name])  #.updateMask(valid_mask) # Applying mask is important here
  
  sw1_coll   = masked_ImgColl.map(lambda image: get_blue(image))
  sw1_mosaic = sw1_coll.median()

  median_sw1 = Img.apply_gain_offset(sw1_mosaic, SsrData, 100, True)  
  print('<score_collection> median_sw1 band name = ', median_sw1.bandNames().getInfo())

  #==================================================================================================
  # Attach a spectral-time score and acquisition date bands to each image in the image collection
  #==================================================================================================
  scored_ImgColl = masked_ImgColl.map(lambda image: attach_Score(median_sw1, midDate, SsrData, image)) \
                                 .map(lambda image: Img.attach_Date(image))  
  
  #==================================================================================================
  # Attach an additional bands as necessary to each image in the image collection
  #==================================================================================================  
  extra_code = int(ExtraBandCode)
  if extra_code == EXTRA_ANGLE:
    scored_ImgColl = scored_ImgColl.map(lambda image: Img.attach_S2AngleBands(image, SsrData))
  elif extra_code == EXTRA_NDVI:
    scored_ImgColl = scored_ImgColl.map(lambda image: Img.attach_NDVIBand(image, SsrData))

  # Return scored image collection  
  print('<score_collection> numb of images = ', scored_ImgColl.size().getInfo())
  print('<score_collection> band names of 1st scored image = ', scored_ImgColl.first().bandNames().getInfo())
  return scored_ImgColl




######################################################################################################
# Description: This function creates a mosaic image based on a given image collection. 
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def coll_mosaic(collection, SsrData, midDate, ExtraBandCode, modis_img = None):
  '''Create a mosaic image based on a given image collection.
  
  Args:
     collection(ee.ImageCollection): A given image collection;
     SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
     midDate(ee.Date): The centre date of a time period for a mosaic generation;
     addGeometry(boolean): A flag indicating if geometry angle bands need to be attached to each image.'''
  
  #==================================================================================================
  # Create a scored image collection (attach a score image for each image in the given collection)
  #==================================================================================================  
  scored_collection = score_collection(collection, SsrData, midDate, ExtraBandCode, modis_img)

  #==================================================================================================
  # Create and return a mosaic based on associated score maps
  #==================================================================================================  
  return scored_collection.qualityMosaic(Img.pix_score) #.set('system:time_start', midDate.millis())






#############################################################################################################
# Description: Creates a mosaic image specially for vegetation parameter extraction with LEAF tool.
#
# Note:        (1) The major difference between a mosaic for LEAF tool and general-purpose mosaic is the 
#              attachment of three imaging geometrical angle bands. 
#              (2) For Landsat and Sentinel-2 data, the Value range of returned mosaic will be different. 
#                  The value range of a Sentinel-2 mosaic is from 0 to 1, while the value range of a
#                  landsat mosaic is identical as raw data.
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
  start, stop = IS.month_range(year, month) if month > 0 and month < 13 else IS.summer_range(year)

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
def MergeMixMosaics(MosaicBase, MosaicBkUp, SensorBase, SensorBkUp):
  '''Merge the mosaics created from the images acquired with different Landsat sensors.

  Args:
    MosaicBase(ee.Image): The mosaic that will be used as a base/main one;
    MosaicBkUp(ee.Image): The mosaic that will be used to fill the gaps in the base mosaic;
    SensorBase(Dictionary): The sensor info dictionary of the base/main mosaic;
    SensorBkUp(Dictionary): The sensor info dictionary of the 2nd mosaic to fill the gaps in base mosaic.'''  
  
  #==================================================================================================
  # Refresh the masks for both given mosaic images   
  #==================================================================================================      
  mosaic_base = ee.Image(MosaicBase)
  mosaic_bkup = ee.Image(MosaicBkUp)
  
  #print('\n\n<MergeMixMosaics> Bands in initial base mosaic = ', mosaic_base.bandNames().getInfo())
  #print('<MergeMixMosaics> Bands in initial 2nd mosaic = ', mosaic_bkup.bandNames().getInfo())

  #==================================================================================================
  # Fill the gaps in base mosaic with the valid pixels in the 2nd mosaic
  #==================================================================================================
  ssr_code_base = SensorBase['SSR_CODE']
  ssr_code_bkup = SensorBkUp['SSR_CODE']

  if (ssr_code_base > Img.MAX_LS_CODE and ssr_code_bkup < Img.MAX_LS_CODE) or \
     (ssr_code_base < Img.MAX_LS_CODE and ssr_code_bkup > Img.MAX_LS_CODE):  
    #In the case when the base and backup mosaics are acquired from Sentinel-2 and Landsat  
    bands_more = [Img.pix_score, Img.pix_date, Img.mosaic_ssr_code]
    bands_base = SensorBase['SIX_BANDS'] + bands_more
    bands_bkup = SensorBkUp['SIX_BANDS'] + bands_more
    bands_final = Img.STD_6_BANDS + bands_more

    mosaic_base = mosaic_base.select(bands_base).rename(bands_final)  #.selfMask()
    mosaic_bkup = mosaic_bkup.select(bands_bkup).rename(bands_final)  #.selfMask()
    print('\n\n<MergeMixMosaics> Bands in base mosaic = ', mosaic_base.bandNames().getInfo())
    print('<MergeMixMosaics> Bands in 2nd mosaic = ', mosaic_bkup.bandNames().getInfo())

    mosaic_base = mosaic_base.unmask(mosaic_bkup)
    #==============================================================================================
    # Overwrite the pixels in the base mosaic with the pixels with significantly higher scores in 
    # backup mosaic
    #==============================================================================================
    base_score = mosaic_base.select([Img.pix_score])
    bkup_score = mosaic_bkup.select([Img.pix_score]).subtract(2)

    mosaic_base = mosaic_base.where(bkup_score.gt(base_score), mosaic_bkup)
  else:  
    mosaic_base = mosaic_base.unmask(mosaic_bkup)

  #score_main = mosaic_base.select(Img.pix_score).add(5)
  #score_2nd  = mosaic_2nd.select(Img.pix_score)  
  #out_mosaic = mosaic_base.where(score_2nd.gt(score_main), mosaic_2nd) 
  return ee.Image(mosaic_base)  #.selfMask())






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
  #modis_ssr_data = Img.SSR_META_DICT['MOD_SR']
  #modis_coll     = IS.getCollection(modis_ssr_data, Region, start, stop)
  midDate_target = IS.period_centre(start, stop)
  #modis_target   = coll_mosaic(modis_coll, modis_ssr_data, midDate_target, ExtraBandCode)  


  #==========================================================================================================
  # Get a mosaic image corresponding to a given time window in a targeted year
  #==========================================================================================================
  coll_target    = IS.getCollection(SsrData, Region, start, stop)
  #mosaic_target  = coll_mosaic(coll_target, SsrData, midDate_target, ExtraBandCode, modis_target)
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
# Description: This function returns a primary or secondary landsat sensor code based on a given
#              year.
#
# Note:        Landsat data for Canada north is not available before 2004.
#  
# Revision history:  2023-Mar-08  Lixin Sun  Initial creation
#
###################################################################################################
def LS_code_from_year(Year, prim_2nd_code):
  '''Returns a primary or secondary landsat sensor code based on a given year.
     
  Args:      
      Year(int): A specified target year (must be a regular integer);
      prim_2nd_code: An integer indicating the returned Landsat sensor code is for primary or secondary 
                     1 => primary; 2 => secondary.'''

  year = int(Year)
  
  if prim_2nd_code == 1:
    return 5 if year < 2013 else 8
  else:
    return 7 if year < 2022 else 9





###################################################################################################
# Description: This function returns a primary or secondary landsat sensor meta dictionary based on
#              a given year.
#
# Revision history:  2023-Mar-08  Lixin Sun  Initial creation
#
###################################################################################################
def LS_Dict_from_year(Year, Unit, prim_2nd_code):
  '''Returns a primary or secondary landsat sensor code based on a given year.
     
  Args:      
      Year(int): A specified target year (must be a regular integer);
      Unit(int): An integer representing data unit (1 => TOA or 2 => surface reflectance);
      prim_2nd_code: An integer indicating the returned Landsat sensor code is for primary or secondary 
                     1 => primary; 2 => secondary.'''

  year = int(Year)
  unit = int(Unit)

  ssr_code = LS_code_from_year(year, prim_2nd_code)

  unit_str  = '_SR' if unit > 1 else '_TOA'
  ssr_str   = 'L' + str(ssr_code) + unit_str 

  return Img.SSR_META_DICT[ssr_str]  






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
  # Determine a proper time period based on a given target year and an initial period 
  #================================================================================================
  year    = int(Year)
  unit    = int(DataUnit)
  start   = ee.Date(StartDate).update(Year)
  stop    = ee.Date(StopDate).update(Year)
  midDate = IS.period_centre(start, stop)

  #================================================================================================
  # Create a base Landsat mosaic image
  #================================================================================================
  ssr_main      = LS_Dict_from_year(Year, unit, 1)
  img_coll_main = IS.getCollection(ssr_main, Region, start, stop)
  mosaic_main   = coll_mosaic(img_coll_main, ssr_main, midDate, ExtraBandCode)  
  #print('\n\n<LSMix_PeriodMosaic> bands in main mosaic = ', mosaic_main.bandNames().getInfo())

  #================================================================================================
  # Create a secondary Landsat mosaic image
  #================================================================================================
  ssr_2nd       = LS_Dict_from_year(Year, unit, 2)
  img_coll_2nd  = IS.getCollection(ssr_2nd, Region, start, stop)  
  mosaic_2nd    = coll_mosaic(img_coll_2nd, ssr_2nd, midDate, ExtraBandCode)    

  #print('\n\n<LSMix_PeriodMosaic> sensor info of the 2nd sensor = ', ssr_2nd)
  #print('\n<LSMix_PeriodMosaic> size of 2nd img coll = ', img_coll_2nd.size().getInfo())

  #================================================================================================
  # Deal with the case when Landsat 7 needs to be merged with Landsat 8 data 
  #================================================================================================
  ssr_main_code = LS_code_from_year(year, 1)
  ssr_2nd_code  = LS_code_from_year(year, 2)
  #print('\n\n<LSMix_PeriodMosaic> sensor code1 and code2 = ', ssr_main_code, ssr_2nd_code)

  if ssr_main_code == Img.LS8_sensor and ssr_2nd_code == Img.LS7_sensor:
    temp_ls7_mosaic = mosaic_2nd.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']) \
                             .rename(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'])

    ls7_mosaic = mosaic_2nd.select(['SR_B1']).addBands(temp_ls7_mosaic)

    # Add rest other bands
    if ExtraBandCode == EXTRA_ANGLE:
      mosaic_main = mosaic_main.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'cosVZA', 'cosSZA', 'cosRAA', Img.pix_score, Img.pix_date])
      rest_bands = ['cosVZA', 'cosSZA', 'cosRAA', Img.pix_score, Img.pix_date]
    elif ExtraBandCode == EXTRA_NDVI:
      mosaic_main = mosaic_main.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', Img.pix_date, Img.PARAM_NDVI, Img.pix_score])
      rest_bands = [Img.pix_date, Img.PARAM_NDVI, Img.pix_score]
    else:
      mosaic_main = mosaic_main.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', Img.pix_date, Img.pix_score])
      rest_bands = [Img.pix_date, Img.pix_score]

    ls7_mosaic = ls7_mosaic.addBands(mosaic_2nd.select(rest_bands))

    test_ls7_mosaic = ls7_mosaic.focal_mean(1, 'circle', 'pixels', 2)
    mosaic_2nd      = ls7_mosaic.unmask(test_ls7_mosaic)

  # Added this line so that, when the 2nd image collection is empty (LS7 does not image in northen Canada),  
  # program still work properly.
  mosaic_2nd = ee.Algorithms.If(img_coll_2nd.size().gt(0), mosaic_2nd, mosaic_main)
  mosaic_2nd = ee.Image(mosaic_2nd)

  #================================================================================================
  # Attach sensor codes to base and backup mosaic, respectively 
  #================================================================================================
  ssr_code_base_img = ee.Image.constant(ssr_main_code).rename([Img.mosaic_ssr_code]).updateMask(mosaic_main.mask().select(0))
  ssr_code_2nd_img  = ee.Image.constant(ssr_2nd_code).rename([Img.mosaic_ssr_code]).updateMask(mosaic_2nd.mask().select(0))

  mosaic_main = mosaic_main.addBands(ssr_code_base_img)
  mosaic_2nd  = mosaic_2nd.addBands(ssr_code_2nd_img)

  return MergeMixMosaics(mosaic_main, mosaic_2nd, ssr_main, ssr_2nd)




###################################################################################################
# Description: This function creates a mosaic image for a specified region using all the LANDSAT
#              images acquired during a period of time.
#
# Revision history:  2022-May-02  Lixin Sun  Initial creation
#
###################################################################################################
def LSMix_LEAFMosaic(Region, Year, StartDate, StopDate):
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
  # Determine a proper time period based on a given target year and an initial period 
  #================================================================================================
  year    = int(Year)
  start   = ee.Date(StartDate).update(Year)
  stop    = ee.Date(StopDate).update(Year)
  midDate = IS.period_centre(start, stop)

  #================================================================================================
  # Create a base Landsat mosaic image
  #================================================================================================
  SR_SSR_base   = Img.SSR_META_DICT['L8_SR'] if year < 2022 else Img.SSR_META_DICT['L9_SR']
  img_coll_base = IS.getCollection(SR_SSR_base, Region, start, stop)

  TOA_SSR_base  = Img.SSR_META_DICT['L8_TOA'] if year < 2022 else Img.SSR_META_DICT['L9_TOA']
  toa_img_coll1 = IS.getCollection(TOA_SSR_base, Region, start, stop)
  
  img_coll_base = img_coll_base.map(lambda image: attach_LSAngleBands(image, toa_img_coll1))
  mosaic_base   = coll_mosaic(img_coll_base, SR_SSR_base, midDate, EXTRA_NONE)  

  print('\n\n<LSMix_PeriodMosaic> bands in main mosaic = ', mosaic_base.bandNames().getInfo())

  #================================================================================================
  # Create a secondary Landsat mosaic image
  #================================================================================================
  SR_SSR_2nd    = Img.SSR_META_DICT['L7_SR'] if year < 2022 else Img.SSR_META_DICT['L8_SR']
  img_coll_2nd  = IS.getCollection(SR_SSR_2nd, Region, start, stop)

  TOA_SSR_base  = Img.SSR_META_DICT['L7_TOA'] if year < 2022 else Img.SSR_META_DICT['L8_TOA']
  toa_img_coll2 = IS.getCollection(TOA_SSR_base, Region, start, stop)

  img_coll_2nd  = img_coll_2nd.map(lambda image: attach_LSAngleBands(image, toa_img_coll2))
  mosaic_2nd    = coll_mosaic(img_coll_2nd, SR_SSR_2nd, midDate, EXTRA_NONE)  

  print('<LSMix_PeriodMosaic> bands in 2nd mosaic = ', mosaic_2nd.bandNames().getInfo())

  #================================================================================================
  # Deal with the case when Landsat 7 needs to be merged with Landsat 8 data 
  #================================================================================================
  mosaic_base = mosaic_base.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'cosVZA', 'cosSZA', 'cosSA', Img.pix_score, Img.pix_date])
  
  if year < 2022:
    temp_ls7_mosaic = mosaic_2nd.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'cosVZA', 'cosSZA', 'cosSA', Img.pix_score, Img.pix_date]) \
                                .rename(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'cosVZA', 'cosSZA', 'cosSA', Img.pix_score, Img.pix_date])

    mosaic_2nd = mosaic_2nd.select(['SR_B1']).addBands(temp_ls7_mosaic)
  else:
    mosaic_2nd = mosaic_2nd.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'cosVZA', 'cosSZA', 'cosSA', Img.pix_score, Img.pix_date]) 

  return MergeMixMosaics(mosaic_base, mosaic_2nd, SR_SSR_base, SR_SSR_2nd)







###################################################################################################
# Description: This function extracts FOUR (VZA, VAA, SZA and SAA) geometry angle bands from a
#              Landsat TOA reflectance image and then attach them to a Landsat surface reflectance
#              image.
#
# Note:        This function is specifically developed for LEAF production with Landsat images.
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

  #================================================================================================
  # Extract angle bands from a corresponding TOA reflectance image
  # Note: The angle values in VZA, VAA,SZA and SAA bands are degrees scaled up with 100
  #================================================================================================
  rad = ee.Number(math.pi/180.0)  
  angle_imgs = LS_toa_img_coll.filterMetadata('system:index','equals', sr_system_indx).first() \
                              .select(['VZA','VAA','SZA','SAA']).divide(100.0).multiply(rad)
  
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
  #exp_polygon = eoTG.expandSquare(polygon, 0.02) 

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
  myCRS       = 'EPSG:3979'
  max_pixels  = 1e11
  export_dict = {'scale': int(Scale),
                 'crs': myCRS,
                 'maxPixels': max_pixels,
                 'region': polygon}
  
  out_band_names = SsrData['OUT_BANDS']

  if out_location.find('drive') > -1:  # Export to Google Drive
    print('<export_mosaic> Exporting to Google Drive......')  
    export_dict['folder'] = exportFolder
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
    asset_root = 'projects/ee-lsunott/assets/'

    for item in out_band_names:
      filename  = filePrefix + '_' + item + '_' + str(Scale) + 'm'
      
      export_dict['image'] = mosaic.select(item).multiply(ee.Image(100)).uint16()
      export_dict['description'] = filename
      export_dict['assetId'] = asset_root + exportFolder + '/' + filename

      task_list.append(ee.batch.Export.image.toAsset(**export_dict).start())
  
'''
task = ee.batch.Export.image.toAsset(**{
  'image': band4,
  'description': 'imageToAssetExample',
  'assetId': 'users/csaybar/exampleExport',
  'scale': 100,
  'region': geometry.getInfo()['coordinates']
})
'''




###################################################################################################
# Description: This function creates a mosaic image for a specified region using all available
#              images (Landsat series and Sentinel-2 A/B) acquired during a period of time.
#
# Revision history:  2023-Jun-06  Lixin Sun  Initial creation
#
###################################################################################################
def FullMix_PeriodMosaic(DataUnit, Region, Year, StartDate, StopDate, ExtraBandCode):
  '''Creates a mosaic image for a region using the images acquired during a period of time. 
     
  Args:
      DataUnit(Dictionary): Data unit code integer. 1 and 2 represent TOA and surface reflectance, respectively;
      Region(ee.Geometry): The spatial polygon of a ROI;
      Year(int): A specified target year (must be a regular integer);
      StartDate(ee.Date or string): The start date string (e.g., '2020-06-01') or ee.Date object;
      StopDate(ee.Date or string): The end date string (e.g., '2020-06-30') or ee.Date object;
      ExtraBandCode(int): A integer code representing band type to be attached additionaly.
  '''
  #================================================================================================
  # Determine a proper time period based on a given target year and an initial period 
  #================================================================================================
  year    = int(Year)
  unit    = int(DataUnit)
  start   = ee.Date(StartDate).update(Year)
  stop    = ee.Date(StopDate).update(Year)

  #================================================================================================
  # Create a mosaic image using available Sentinel-2 images
  #================================================================================================
  S2_type_str = 'S2_SR' if unit > 1 else 'S2_TOA'
  S2_ssrData  = Img.SSR_META_DICT[S2_type_str]
  print('<<<<<<<<<<<<<<<<<< start to generate mosaic with S2 images...........\n')
  s2_mosaic = HomoPeriodMosaic(S2_ssrData, Region, year, -1, start, stop, ExtraBandCode)

  #================================================================================================
  # Create a mosaic image using available Landsat series images
  #================================================================================================
  L8_type_str = 'L8_SR' if unit > 1 else 'L8_TOA'
  L8_ssrData  = Img.SSR_META_DICT[L8_type_str]
  print('<<<<<<<<<<<<<<<<<< start to generate mosaic with LS images...........\n')
  ls_mosaic   = LSMix_PeriodMosaic(unit, Region, year, start, stop, ExtraBandCode)

  #================================================================================================
  # Apply gain and offset to convert data to the same unit and use Sentinel-2 data as base mosaic 
  #================================================================================================
  s2_mosaic = Img.apply_gain_offset(s2_mosaic, S2_ssrData, 100, False)
  ls_mosaic = Img.apply_gain_offset(ls_mosaic, L8_ssrData, 100, False)
  
  s2_ssr_code = ee.Image.constant(21).rename([Img.mosaic_ssr_code]).updateMask(s2_mosaic.mask().select(0))
  s2_mosaic   = s2_mosaic.addBands(s2_ssr_code)

  return MergeMixMosaics(s2_mosaic, ls_mosaic, S2_ssrData, L8_ssrData), s2_mosaic, ls_mosaic





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