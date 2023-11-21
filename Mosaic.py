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
import eoAuxData as eoAD



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
  # Note that 86400000 is milliseconds per day
  #==================================================================================================
  millis_per_day = 86400000
  img_date   = ee.Date(image.date())  # Get the Unix date of the given image   
  img_year   = img_date.get('year')   # Get the year integer of the given image
  DOY_1st    = ee.Date.fromYMD(img_year, 1, 1).millis().divide(millis_per_day)  # the unix date of the 1st DOY 
  mid_date   = ee.Date(midDate).update(img_year)  # Corrected midDate
  
  img_date   = img_date.millis().divide(millis_per_day).subtract(DOY_1st)
  refer_date = mid_date.millis().divide(millis_per_day).subtract(DOY_1st)
  date_diff  = img_date.subtract(refer_date).abs()

  #==================================================================================================
  # Calculatr time score according to sensor type 
  #==================================================================================================
  ssr_code = int(ssr_code)

  factor  = 25 if ssr_code > Img.MAX_LS_CODE else 64
  one_img = image.select([0]).multiply(0).add(1)

  return one_img.divide((ee.Image(date_diff).divide(ee.Image(factor))).exp())




######################################################################################################
# Description: This function creates a score image for a given ee.Image object.
#   
# Note:        The value ranges of all the input spectral bands must be within [0, 100]  
#
# Revision history:  2023-Aug-25  Lixin Sun  Initial creation
#
######################################################################################################
def get_spec_score(blu, nir, med_blu, med_nir):
  maxNB   = nir.max(blu)
  minNB   = nir.min(blu)
  nir_pen = med_nir.subtract(nir).abs().exp()
  blu_pen = med_blu.subtract(blu).abs().exp()
  
  score   = maxNB.divide(minNB.add(blu_pen).add(nir_pen).add(maxNB.divide(2)))

  return ee.Image(score)




######################################################################################################
# Description: This function creates a score image assuming all the pixels are land.
#   
# Note:        The value ranges of all the input spectral bands must be within [0, 100]  
#
# Revision history:  2023-Aug-25  Lixin Sun  Initial creation
#
######################################################################################################
def get_land_score(blu, grn, red, nir, sw1, sw2, med_blu, med_nir):
  nir_pen = med_nir.subtract(nir).abs().exp()
  blu_pen = med_blu.subtract(blu).abs().exp()
  
  score   = nir.divide(blu.add(blu_pen).add(nir_pen).add(nir.subtract(2)))   #.multiply(0.1)
  #score   = blu.add(1).divide(blu.add(blu_pen).add(nir_pen))

  #==================================================================================================
  # Apply bottom line for spectral values of vegetated pixels
  #==================================================================================================  
  min_VIS   = blu.min(grn).min(red) 
  min_IR    = nir.min(sw1).min(sw2) 
  neg_score = score.abs().multiply(-1)
  
  condition = min_IR.lt(0).Or(min_VIS.lt(min_IR.divide(30.0)))
  score     = score.where(condition, neg_score)  

  #==================================================================================================
  # For some pixels, even their NDVI values are bigger than 0.5, but if they have the following band
  # relationships, they are not valided pixels, so should get negative scores:
  # (1) blue is higher than green
  # (2) red is higher than green for more 1%  
  # (3) SWIR2 is bigger than SWIR1
  #==================================================================================================
  ndvi    = nir.subtract(red).divide(nir.add(red))
  bad_veg = ndvi.gt(0.5).And(blu.gt(grn).Or(sw2.gt(sw1)))
  score   = score.where(bad_veg, neg_score)

  return ee.Image(score)





######################################################################################################
# Description: This function creates a score image assuming all the pixels are land.
#   
# Note:        The value ranges of all the input spectral bands must be within [0, 100]  
#
# Revision history:  2023-Aug-25  Lixin Sun  Initial creation
#
######################################################################################################
def get_water_score(blu, grn, red, nir, sw1, sw2, medBlue):  
  max_SW       = sw1.max(sw2)
  nir_sw_ratio = nir.add(1).divide(max_SW.add(1))  # This ratio is useful for excluding ice/snow
  shadow_pen   = medBlue.subtract(blu).abs().exp()
  numerator    = ee.Image.constant(4).subtract(max_SW) 
  denominator  = nir_sw_ratio.add(shadow_pen).add(4)

  score  = numerator.divide(denominator)

  #==================================================================================================
  # Apply bottom line for spectral values of vegetated pixels
  #==================================================================================================
  #min_VIS = blu.min(grn).min(red)
  mean_VIS = blu.add(grn).add(red).divide(3.0)
  min_IR   = nir.min(sw1).min(sw2)
  score    = score.where(mean_VIS.lt(0).Or(min_IR.lt(-1.5)), score.abs().multiply(-10))

  return ee.Image(score)




######################################################################################################
# Description: This function creates a combined (spectral and time) score map for a given image
#              (either TOA or surface reflectance).
#
# Note:        (1) This function assumes the value range of the given image is between 0 and 100
#              (2) The value range of "median_blue" is already in between 0 and 100
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#                    2023-Aug-20  Lixin Sun  Added a water map input parameter so that water pixels
#                                            can be identified.
#                    2023-Aug-24  Lixin Sun  Added the second returned image to indicate a score value
#                                            is from which type of target (non-vegetated, vegetated
#                                            or water)
#                    2023-Sep-08  Lixin Sun  Added the fifth input parameter to flag if the score
#                                            map is for generating mosaic for land pixels only.
#                                            (Biophysical parameter extraction needs land mosaic only)
######################################################################################################
def get_score_map(inMidDate, SsrData, image, MedBlue, MedNIR):
  '''Return a pixel score image corresponding to a given image
  
  Args:      
      inMidDate(ee.Date): The centre date of a time period for a mosaic generation.
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
      image(ee.Image): A given ee.Image object with cloud/shadow mask applied;
      WaterMap(ee.Image): A given water map.'''
  
  #==================================================================================================
  # Rescale the pixel values in the given image
  #==================================================================================================
  max_ref = 100
  scaled_img = Img.apply_gain_offset(image, SsrData, max_ref, False)  

  #==================================================================================================  
  # Get separate band images 
  #==================================================================================================
  blu  = scaled_img.select(SsrData['BLU'])
  #grn  = scaled_img.select(SsrData['GRN'])
  #red  = scaled_img.select(SsrData['RED'])
  nir  = scaled_img.select(SsrData['NIR'])
  #sw1  = scaled_img.select(SsrData['SW1'])
  #sw2  = scaled_img.select(SsrData['SW2'])

  #==================================================================================================
  # Calculate base score for both vagetated and non-vegetated targets
  #==================================================================================================
  #land_score = ee.Image(get_land_score(blu, grn, red, nir, sw1, sw2, MedBlue, MedNIR))
  spec_score = ee.Image(get_spec_score(blu, nir, MedBlue, MedNIR))
    
  #==================================================================================================
  # Apply could coverage score
  #==================================================================================================
  cloud_cover = ee.Number(image.get(SsrData['CLOUD'])).divide(100)  
  cover_score = ee.Image.constant(ee.Number(1).subtract(cloud_cover))   #.multiply(0.63)

  #==================================================================================================
  # Apply time scores exclusively to vegetation targets 
  #==================================================================================================
  ssr_code   = SsrData['SSR_CODE']
  time_score = ee.Image(get_time_score(image, inMidDate, ssr_code))   #.multiply(0.9)
  
  #score      = score.where(ndvi.gt(0.5), score.add(time_score))
  total_score = spec_score.add(cover_score).add(time_score)   #.divide(2.53)
 
  return ee.Image(total_score).rename([Img.pix_score]) 





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
  # Calculate scores for vagetated targets only and set scores for pixels with NDVI < 0.3 to zero
  #==================================================================================================  
  land_score  = get_land_score(blu, grn, red, nir, sw2) 

  zero_score = sw2.multiply(ee.Image(0.0)) #.add(cld_score.divide(ee.Image(200)))
  NDVI_img   = nir.subtract(red).divide(nir.add(red))

  return land_score.where(NDVI_img.lt(ee.Image(0.3)), zero_score)





######################################################################################################
# Description: This function attachs a smoothed score image to the given image
#
# Note:        The value range of "median_blue" is already in between 0 and 100
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def attach_Score(midDate, SsrData, Image, MedBlue, MedNIR):
  '''Attach a score image to a given image.
  
  Args:      
      midDate(ee.Date): The centre date of a time period for a mosaic generation.
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
      Image(ee.Image): A given ee.Image object to be attached a score image;
      WaterMap(ee.Image): A given water map.'''

  #==================================================================================================
  # Create a map that combines spectral and time scores
  #==================================================================================================
  score_map = get_score_map(midDate, SsrData, Image, MedBlue, MedNIR)

  # Define a boxcar or low-pass kernel.
  #boxcar = ee.Kernel.circle(radius = 2, units = 'pixels', normalize = True)

  # Smooth the image by convolving with the boxcar kernel.
  #smoothed_score = score_map.convolve(boxcar)

  return Image.addBands(score_map)
             




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
  masked_ImgColl = IS.mask_collection(collection, SsrData)
  #print('\n\n<score_collection> band names:', masked_ImgColl.first().bandNames().getInfo())
  
  median_mosaic = masked_ImgColl.median()
  median_mosaic = Img.apply_gain_offset(median_mosaic, SsrData, 100, False)  
  print('\n\n<score_collection> bands in median mosaic:', median_mosaic.bandNames().getInfo())

  med_blu = median_mosaic.select(SsrData['BLU'])  
  med_red = median_mosaic.select(SsrData['RED'])
  med_nir = median_mosaic.select(SsrData['NIR'])

  med_HOT = med_red.multiply(0.5).add(0.8)
  med_blu = med_blu.min(med_HOT)

  #==================================================================================================
  # Attach a spectral-time score and acquisition date bands to each image in the image collection
  #==================================================================================================
  #water_map = eoAD.get_GlobWater(1)
  #kernel    = ee.Kernel.circle(radius = 1)
  #water_map = water_map.focalMax(kernel = kernel, iterations = 2)

  scored_ImgColl = masked_ImgColl.map(lambda image: attach_Score(midDate, SsrData, image, med_blu, med_nir)) \
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
  #print('<score_collection> numb of images = ', scored_ImgColl.size().getInfo())
  #print('<score_collection> band names of 1st scored image = ', scored_ImgColl.first().bandNames().getInfo())
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
     ExtraBandCode(int): The integer code representing the band type to be added additionally.'''
  
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
# Note:        (1) The major difference between a mosaic image for LEAF tool and that for general-purpose 
#                  is the attachment of three imaging geometrical angle bands. 
#              (2) For Landsat and Sentinel-2 data, the Value range of returned mosaic will depend on which 
#                  algorithm will be apllied for extracting biophysical parameetrs. If SL2P is applied, 
#                  then the value range must be within [0, 1], if RF model is applied, then just keep 
#                  original value range.
#
# Revision history:  2021-May-19  Lixin Sun  Initial creation
#                    2022-Jan-14  Lixin Sun  Modified so that every value in "fun_Param_dict" dictionary
#                                            is a single value.  
#                    2023-Sep-07  Lixin Sun  Added the third input parameetr to indicate if SL2P algorithm 
#                                            will be applied.
#############################################################################################################
def LEAF_Mosaic(fun_param_dict, region, SL2P_algo):
  '''Creates a mosaic image specially for vegetation parameter extraction with LEAF tool.
     
     Args:
       fun_param_dict({}): a function parameter dictionary containing various single parameters;    
       region(ee.Geometry): the spatial region of a mosaic image;
       SL2P_algo(Boolean): a flag indicating if SL2P algorithm will be applied.'''
  
  #==========================================================================================================
  # Determine time period based on the given year and month
  #==========================================================================================================
  year  = int(fun_param_dict['year'])
  month = int(fun_param_dict['month'])
  start, stop = IS.month_range(year, month) if month > 0 and month < 13 else IS.summer_range(year)

  #==========================================================================================================
  # Create a mosaic image including imaging geometry angles that are  required by vegetation parameter 
  # extraction.
  # Note: the mosaic pixel value range required by SL2P algorithm must be within [0, 1]. If Random Forest
  # model is used for Landsat data, then original value range is OK.
  #==========================================================================================================
  ssr_data = Img.SSR_META_DICT[fun_param_dict['sensor']]
  ssr_code = ssr_data['SSR_CODE']

  mosaic = HomoPeriodMosaic(ssr_data, region, year, -1, start, stop, EXTRA_ANGLE)

  if (ssr_code < Img.MAX_LS_CODE and SL2P_algo == True) or ssr_code >= Img.MAX_LS_CODE:
    mosaic = Img.apply_gain_offset(mosaic, ssr_data, 1, False)
  
  return mosaic
    



######################################################################################################
# Description: This function merges two mosaics created from the images acquired with different
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
def MergeMosaics(MosaicBase, MosaicBkUp, SensorBase, SensorBkUp, ScroeThresh):
  '''Merge the mosaics created from the images acquired with different Landsat sensors.

  Args:
    MosaicBase(ee.Image): The mosaic that will be used as a base/main one;
    MosaicBkUp(ee.Image): The mosaic that will be used to fill the gaps in the base mosaic;
    SensorBase(Dictionary): The sensor info dictionary of the base/main mosaic;
    SensorBkUp(Dictionary): The sensor info dictionary of the 2nd mosaic to fill the gaps in base mosaic;\
    ScroeThresh(float): A given score threshold.'''  
  
  #===================================================================================================
  # Refresh the masks for both given mosaic images   
  #===================================================================================================
  mosaic_base = ee.Image(MosaicBase)
  mosaic_bkup = ee.Image(MosaicBkUp)
  
  #===================================================================================================
  # Fill the gaps in base mosaic with the valid pixels in the 2nd mosaic
  #===================================================================================================
  ssr_code_base = SensorBase['SSR_CODE']
  ssr_code_bkup = SensorBkUp['SSR_CODE']

  if (ssr_code_base > Img.MAX_LS_CODE and ssr_code_bkup < Img.MAX_LS_CODE) or \
     (ssr_code_base < Img.MAX_LS_CODE and ssr_code_bkup > Img.MAX_LS_CODE):  
    #In the case of the base and backup mosaics are acquired from Sentinel-2 and Landsat  
    bands_more = [Img.pix_score, Img.pix_date, Img.mosaic_ssr_code]
    bands_base = SensorBase['SIX_BANDS'] + bands_more
    bands_bkup = SensorBkUp['SIX_BANDS'] + bands_more
    bands_final = Img.STD_6_BANDS + bands_more
    #print('<MergeMosaics> Bands_base:', bands_base)  
    #print('<MergeMosaics> Bands_bkup:', bands_bkup)  
    #print('<MergeMosaics> Bands_final:', bands_final)  

    mosaic_base = mosaic_base.select(bands_base).rename(bands_final)  #.selfMask()
    mosaic_bkup = mosaic_bkup.select(bands_bkup).rename(bands_final)  #.selfMask()    
    #print('\n\n<MergeMosaics> Bands in base mosaic = ', mosaic_base.bandNames().getInfo())
    #rint('<MergeMosaics> Bands in 2nd mosaic = ', mosaic_bkup.bandNames().getInfo())

  #===================================================================================================
  # Fill the gaps in base mosaic with the pixels from backup mosaic 
  #===================================================================================================    
  mosaic_base = mosaic_base.unmask(mosaic_bkup)

  #===================================================================================================
  # Overwrite the pixels in base mosaic with the better pixels from backup mosaic 
  #===================================================================================================
  base_score = mosaic_base.select([Img.pix_score])
  bkup_score = mosaic_bkup.select([Img.pix_score]).subtract(float(ScroeThresh))

  return ee.Image(mosaic_base.where(bkup_score.gt(base_score), mosaic_bkup))




###################################################################################################
# Description: This function creates a mosaic image for a predefined region using the images 
#              acquired by nominal identical sensors, such as Landsat 8/9 and Sentinel-2 A/B, over
#              a time period.
#
# Revision history:  2021-Jun-02  Lixin Sun  Initial creation
#                    2021-Oct-05  Lixin Sun  Added an output option 
###################################################################################################
def HomoPeriodMosaic(SsrData, Region, TargetY, NbYs, StartD, StopD, ExtraBandCode):
  '''Creates a mosaic image for a region using the images acquired during a period of time. 
     
  Args:
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
      Region(ee.Geometry): The spatial polygon of a ROI;
      TargetY(int): A targeted year (must be an integer);
      NbYs(int): The number of years
      StartD(ee.Date or string): The start Date (e.g., '2020-06-01');
      StopD(ee.Date or string): The stop date (e.g., '2020-06-30');
      ExtraBandCode(int): A integr code representing band type be aatached additionally. '''  
  # Cast some input parameters 
  nb_years = int(NbYs)
  ssr_code = SsrData['SSR_CODE']
  start    = ee.Date(StartD).update(TargetY)
  stop     = ee.Date(StopD).update(TargetY)

  midDate  = IS.period_centre(start, stop)

  #==========================================================================================================
  # Get a mosaic image corresponding to a given time window in a targeted year
  #==========================================================================================================
  coll_target   = IS.getCollection(SsrData, Region, start, stop)
  mosaic_target = coll_mosaic(coll_target, SsrData, midDate, ExtraBandCode)
  ssr_code_img  = mosaic_target.select([0]).multiply(0).add(ssr_code).rename([Img.mosaic_ssr_code])

  if nb_years <= 1:
    return mosaic_target.addBands(ssr_code_img)

  elif nb_years == 2: 
    # Create a mosaic image for the year before the target
    PrevYear = TargetY - 1
    start    = start.update(PrevYear)
    stop     = stop.update(PrevYear)

    coll_before    = IS.getCollection(SsrData, Region, start, stop)
    midDate_before = IS.period_centre(start, stop)
    mosaic_before  = coll_mosaic(coll_before, SsrData, midDate_before, ExtraBandCode)

    # Merge the two mosaic images into one and return it  
    mosaic = MergeMosaics(mosaic_target, mosaic_before, SsrData, SsrData, 3.0)
    return mosaic.addBands(ssr_code_img)
  else: 
    # Create mosaic image for the year after the target
    AfterYear = TargetY + 1
    start     = start.update(AfterYear)
    stop      = stop.update(AfterYear)

    coll_after    = IS.getCollection(SsrData, Region, start, stop)
    midDate_after = IS.period_centre(start, stop)
    mosaic_after  = coll_mosaic(coll_after, SsrData, midDate_after, ExtraBandCode)

    mosaic = MergeMosaics(mosaic_target, mosaic_after, SsrData, SsrData, 3.0)

    # Create mosaic image for the year before the target
    PrevYear = TargetY - 1
    start    = start.update(PrevYear)
    stop     = stop.update(PrevYear)

    coll_before    = IS.getCollection(SsrData, Region, start, stop)
    midDate_before = IS.period_centre(start, stop)
    mosaic_before  = coll_mosaic(coll_before, SsrData, midDate_before, ExtraBandCode)
    
    mosaic = MergeMosaics(mosaic, mosaic_before, SsrData, SsrData, 3.0)
    return mosaic.addBands(ssr_code_img)




##########################################################################################################
# Description: This function creates an mosaic image for a region using the images acquired during one to 
#              three peak seasons (from June 15 to September 15).
#
# Revision history:  2021-Jul-07  Lixin Sun  Initial creation using JavaScript
#                    
##########################################################################################################
def HomoPeakMosaic(Ssrdata, Region, TargetY, NbYs, ExtraBandCode):
  '''Creates a mosaic image for a region using the images acquired during one, two or three
     peak-growing seasons (from June 15 to September 15). 
     
  Args:
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
      Region(ee.Geometry): A spatial region of a ROI;
      TargetYear(int): An integer representing a targeted year (e.g., 2020);
      NbYears(int): The number of peak seasons (1, 2 or 3);
      ExtraBandCode(int): A integer representing the band type to be attached to image.'''  

  # Get a peak season mosaic for targeted year
  start, stop = IS.summer_range(TargetY)
  
  return HomoPeriodMosaic(Ssrdata, Region, TargetY, int(NbYs), start, stop, ExtraBandCode)





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
  print('\n\n<LSMix_PeriodMosaic> sensor code1 and code2 for year = ', ssr_main_code, ssr_2nd_code, year)

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

  return MergeMosaics(mosaic_main, mosaic_2nd, ssr_main, ssr_2nd, 2.0)




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

  return MergeMosaics(mosaic_base, mosaic_2nd, SR_SSR_base, SR_SSR_2nd, 2.0)







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
  '''Attaches FOUR (VZA, VAA, SZA and SAA) geometry angle bands from a Landsat TOA reflectance 
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

  cos_scatter = cosScatteringAngle(angle_imgs).rename(['cosRAA'])

  # Calculate cos of the angle images and then attach them to the given surface reflectance image  
  angle_imgs = angle_imgs.cos().rename(['cosVZA','cosVAA','cosSZA','cosSAA'])

  return LS_sr_img.addBands(angle_imgs).addBands(cos_scatter)





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
def export_mosaic(fun_Param_dict, mosaic, SsrData, Region, task_list):
  '''Exports one set of LEAF products to either Google Drive or Google Cloud Storage

     Args:
       fun_Param_dict(dictionary): a dictionary storing other required running parameters;
       mosaic(ee.Image): the mosaic image to be exported;
       SsrData(Dictionary): A dictionary containing all info on a sensor type;
       Region(ee.Geometry): the spatial region of interest;
       task_list([]): a list storing the links to exporting tasks.'''
  #==========================================================================================================
  # Obtain some parameters from the given parameter dictionary
  #==========================================================================================================
  print('\n\n<export_mosaic> fun_Param_dict = ', fun_Param_dict)
  year_str     = str(fun_Param_dict['year'])   
  nb_years     = int(fun_Param_dict['nbYears'])
  tile_str     = str(fun_Param_dict['tile_name'])
  Scale        = int(fun_Param_dict['resolution'])
  given_folder = str(fun_Param_dict['folder'])
  out_location = str(fun_Param_dict['location']).lower()

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
  export_dict = {'scale': Scale,
                 'crs': 'EPSG:3979',
                 'maxPixels': 1e11,
                 'region': ee.Geometry(Region)}
  
  # Determine the bands to be exported according to specified spatial resolution 
  out_band_names = SsrData['OUT_BANDS'] if Scale >=20 else SsrData['10M_BANDS']

  if out_location.find('drive') > -1:  # Export to Google Drive
    print('<export_mosaic> Exporting to Google Drive......')  
    export_dict['folder'] = exportFolder
    for item in out_band_names:
      filename  = filePrefix + '_' + item + '_' + str(Scale) + 'm'

      export_dict['image']          = mosaic.select(item).multiply(ee.Image(100)).uint16()
      export_dict['description']    = filename
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
  




###################################################################################################
# Description: This function creates a mosaic image within a defined region by using all accessible
#              images acquired over a specified timeframe from the Landsat series and Sentinel-2 
#              A/B satellites.
#
# Revision history:  2023-Jun-06  Lixin Sun  Initial creation
#
###################################################################################################
def FullMix_PeriodMosaic(DataUnit, Region, targetY, NbYs, StartD, StopD, ExtraBandCode):
  '''Creates a mosaic image for a region using the images acquired during a period of time. 
     
  Args:
      DataUnit(Dictionary): Data unit code integer. 1 and 2 represent TOA and surface reflectance, respectively;
      Region(ee.Geometry): The spatial polygon of a ROI;
      targetY(int): A specified target year (must be a regular integer);
      NbYs(int): The number of years
      StartD(ee.Date or string): The start date string (e.g., '2020-06-01') or ee.Date object;
      StopD(ee.Date or string): The end date string (e.g., '2020-06-30') or ee.Date object;
      ExtraBandCode(int): A integer code representing band type to be attached additionaly.
  '''
  #================================================================================================
  # Determine a proper time period based on a given target year and an initial period 
  #================================================================================================
  year  = int(targetY)
  years = int(NbYs)
  unit  = int(DataUnit)
  start = ee.Date(StartD).update(year)
  stop  = ee.Date(StopD).update(year)

  #================================================================================================
  # Create a mosaic image using available Sentinel-2 images
  #================================================================================================
  print('\n\n<<<<<<<<<<<<<<<<<< start to generate mosaic with S2 images...........\n')
  S2_type_str = 'S2_SR' if unit > 1 else 'S2_TOA'
  S2_ssrData  = Img.SSR_META_DICT[S2_type_str]
  s2_mosaic   = HomoPeriodMosaic(S2_ssrData, Region, year, years, start, stop, ExtraBandCode, False)

  #================================================================================================
  # Create a mosaic image using available Landsat series images
  #================================================================================================
  print('\n<<<<<<<<<<<<<<<<<< start to generate mosaic with LS images...........\n')
  L8_type_str = 'L8_SR' if unit > 1 else 'L8_TOA'
  L8_ssrData  = Img.SSR_META_DICT[L8_type_str]  
  ls_mosaic   = HomoPeriodMosaic(L8_ssrData, Region, year, years, start, stop, ExtraBandCode, False)

  #================================================================================================
  # Apply gain and offset to convert data to the same unit and use Sentinel-2 data as base mosaic 
  #================================================================================================
  s2_mosaic = Img.apply_gain_offset(s2_mosaic, S2_ssrData, 100, False)
  ls_mosaic = Img.apply_gain_offset(ls_mosaic, L8_ssrData, 100, False)
    
  #return s2_mosaic, ls_mosaic
  #================================================================================================
  # Merge Sentinel-2 and Landat mosaic images into one with Sentinel-2 mosaic as basis 
  #================================================================================================
  mix_mosaic = MergeMosaics(s2_mosaic, ls_mosaic, S2_ssrData, L8_ssrData, 3.0)
  
  print('\n\n<<<<<<<<<<<< The final merge step in <FullMix_PeriodMosaic>')
  print('<FullMix_PeriodMosaic> bands in mixed mosaic:', mix_mosaic.bandNames().getInfo())
  print('<FullMix_PeriodMosaic> bands in S2 mosaic:', s2_mosaic.bandNames().getInfo())
  print('\n<FullMix_PeriodMosaic> bands in L8 mosaic:', ls_mosaic.bandNames().getInfo())

  return mix_mosaic, s2_mosaic, ls_mosaic





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
       Param_dict(Dictionary): A dictionary storing required parameters;
       MixSensor(Boolean): Indicate if to utilize mixed image data;
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
  ssr_data = Img.SSR_META_DICT[exe_Param_dict['sensor']]
  year     = int(exe_Param_dict['year'])
  nYears   = int(exe_Param_dict['nbYears'])    

  task_list = []  
  #==========================================================================================================
  # Loop through each tile
  #==========================================================================================================
  for tile_name in exe_Param_dict['tile_names']:
    fun_Param_dict['tile_name'] = tile_name

    # Create a mosaic region ee.Geometry object 
    if eoTG.is_valid_tile_name(tile_name) == True:
      region = eoTG.PolygonDict.get(tile_name)      
    else:
      region = eoTG.custom_RegionDict.get(tile_name)

    if nYears > 0:  # Create a peak-season mosaic for a specific region/tile and year      
      mosaic = HomoPeakMosaic(ssr_data, region, year, nYears, ExtraBandCode, False)
      mosaic = Img.apply_gain_offset(mosaic, ssr_data, 100, False)

      # Export spectral mosaic images  
      export_mosaic(fun_Param_dict, mosaic, ssr_data, region, task_list)
    else:  # Create a monthly mosaic for a specific region/tile and year
      for month in exe_Param_dict['months']:
        fun_Param_dict['month'] = month
        start, stop = IS.month_range(year, month)
        mosaic = HomoPeriodMosaic(ssr_data, region, year, nYears, start, stop, ExtraBandCode)
        mosaic = Img.apply_gain_offset(mosaic, ssr_data, 100, False)

        # Export spectral mosaic images
        export_mosaic(fun_Param_dict, mosaic, ssr_data, region, task_list)   
      
  return task_list





#############################################################################################################
# Description: The start/main function for operationally producing tile mosaic images using mixted satellite
#              images from Landsat and Sentinel-2
#
# Revision history:  2023-Oct-16  Lixin Sun  Initial creation 
#
#############################################################################################################
def MixMosaic_production(exe_Param_dict, ExtraBandCode):
  '''Produces various mosaic products for one or more tiles using Landsat or Sentinel2 images
     Args:
       Param_dict(Dictionary): A dictionary storing required parameters;
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
  ssr_data = Img.SSR_META_DICT[exe_Param_dict['sensor']]
  year     = int(exe_Param_dict['year'])
  nYears   = int(exe_Param_dict['nbYears'])    

  task_list = []  
  #==========================================================================================================
  # Loop through each tile
  #==========================================================================================================
  for tile_name in exe_Param_dict['tile_names']:
    fun_Param_dict['tile_name'] = tile_name

    # Create a mosaic region ee.Geometry object 
    if eoTG.is_valid_tile_name(tile_name) == True:
      region = eoTG.PolygonDict.get(tile_name)      
    else:
      region = eoTG.custom_RegionDict.get(tile_name)
    
    for month in exe_Param_dict['months']:
      fun_Param_dict['month'] = month
      start, stop = IS.month_range(year, month)
      mosaic = FullMix_PeriodMosaic(2, region, year, nYears, StartD, StopD, ExtraBandCode)
      export_mosaic(fun_Param_dict, mosaic, ssr_data, region, task_list)
      
  return task_list