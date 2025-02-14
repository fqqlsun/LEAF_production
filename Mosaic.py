######################################################################################################
# Description: The code in this file was initially created with JavaScript and then was converted to
#              to Python in April 2021. Modifications were also made after the code conversion.
#
######################################################################################################
import ee 
ee.Initialize()


import math

import Image as Img
import ImgMask as IM
import ImgSet as IS
import eoTileGrids as eoTG
import eoAuxData as eoAD
import eoParams as eoPM


#veg_NDVI_thresh = 0.4



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
        ssr_code (int): The sensor type code;
        TWinSize(int): The size of a composite time window. '''
  #==================================================================================================
  # Calculate the date difference betwen the given image and a reference date
  # Note that 86400000 is milliseconds per day
  #==================================================================================================
  millis_per_day = 86400000
  img_date  = ee.Date(image.date())  # Get the Unix date of the given image   
  img_year  = img_date.get('year')   # Get the year integer of the given image
  DOY_1st   = ee.Date.fromYMD(img_year, 1, 1).millis().divide(millis_per_day)  # the unix date of the 1st DOY 
  mid_date  = ee.Date(midDate).update(img_year)  # Corrected midDate
  
  img_DOY   = img_date.millis().divide(millis_per_day).subtract(DOY_1st)
  refer_DOY = mid_date.millis().divide(millis_per_day).subtract(DOY_1st)
  DOY_diff  = img_DOY.subtract(refer_DOY)

  #==================================================================================================
  # Calculatr time score according to sensor type 
  #==================================================================================================
  ssr_code = int(ssr_code)  

  STD = 12 if ssr_code > Img.MAX_LS_CODE else 16
  
  one_img = ee.Image.constant(1)
  factor  = ee.Image(DOY_diff).divide(ee.Image.constant(STD))

  return one_img.divide((ee.Image.constant(0.5).multiply(factor).multiply(factor)).exp())





#############################################################################################################
# Description: This function returns a reference mosaic image that will be used in HybridTIC
#
# Revision history:  2023-Nov-24  Lixin Sun  Initial creation
#
#############################################################################################################
def period_refer_mosaic(maskedImgColl, SsrData):
  '''Args:
     maskedImgColl(ee.ImageCollection): A given image collection with mask applied to each image;
     SsrData(dictionary): A given dictionary containing some meta data about a sensor.'''
  
  # NIR_ImgColl = maskedImgColl.map(lambda img: img.select(SsrData['NIR']))
  # min_NIR = NIR_ImgColl.min()

  #==========================================================================================================
  # Convert the value range to between 0 and 100 and then create a median mosaic image
  #==========================================================================================================
  ready_ImgColl = maskedImgColl.map(lambda img: Img.apply_gain_offset(img, SsrData, 100, False))  
  refer_median  = ready_ImgColl.median()

  #==========================================================================================================
  # Extract required separate bands and calculate NDVI and modeled blue band image
  #==========================================================================================================
  refer_blu = refer_median.select(SsrData['BLU'])
  refer_red = refer_median.select(SsrData['RED'])
  refer_nir = refer_median.select(SsrData['NIR'])
  #refer_sw1 = refer_median.select(SsrData['SW2'])
  refer_sw2 = refer_median.select(SsrData['SW2'])
  #refer_sw  = refer_sw1.max(refer_sw2) 

  #==========================================================================================================
  # Correct the blue band values of median mosaic for the pixels with NDVI values larger than 0.3
  #========================================================================================================== 
  NDVI     = refer_nir.subtract(refer_red).divide(refer_nir.add(refer_red))

  #veg_cond = NDVI.gt(0.3).Or(refer_sw2.lt(refer_blu).And(refer_sw.gt(3.0)))
  #veg_cond = NDVI.gt(0.3)
  veg_blu  = refer_blu.where(NDVI.gt(0.3), refer_sw2.multiply(0.25))  
  
  return refer_median.addBands(srcImg=veg_blu, overwrite = True)
  #==========================================================================================================
  # Correct water reference in the blue band
  #========================================================================================================== 
  #water_cond = (refer_blu.gt(refer_sw).And(refer_sw.lt(3.0)))   #.Or(refer_sw.lt(3.0))
  #final_blu  = corrected_blu.where(water_cond, ee.Image.constant(2.0))
  #final_nir  = refer_nir.where(water_cond, ee.Image.constant(1.0))

  #refer_median = refer_median.addBands(srcImg=final_blu, overwrite = True)
  #return refer_median.addBands(srcImg=final_nir, overwrite = True)




#############################################################################################################
# Description: This function returns a reference mosaic image that will be used in HybridTIC
#
# Revision history:  2023-Nov-24  Lixin Sun  Initial creation
#
#############################################################################################################
def get_refer_mosaic(masked_ImgColl, SsrData, Start, Stop):
  '''Args:
     masked_ImgColl(ee.ImageCollection): A given image collection with maske appliedto each image;
     SsrData(dictionary): A given dictionary containing some meta data about a sensor;
     Start(string): A string represents the starting date of a compositing period;
     Stop(string): A string represents the ending date of a compositing period.'''

  #==========================================================================================================
  # Generate a reference mosaic for entire period specified
  #==========================================================================================================  
  whole_period_refer = period_refer_mosaic(masked_ImgColl, SsrData)
  
  WinSize = IS.time_window_size(Start, Stop).getInfo()  

  if WinSize < 1000:
    return ee.Image(whole_period_refer)
  
  else:  
    #--------------------------------------------------------------------------------------------------------
    # When a compositing period is longer than one month, the 'refer_mosaic' created above is for whole
    # compositing period. So a monthly referance mosaic needs to be created. 
    #--------------------------------------------------------------------------------------------------------
    midDate = IS.period_centre(Start, Stop)              # Determine the central date of a time window 
    month_start, month_stop = IS.time_range(midDate, 31) # Determine the start and stop dates of a month
  
    month_ImgColl = masked_ImgColl.filterDate(month_start, month_stop) # get a subset of image collection

    #--------------------------------------------------------------------------------------------------------
    # Correct the blue band values of monthly mosaic for the pixels with NDVI values larger than 0.3
    #--------------------------------------------------------------------------------------------------------
    month_refer = period_refer_mosaic(month_ImgColl, SsrData)
    month_refer = month_refer.unmask(whole_period_refer)

    blu = month_refer.select(SsrData['BLU'])
    red = month_refer.select(SsrData['RED'])
    nir = month_refer.select(SsrData['NIR'])
    sw2 = month_refer.select(SsrData['SW2'])

    NDVI      = nir.subtract(red).divide(nir.add(red))
    model_blu = sw2.multiply(0.3)  

    replace_cond  = model_blu.lt(blu).And(NDVI.gt(0.3))
    corrected_blu = blu.where(replace_cond, model_blu)
    
    #--------------------------------------------------------------------------------------------------------
    # Replace the blue reference band with corrected one 'corrected_blu'
    #--------------------------------------------------------------------------------------------------------
    return ee.Image(month_refer.addBands(srcImg=corrected_blu, overwrite = True))





######################################################################################################
# Description: This function returns a HOT score map
#
# Revision history:  2023-Oct-22  Lixin Sun  Initial creation
#
######################################################################################################
def get_HOT_score(blu, red):
  HOT     = blu.subtract(red.multiply(0.5).add(0.8))
  one_img = ee.Image.constant(1)

  return one_img.divide(one_img.add((HOT.add(0.075).multiply(50)).exp()))




######################################################################################################
# Description: This function returns a HOT score map
#
# Revision history:  2023-Oct-22  Lixin Sun  Initial creation
#
######################################################################################################
def get_CCover_score(Img, SsrData):
  coverage = ee.Number(Img.get(SsrData['CLOUD'])).divide(100)  

  return ee.Image.constant(ee.Number(1).subtract(coverage))





######################################################################################################
# Description: This function attaches a NIR-to-blue ratio score map to a given single image 
#
# Revision history:  2021-Jun-10  Lixin Sun  Initial creation
#
######################################################################################################
def get_maxNBR_score(blu, red, nir, sw1, sw2):
  model_blu = (sw2.multiply(0.25)).max(red.multiply(0.5).add(0.8)).max(blu)  

  return ee.Image(nir.divide(model_blu))






######################################################################################################
# Description: This function creates a score image for a given ee.Image object.
#   
# Note:        The value ranges of all the input spectral bands must be within [0, 100]  
#              (1) Using NLCD distance as penalty does not work well
#
# Revision history:  2023-Aug-25  Lixin Sun  Initial creation
#
######################################################################################################
def get_spec_score(blu, grn, red, nir, sw1, sw2, refer_blu, refer_nir, water_map):
    
  #==================================================================================================
  # Calculate scores assuming all the pixels are water
  #==================================================================================================  
  max_SV   = blu.max(grn).max(0.01)
  max_SW   = sw1.max(sw2).max(0.01)
  max_IR   = max_SW.max(nir).max(0.01)  
  used_blu = blu.max(0.01)
  zero_img = max_SV.multiply(0)

  water_score = zero_img
  water_score = water_score.where(max_SW.lt(3.0), ee.Image(refer_blu.divide(used_blu)))  

  #==================================================================================================
  # Calculate scores assuming all the pixels are land
  #==================================================================================================
  blu_pen = refer_blu.subtract(blu).abs().exp()
  nir_pen = refer_nir.subtract(nir)  
  nir_pen = nir_pen.where(nir.gt(refer_nir).Or(blu.gt(refer_blu)), ee.Image.constant(0.0)).abs()  
  
  land_score = ee.Image(nir.divide(used_blu.add(blu_pen).add(nir_pen)))
  land_score = land_score.where(blu.gt(nir).Or(max_SW.lt(3.0)), ee.Image.constant(0)) 

  #return land_score
  #==================================================================================================
  # Normalize land and water scores
  #==================================================================================================  
  land_score  = land_score.divide(land_score.add(1))
  water_score = water_score.divide(water_score.add(1))

  # max_score  = refer_nir.divide(refer_blu.add(ee.Image.constant(1.0)))  
  # land_k     = ee.Image.constant(-5.0).divide(max_score)
  #land_score = ee.Image.constant(1.0).subtract((land_score.multiply(land_k)).exp())

  # water_score = ee.Image.constant(1.0).subtract((water_score.multiply(ee.Image.constant(-0.5))).exp())

  #==================================================================================================
  # Create a water mask for replacing land scores with water scores
  #==================================================================================================  
  #water_mask  = water_map.eq(2).Or(water_map.eq(0).And(max_SV.gt(max_IR)).And(max_SW.lt(3.0)))
  water_mask  = water_map.eq(2).Or(water_map.eq(0).And(max_SV.gt(max_IR))).Or(max_SW.lt(3.0)).Or(refer_nir.lt(3.0))
  
  final_score = land_score.where(water_mask, water_score)  
  final_score = final_score.where(blu.gt(refer_blu.multiply(2.0)), blu.multiply(-1.0))

  min_spec = blu.min(grn).min(red).min(nir).min(sw1).min(sw2)
  return final_score.where(min_spec.lt(0.011), ee.Image.constant(-10))
  





######################################################################################################
# Description: This function attaches a MaxNBR score map to a given image
#
# Revision history:  2023-Dec-08  Lixin Sun  Initial creation
#                                 
######################################################################################################
def attach_MaxNBR_score(maskedImg, SsrData):
  '''This function attaches a MaxNBR score map to a given image
  
  Args:      
      maskedImg(ee.Image): A given ee.Image object with cloud/shadow mask applied;
      SsrData(Dictionary): A sensor info dictionary.'''  
  #==================================================================================================
  # Rescale the given image to value range between 0 and 100
  #==================================================================================================
  max_ref = 100
  readyImg = Img.apply_gain_offset(maskedImg, SsrData, max_ref, False)

  #==================================================================================================  
  # Get separate band images 
  #==================================================================================================
  blu = readyImg.select(SsrData['BLU'])
  red = readyImg.select(SsrData['RED'])
  nir = readyImg.select(SsrData['NIR'])
  sw1 = readyImg.select(SsrData['SW1'])
  sw2 = readyImg.select(SsrData['SW2'])

  #==================================================================================================
  # Calculate maxNBR map
  #==================================================================================================  
  score = ee.Image(get_maxNBR_score(blu, red, nir, sw1, sw2))
  
  return maskedImg.addBands(score.rename([Img.pix_score]))




######################################################################################################
# Description: This function attaches a MaxNDVI score map to a given image
#
# Revision history:  2023-Dec-08  Lixin Sun  Initial creation
#                                 
######################################################################################################
def attach_MaxNDVI_score(maskedImg, SsrData):
  '''This function attaches a MaxNDVI score map to a given image
  
  Args:      
      maskedImg(ee.Image): A given ee.Image object with cloud/shadow mask applied;
      SsrData(Dictionary): A sensor info dictionary.'''  
  #==================================================================================================
  # Rescale the given image to value range between 0 and 100
  #==================================================================================================
  max_ref = 100
  readyImg = Img.apply_gain_offset(maskedImg, SsrData, max_ref, False)

  #==================================================================================================  
  # Get separate band images 
  #==================================================================================================
  red = readyImg.select(SsrData['RED'])
  nir = readyImg.select(SsrData['NIR'])

  #==================================================================================================
  # Calculate maxNDVI score map
  #==================================================================================================  
  score = ee.Image(nir.subtract(red).divide(nir.add(red)))
  
  return maskedImg.addBands(score.rename([Img.pix_score]))





######################################################################################################
# Description: This function attaches a score map that is calculated based on NLCD algorithm
#
# Revision history:  2023-Jun-10  Lixin Sun  Initial creation
#
######################################################################################################
def attach_NLCD_score(maskedImg, SsrData, ready_median_mosaic, MidDate):  
  '''This function attaches a score map that is calculated based on NLCD algorithm
  Args:
      maskedImg(ee.Image): A given single image scene;
      SsrData(Dictionary): A sensor info dictionary;
      ready_median_mosaic(ee.Image): A median-based mosaic image with values rescaled. '''
  
  #==================================================================================================
  # Rescale the given single image and then calculate distance between image and median
  #==================================================================================================
  max_ref = 100
  readyImg = Img.apply_gain_offset(maskedImg, SsrData, max_ref, False).select(SsrData['OUT_BANDS'])  

  #==================================================================================================
  # Calculate the difference between the pixels in the single image and their corresponding median 
  #==================================================================================================  
  diffImg = ((readyImg.subtract(ready_median_mosaic)).pow(2).reduce(ee.Reducer.sum())).sqrt()
  
  spec_score = ee.Image.constant(1).divide(diffImg.add(0.001))
  #spec_score = ee.Image.constant(1).divide((diffImg.multiply(ee.Image.constant(0.25))).exp())

  #==================================================================================================
  # Calculate could coverage score
  #==================================================================================================
  #cover_score = get_CCover_score(maskedImg, SsrData)   #.multiply(10.0)

  #asset_size  = ee.Number(maskedImg.get('system:asset_size')).divide(1800000000) 
  #cover_score = cover_score.where(cover_score.lt(0.7), ee.Image.constant(0)).multiply(asset_size)  

  #==================================================================================================
  # Calculate time score
  #==================================================================================================
  #ssr_code   = SsrData['SSR_CODE']
  #time_score = ee.Image(get_time_score(maskedImg, MidDate, ssr_code))    #.multiply(10.0)
  
  final_score = spec_score   #.add(cover_score).add(time_score)

  return maskedImg.addBands(final_score.rename([Img.pix_score]))





def attach_CSP_score(maskedImg, SsrData, MidDate):  
  '''This function attaches a score map that is calculated based on NLCD algorithm
  Args:
      maskedImg(ee.Image): A given single image scene;
      SsrData(Dictionary): A sensor info dictionary;
      ready_median_mosaic(ee.Image): A median-based mosaic image with values rescaled. '''
  
  #==================================================================================================
  # Calculate the difference between the pixels in the single image and their corresponding median 
  #==================================================================================================  
  spec_score = maskedImg.select(Img.cloud_score)
  #spec_score = ee.Image.constant(1).divide((diffImg.multiply(ee.Image.constant(0.25))).exp())

  #==================================================================================================
  # Calculate could coverage score
  #==================================================================================================
  cover_score = get_CCover_score(maskedImg, SsrData)   #.multiply(10.0)

  #==================================================================================================
  # Calculate time score
  #==================================================================================================
  ssr_code   = SsrData['SSR_CODE']
  time_score = ee.Image(get_time_score(maskedImg, MidDate, ssr_code))    #.multiply(10.0)
  
  final_score = spec_score.add(cover_score).add(time_score)

  return maskedImg.addBands(final_score.rename([Img.pix_score]))




######################################################################################################
# Description: This function attaches a score map to a given image
#
# Note:        (1) This function assumes the value range of the given image is between 0 and 100
#              (2) The value range of "median_blue" is already in between 0 and 100
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def attach_Hybrid_score(maskedImg, midDate, SsrData, ready_refer_mosaic, water_map):
  '''Attach a score image to a given image.
  
  Args:      
      maskedImg(ee.Image): A given ee.Image object with mask applied;
      midDate(ee.Date): The centre date of a compositing time period;
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;      
      ready_refer_mosaic(ee.Image): A given reference image that has been rescaled and masked;
      water_map(ee.Image): A given permanent water and permanent land map.'''
  
  #==================================================================================================
  # Rescale the pixel values to range between 0 and 100
  #==================================================================================================
  max_ref = 100
  readyImg = Img.apply_gain_offset(maskedImg, SsrData, max_ref, False)

  #==================================================================================================
  # Select blue and NIR bands from the given reference mosaic with rescaled SR values
  #==================================================================================================
  refer_blu = ready_refer_mosaic.select(SsrData['BLU'])
  refer_nir = ready_refer_mosaic.select(SsrData['NIR'])
  #dist_img = scaled_img.subtract(refer_mosaic).pow(2).reduce(ee.Reducer.sum()).sqrt()

  #==================================================================================================
  # Calculate spectral score for all targets, including vegetated, non-vegetated and water
  #==================================================================================================
  blu = readyImg.select(SsrData['BLU'])
  grn = readyImg.select(SsrData['GRN'])
  red = readyImg.select(SsrData['RED'])  
  nir = readyImg.select(SsrData['NIR'])  
  sw1 = readyImg.select(SsrData['SW1'])
  sw2 = readyImg.select(SsrData['SW2'])

  #land_score = ee.Image(get_land_score(blu, grn, red, nir, sw1, sw2, MedBlue, MedNIR))
  spec_score = ee.Image(get_spec_score(blu, grn, red, nir, sw1, sw2, refer_blu, refer_nir, water_map))  
      
  #return maskedImg.addBands(spec_score.rename([Img.pix_score]))   

  #==================================================================================================
  # Calculate could coverage score
  #==================================================================================================
  cover_score = get_CCover_score(maskedImg, SsrData)   #.multiply(10.0)

  #==================================================================================================
  # Calculate time score
  #==================================================================================================
  ssr_code   = SsrData['SSR_CODE']
  time_score = ee.Image(get_time_score(maskedImg, midDate, ssr_code))    #.multiply(10.0)
  
  #==================================================================================================
  # Calculate total score
  #==================================================================================================
  #total_score = spec_score.multiply(cover_score).multiply(time_score)
  total_score = spec_score.add(cover_score).add(time_score)

  return maskedImg.addBands(total_score.rename([Img.pix_score]))
             




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
def score_collection(masked_img_coll, SsrData, midDate, ExtraBandCode, CS_plus, rescaled_refer_mosaic):
  '''Attaches a score, acquisition date and some specified bands to each image of a collection.
  
  Args:
     masked_img_coll(ee.ImageCollection): A given image collection with mask applied to each image;
     SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
     midDate(ee.Date): The centre date of a comositing time period;
     ExtraBandCode(int): The integer code representing band type to be added additionally;
     CS_plus(Boolean): A flag indicating if to apply CloudScore+ mask;
     rescaled_refer_mosaic(ee.Image): A given rescaled reference image.'''
  #print('<score_collection> band names of 1st image = ', collection.first().bandNames().getInfo())
  #print('<score_collection> the given collection = ', collection.size().getInfo())  
  #==================================================================================================
  # Obtain a global permanent water and land map
  # 0,1 and 2 in the map represent temporary water, permanent land and permanent water, respectively
  #==================================================================================================
  water_map = eoAD.get_water_land_map(90).unmask()
  
  #==================================================================================================
  # Attach a score and an acquisition date bands to each image in the image collection
  #==================================================================================================  
  scored_ImgColl = masked_img_coll.map(lambda img: attach_Hybrid_score(img, midDate, SsrData, rescaled_refer_mosaic, water_map)) \
                                  .map(lambda img: Img.attach_Date(img))  
  
  #==================================================================================================
  # Attach an additional bands as necessary to each image in the image collection
  #==================================================================================================  
  extra_code = int(ExtraBandCode)
  if extra_code == Img.EXTRA_ANGLE:
    scored_ImgColl = scored_ImgColl.map(lambda image: Img.attach_AngleBands(image, SsrData))
  elif extra_code == Img.EXTRA_NDVI:
    scored_ImgColl = scored_ImgColl.map(lambda image: Img.attach_NDVIBand(image, SsrData))

  # Return scored image collection  
  #print('<score_collection> numb of images = ', scored_ImgColl.size().getInfo())
  #print('<score_collection> band names of 1st scored image = ', scored_ImgColl.first().bandNames().getInfo())
  return scored_ImgColl




  
######################################################################################################
# Description: This function creates a mosaic image from a given image collection based on MaxNBR. 
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def coll_MaxNBR_mosaic(maskedImgColl, SsrData):
  '''Create a mosaic image from a given image collection based on MaxNBR.
  
  Args:     
    inMaskedImgColl(ee.ImageCollection): A given image collection with cloud/shadow masks applied; 
    SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit.
  '''    
  #==================================================================================================
  # Create a scored image collection (attach a score image for each image in the given collection)
  #==================================================================================================
  scored_ImgColl = maskedImgColl.map(lambda img: attach_MaxNBR_score(img, SsrData))
  
  #==================================================================================================
  # Create and return a mosaic based on associated score maps
  #==================================================================================================  
  return scored_ImgColl.qualityMosaic(Img.pix_score) #.set('system:time_start', midDate.millis())





######################################################################################################
# Description: This function creates a mosaic image from a given image collection based on MaxNDVI. 
#
# Note:        This MaxNDVI-based TIC method cannot be used as an independent method since it uses
#              rescaled values for all spectral bands.
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def coll_MaxNDVI_mosaic(maskedImgColl, SsrData):
  '''Create a mosaic image from a given image collection based on MaxNDVI.
  
  Args:     
    maskedImgColl(ee.ImageCollection): A given image collection with cloud/shadow masks applied; 
    SsrData(Dictionary): A sensor info dictionary. '''
    
  #==================================================================================================
  # Create a scored image collection (attach a score image for each image in the given collection)
  #==================================================================================================
  scored_ImgColl = maskedImgColl.map(lambda img: attach_MaxNDVI_score(img, SsrData))
  
  #==================================================================================================
  # Create and return a mosaic based on associated score maps
  #==================================================================================================  
  return scored_ImgColl.qualityMosaic(Img.pix_score) #.set('system:time_start', midDate.millis())





######################################################################################################
# Description: This function creates a mosaic image from a given image collection based on CloudScore+ 
#
# Revision history:  2024-Dec-25  Lixin Sun  Initial creation
#
######################################################################################################
def coll_CS_mosaic(maskedImgColl, SsrData, MidTime):
  '''Create a mosaic image from a given image collection based on CloudScore_plus.
  
  Args:     
    maskedImgColl(ee.ImageCollection): A given image collection with cloud/shadow masks applied. '''
   
  #==================================================================================================
  # Create a scored image collection (attach a score image for each image in the given collection)
  #==================================================================================================
  scored_ImgColl = maskedImgColl.map(lambda img: attach_CSP_score(img, SsrData, MidTime))    #attach CloudScore+

  #==================================================================================================
  # Create and return a mosaic based on associated score maps
  #==================================================================================================  
  return scored_ImgColl.qualityMosaic(Img.pix_score) #.set('system:time_start', midDate.millis())

  





######################################################################################################
# Description: This function creates a mosaic image based on a given image collection. 
#
# Revision history:  2020-Dec-22  Lixin Sun  Initial creation
#
######################################################################################################
def coll_Hybrid_mosaic(inImgColl, SsrData, StartD, StopD, ExtraBandCode, CS_plus):
  '''Create a mosaic image based on a given image collection.
  
  Args:   
    inImgColl(ee.ImageCollection): A given image collection;  
    SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;    
    StartD(ee.Date): The beginning date of a compositing time period;
    StopD(ee.Date): The ending date of a compositing time period;
    ExtraBandCode(int): The integer code representing the band type to be added additionally;
    CS_plus(Boolean): A flag indicating if to apply CloudScore+ mask to image collection.'''

  #==================================================================================================
  # Create a historical median mosaic image
  #==================================================================================================    
  '''
  med_start, med_stop = IS.time_range(midDate, 31)  # Determine the start and stop dates of a month
  
  if ssr_code < Img.MAX_LS_CODE:
    hist_median = median_refer_LS_SR(SsrData['GEE_NAME'], Region, med_start, med_stop, 2019, 2023)
  elif ssr_code >= Img.MAX_LS_CODE and ssr_code < Img.MOD_sensor:
    hist_median = median_refer_S2_SR(SsrData['GEE_NAME'], Region, med_start, med_stop, 2019, 2023)
  else:
    hist_median = median_refer_HLS_SR(SsrData['GEE_NAME'], Region, med_start, med_stop, 2019, 2023)
  #print('<coll_mosaic> Bands in historical median image:', hist_median.bandNames().getInfo())
  
  hist_median = hist_median.select([SsrData['BLU'], SsrData['GRN'], SsrData['RED'], SsrData['NIR'],SsrData['SW1'], SsrData['SW2']]) \
                           .rename(['blue', 'green', 'red', 'nir', 'swir1', 'swir2'])
  
  median_SR_refer = get_refer_mosaic(masked_ImgColl, SsrData, Start, Stop)
  median = median_SR_refer.unmask(hist_median)
  median = Img.apply_gain_offset(median, SsrData, 100, False)
  '''
  #==================================================================================================
  # Apply default (OR CloudScore) masks to each image in the given collection
  #==================================================================================================  
  #masked_ImgColl = inImgColl
  masked_ImgColl = IS.mask_collection(inImgColl, SsrData, CS_plus) 
  #print('<coll_mosaic> Bands in the first masked image:', masked_ImgColl.first().bandNames().getInfo())

  #==================================================================================================
  # Create a reference mosaic image
  #==================================================================================================  
  refer_mosaic = get_refer_mosaic(masked_ImgColl, SsrData, StartD, StopD)
  #print('<coll_mosaic> Bands in refer median image:', refer_mosaic.bandNames().getInfo()) 

  #==================================================================================================
  # Create a scored image collection (attach a score image for each image in the given collection)
  #==================================================================================================
  midDate           = IS.period_centre(StartD, StopD)        # Determine the central date of a time window 
  scored_collection = score_collection(masked_ImgColl, SsrData, midDate, ExtraBandCode, CS_plus, refer_mosaic)

  #==================================================================================================
  # Create and return a mosaic based on associated score maps
  #==================================================================================================  
  return scored_collection.qualityMosaic(Img.pix_score) #.set('system:time_start', midDate.millis())





#############################################################################################################
# Description: This function creates a median reference mosaic using historical Landsat-8 images acquired
#              within specified time window and spatial region.
# 
# Revision history:  2023-Dec-02  Lixin Sun  initial creation
#  
#############################################################################################################
def median_refer_HLS_SR(CollName, inRegion, StartData, StopData, StartYear, StopYear):
  def one_year_median(inYear):
    start = ee.Date(StartData).update(inYear)
    stop  = ee.Date(StopData).update(inYear)    
    
    img_coll = ee.ImageCollection(CollName).filterBounds(inRegion).filterDate(start, stop)

    masked_coll = img_coll.map(lambda img: img.updateMask(IM.HLS_ClearMask(img).Not()))
    return masked_coll.median()
  
  median_coll = ee.List.sequence(StartYear, StopYear).map(lambda x: one_year_median(x))
  
  median = ee.ImageCollection(median_coll).median()
  #print(median.bandNames().getInfo())

  return median





#############################################################################################################
# Description: Creates a mosaic image specially for vegetation parameter extraction with LEAF tool.
#
# Note:        (1) The major difference between a mosaic image for LEAF tool and that for general purpose 
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
def LEAF_Mosaic(inSsrData, region, inStart, inStop, SL2P_algo):
  '''Creates a mosaic image specially for vegetation parameter extraction with LEAF tool.
     
     Args:
       inSsrData(Dictionary): a dictionary containing various info about a sensor;
       region(ee.Geometry): the spatial region of a mosaic image;
       inStart(string or ee.Date): The start date of a time period;
       inStop(string or ee.Date): The stop date of a time period;
       SL2P_algo(Boolean): a flag indicating if SL2P algorithm will be applied.'''
  
  #==========================================================================================================
  # Create a mosaic image including imaging geometry angles required by vegetation parameter extraction.
  # Note: (1) the mosaic pixel value range required by SL2P algorithm must be within [0, 1]. If Random Forest
  #           model is used for Landsat data, then original value range is OK.
  #       (2) Generating pixel masks using CloudScore could sometimes cause problem. So the last parameter
  #           for "HomoPeriodMosaic" function should be "False" for now (Feb. 10, 2024) 
  #==========================================================================================================
  ssr_code = inSsrData['SSR_CODE']  
  year     = ee.Date(inStart).get('year').getInfo()

  mosaic = HomoPeriodMosaic(inSsrData, region, year, -1, inStart, inStop, Img.EXTRA_ANGLE, False)

  if (ssr_code < Img.MAX_LS_CODE and SL2P_algo == True) or (ssr_code >= Img.MAX_LS_CODE and ssr_code < Img.MOD_sensor):
    # The value range for applying SL2P algorithm must be within 0 and 1 
    mosaic = Img.apply_gain_offset(mosaic, inSsrData, 1, False)
  
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
def HomoPeriodMosaic(SsrData, Region, TargetY, NbYs, StartD, StopD, ExtraBandCode, CS_plus):
  '''Creates a mosaic image for a region using the images acquired during a period of time. 
     
  Args:
      SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
      Region(ee.Geometry): The spatial polygon of a ROI;
      TargetY(int): A targeted year (must be an integer);
      NbYs(int): The number of years
      StartD(ee.Date or string): The start Date (e.g., '2020-06-01');
      StopD(ee.Date or string): The stop date (e.g., '2020-06-30');
      ExtraBandCode(int): A integr code representing band type be attached additionally;
      CS_plus(Boolean): A flag indicating if to apply CloudScore+ mask.'''  
  # Cast some input parameters 
  nb_years = int(NbYs)
  ssr_code = SsrData['SSR_CODE'] 

  #==========================================================================================================
  # Get a mosaic image corresponding to a given time window in a targeted year
  #==========================================================================================================  
  start = ee.Date(StartD).update(TargetY)
  stop  = ee.Date(StopD).update(TargetY)
  
  # Generate an image collection and then apply masks to each image in the collection 
  ImgColl_target = IS.getCollection(SsrData, Region, start, stop, ExtraBandCode)
  #masked_ImgColl_target = IS.mask_collection(ImgColl_target, SsrData, CS_plus)

  mosaic_target  = coll_Hybrid_mosaic(ImgColl_target, SsrData, start, stop, ExtraBandCode, CS_plus)  
  
  #print('bands in mosaic = ', mosaic_target.bandNames().getInfo())
  if nb_years <= 1:
    ssr_code_img  = mosaic_target.select([0]).multiply(0).add(ssr_code).rename([Img.mosaic_ssr_code])
    return mosaic_target.addBands(ssr_code_img)

  elif nb_years == 2: 
    # Create a mosaic image for the year before the target
    PrevYear = TargetY - 1
    start    = start.update(PrevYear)
    stop     = stop.update(PrevYear)
    
    # Prepare an image collection and then apply masks to each image in the collection 
    ImgColl_before = IS.getCollection(SsrData, Region, start, stop, ExtraBandCode)
    #masked_ImgColl_before = IS.mask_collection(ImgColl_before, SsrData, CS_plus)

    mosaic_before = coll_Hybrid_mosaic(ImgColl_before, SsrData, start, stop, ExtraBandCode, CS_plus)

    # Merge the two mosaic images into one and return it  
    mosaic = MergeMosaics(mosaic_target, mosaic_before, SsrData, SsrData, 3.0)
    return mosaic.addBands(ssr_code_img)
  
  else: 
    # Create mosaic image for the year after the target
    AfterYear = TargetY + 1
    start     = start.update(AfterYear)
    stop      = stop.update(AfterYear)   
    
    # Prepare an image collection and then apply masks to each image in the collection 
    ImgColl_after        = IS.getCollection(SsrData, Region, start, stop, ExtraBandCode)
    #masked_ImgColl_after = IS.mask_collection(ImgColl_after, SsrData, CS_plus)

    mosaic_after = coll_Hybrid_mosaic(ImgColl_after, SsrData, start, stop, ExtraBandCode, CS_plus)

    mosaic = MergeMosaics(mosaic_target, mosaic_after, SsrData, SsrData, 3.0)

    # Create mosaic image for the year before the target
    PrevYear = TargetY - 1
    start    = start.update(PrevYear)
    stop     = stop.update(PrevYear)
    
    # Prepare an image collection and then apply masks to each image in the collection 
    ImgColl_before        = IS.getCollection(SsrData, Region, start, stop, ExtraBandCode)
    #masked_ImgColl_before = IS.mask_collection(ImgColl_before, SsrData, CS_plus)

    mosaic_before = coll_Hybrid_mosaic(ImgColl_before, SsrData, start, stop, ExtraBandCode, CS_plus)
    
    mosaic = MergeMosaics(mosaic, mosaic_before, SsrData, SsrData, 3.0)
    return mosaic.addBands(ssr_code_img)






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
def LSMix_PeriodMosaic(SsrData, Region, Year, StartDate, StopDate, ExtraBandCode, CS_plus):
  '''Creates a mosaic image for a region using the images acquired during a period of time. 
     
  Args:
      DataUnit(int): Data unit code integer. 1 and 2 represent TOA and surface reflectance, respectively;
      Region(ee.Geometry): The spatial polygon of a ROI;
      Year(int): A specified target year (must be a regular integer);
      Startdate(ee.Date or string): The start date string (e.g., '2020-06-01') or ee.Date object;
      StopDate(ee.Date or string): The end date string (e.g., '2020-06-30') or ee.Date object;
      ExtraBandCode(int): A integer code representing band type to be attached additionaly;
      CS_plus(Boolean): A flag indicating if to apply CloudScore+ mask.'''
  
  #================================================================================================
  # Determine a proper time period based on a given target year and an initial period 
  #================================================================================================
  year  = int(Year)
  start = ee.Date(StartDate).update(Year)
  stop  = ee.Date(StopDate).update(Year)
  unit  = SsrData['DATA_UNIT']

  #================================================================================================
  # Create a base Landsat mosaic image
  #================================================================================================
  ssr_main    = LS_Dict_from_year(Year, unit, 1)
  mosaic_main = coll_Hybrid_mosaic(ssr_main, Region, start, stop, ExtraBandCode, CS_plus)

  #print('\n\n<LSMix_PeriodMosaic> bands in main mosaic = ', mosaic_main.bandNames().getInfo())

  #================================================================================================
  # Create a secondary Landsat mosaic image
  #================================================================================================
  ssr_2nd    = LS_Dict_from_year(Year, unit, 2)
  mosaic_2nd = coll_Hybrid_mosaic(ssr_2nd, Region, start, stop, ExtraBandCode, CS_plus)

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
    if ExtraBandCode == Img.EXTRA_ANGLE:
      mosaic_main = mosaic_main.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'cosVZA', 'cosSZA', 'cosRAA', Img.pix_score, Img.pix_date])
      rest_bands = ['cosVZA', 'cosSZA', 'cosRAA', Img.pix_score, Img.pix_date]
    elif ExtraBandCode == Img.EXTRA_NDVI:
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
# Description: This function exports a given mosaic image to a specified location (either Google Drive or
#              Google Cloud Storage). The filenames of the exported images will be automatically generated 
#              based on tile name, image acquisition time and spatial resolution.
#
# Revision history:  2022-Mar-30  Lixin Sun  Initial creation 
#
#############################################################################################################
def export_mosaic(exe_Params, mosaic, SsrData, Region, for_LEAF, task_list):
  '''Exports one set of LEAF products to either Google Drive or Google Cloud Storage

     Args:
       fun_Params(dictionary): a dictionary storing other required running parameters;
       mosaic(ee.Image): the mosaic image to be exported;
       SsrData(Dictionary): A dictionary containing all info on a sensor type;
       Region(ee.Geometry): the spatial region of interest;
       for_LEAF(Boolean): A flag indicating if the mosaic is for LEAF;
       task_list([]): a list storing the links to exporting tasks.'''
  
  print('\n\n<export_mosaic> band names in mosaic = ', mosaic.bandNames().getInfo())
  #==========================================================================================================
  # Obtain some parameters from the given parameter dictionary
  #==========================================================================================================  
  year_str     = str(exe_Params['year'])     
  Scale        = int(exe_Params['resolution'])
  given_folder = str(exe_Params['out_folder'])
  out_location = str(exe_Params['out_location']).lower()

  region_str   = str(exe_Params['current_region'])
  period_str   = str(exe_Params['time_str'])
  out_style    = str(exe_Params['export_style']).lower()

  #==========================================================================================================
  # Create an exporting folder name or use a given one
  #==========================================================================================================
  form_folder  = region_str + '_' + year_str
  exportFolder = form_folder if len(given_folder) < 2 else given_folder  

  #==========================================================================================================
  # Create prefix filenames for peak or monthly mosaic band images 
  #==========================================================================================================  
  filePrefix = region_str + '_' + period_str + '_' + SsrData['NAME']

  #==========================================================================================================
  # Export LEAF products to a Google Drive directory 
  #========================================================================================================== 
  export_dict = {'scale': Scale,
                 'crs': exe_Params['projection'],
                 'maxPixels': 1e11,
                 'region': ee.Geometry(Region)}
  
  # Determine the bands to be exported according to specified spatial resolution 
  out_band_names = SsrData['OUT_BANDS'] if Scale >=20 else SsrData['10M_BANDS']
  if for_LEAF:
    out_band_names = out_band_names + ['cosVZA', 'cosSZA', 'cosRAA']

  if out_location.find('drive') > -1:  # Export to Google Drive
    print('<export_mosaic> Exporting to Google Drive......')
    export_dict['folder'] = exportFolder
    
    if out_style.find('comp') > -1:      
      filename  = filePrefix + '_' + str(Scale) + 'm'
      export_dict['image']          = mosaic.select(out_band_names).multiply(ee.Image(100)).uint16()
      export_dict['description']    = filename
      export_dict['fileNamePrefix'] = filename

      task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())

    else: 
      for band in out_band_names:
        filename  = filePrefix + '_' + band + '_' + str(Scale) + 'm'
        
        export_dict['image']          = mosaic.select(band).multiply(ee.Image(100)).uint16()
        export_dict['description']    = filename
        export_dict['fileNamePrefix'] = filename

        task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())
    
  elif out_location.find('storage') > -1:  # Exporting to Google Cloud Storage
    print('<export_mosaic> Exporting to Google Cloud Storage......')  
    export_dict['bucket'] = str(exe_Params['bucket'])    
    for band in out_band_names:
      filename  = filePrefix + '_' + band + '_' + str(Scale) + 'm'
      
      export_dict['image']          = mosaic.select(band).multiply(ee.Image(100)).uint16()
      export_dict['description']    = filename
      export_dict['fileNamePrefix'] = filename

      task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())

  elif out_location.find('asset') > -1:
    print('<export_mosaic> Exporting to Google Earth Assets......')
    asset_root = 'projects/ee-lsunott/assets/'

    for band in out_band_names:
      filename  = filePrefix + '_' + band + '_' + str(Scale) + 'm'
      
      export_dict['image']       = mosaic.select(band).multiply(ee.Image(100)).uint16()
      export_dict['description'] = filename
      export_dict['assetId']     = asset_root + exportFolder + '/' + filename

      task_list.append(ee.batch.Export.image.toAsset(**export_dict).start())
  




###################################################################################################
# Description: This function creates a mosaic image within a defined region by using all accessible
#              images acquired over a specified timeframe from the Landsat series and Sentinel-2 
#              A/B satellites.
#
# Revision history:  2023-Jun-06  Lixin Sun  Initial creation
#
###################################################################################################
def HLS_PeriodMosaic(DataUnit, Region, targetY, NbYs, StartD, StopD, ExtraBandCode):
  '''Creates a mosaic image for a region using the images acquired during a period of time. 
     
  Args:
      DataUnit(Dictionary): Data unit code integer. 1 and 2 represent TOA and surface reflectance, respectively;
      Region(ee.Geometry): The spatial polygon of a ROI;
      targetY(int): A specified target year (must be a regular integer);
      NbYs(int): The number of years
      StartD(ee.Date or string): The start date string (e.g., '2020-06-01') or ee.Date object;
      StopD(ee.Date or string): The end date string (e.g., '2020-06-30') or ee.Date object;
      ExtraBandCode(int): A integer code representing band type to be attached additionaly.'''
  
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

  return mix_mosaic   #, s2_mosaic, ls_mosaic






#############################################################################################################
# Description: The start/main function for operationally producing tile mosaic maps using Landsat or 
#              Sentinel2 data
#
# Revision history:  2021-Oct-28  Lixin Sun  Initial creation 
#                    2024-Feb-27  Lixin Sun  Modified so that customized spatial region or compositing period
#                                            can be handled.
#############################################################################################################
def Mosaic_production(inParams, MixSensor):
  '''Produces various mosaic products for one or more tiles using Landsat or Sentinel2 images
     Args:
       exe_Params(Dictionary): A dictionary storing required parameters;
       MixSensor(Boolean): Indicate if to utilize mixed image data;
       ExtraBandCode(int): A integer(EXTRA_NONE, EXTRA_ANGLE, EXTRA_NDVI) representing extra bands to be attached to each image.'''
  
  #==========================================================================================================
  # Standardize parameter dictionary for composite generation
  #==========================================================================================================
  params = eoPM.get_mosaic_params(inParams)

  #==========================================================================================================
  # get some required parameters
  #==========================================================================================================
  ssr_data    = Img.SSR_META_DICT[params['sensor']]
  year        = int(params['year'])
  nYears      = int(params['nbYears'])
  extra_bands = int(params['extra_bands'])
  cloud_score = params['CloudScore']

  #==========================================================================================================
  # Produce composite images for each region and each time window
  #==========================================================================================================
  task_list = []
  region_names = params['regions'].keys()
  nTimes = len(params['start_dates'])
  
  # Produce mosaic images for each spatial region
  for reg_name in region_names: 
    eoPM.set_spatial_region(params, reg_name)
    
    region = eoPM.get_spatial_region(params)  
    if 'tile' in reg_name:
      region = eoTG.expandSquare(region, 0.02)  

    # Produce mosaic images for each time window
    for TIndex in range(nTimes):
      params = eoPM.set_current_time(params, TIndex)      
      start, stop = eoPM.get_time_window(params, False)

      # Produce and export mosaic images for a time period and a region
      print('\n<Mosaic_production> Generate and export composite images for {}th time period and {} region......'.format(TIndex+1, reg_name))        
      mosaic = HomoPeriodMosaic(ssr_data, region, year, nYears, start, stop, extra_bands, cloud_score)      
      mosaic = Img.apply_gain_offset(mosaic, ssr_data, 100, False)
      #mosaic = LEAF_Mosaic(ssr_data, region, start, stop, True)

      # Export spectral mosaic images
      export_mosaic(params, mosaic, ssr_data, region, True, task_list)
    
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



'''
To run the Mosaic Tool, a set of parameters must be supplied. To simplify parameter provision, a Python dictionary is utilized as a container, capable of holding 11 “key:value” pairs (the last three are optional), each detailed as follows:
   
(1) Value for 'sensor' key: a string denoting the sensor type and data unit. Currently, valid values include 'L8_SR', 'S2_SR', 'L8_TOA' and 'S2_TOA', which denote Landsat 8/9 and Sentinel-2 surface reflectance and TOA reflectance data, respectively. 

(2) Value for 'year' key: a 4-digits integr representing the acquisition year (e.g., 2020) of the daily images used in compositing.

(3) Value for 'months' key: a list of integers specifying the months of a year (e.g., [6, 7] for June and July). With a list of month numbers, multiple monthly composite images can be generated through a single execution of the Mosaic Tool. To generate a composite image for a peak season 
(June 15 to September 15) of a year (defined by the value of the 'year' key), just include a negative integer in this list.

(4) Value for 'tile_names' key: a set of strings representing the names of grid tiles, each covering a 900km x 900km area. Providing a list of tile names allows the creation of composite images for multiple tiles through a single execution of the Mosaic Tool. 
    To generate a composite image for a customized region, an additional "key:value" pair must be included in this parameter dictionary (refer to the value specification for 'custom_region' key. 

(5) Value for 'resolution' key: an integer (e.g., 30 and 20 for Landsat and Sentinel-2 composites, respectively) defining the spatial resolution (in meters) for exporting resultant composite images.

(6) Value for 'out_location' key: a string specifying the destination location for exporting resultant composite images. Valid values for this key are 'drive' or 'storage', indicating Google Drive (GD) or Google Cloud Storage (GCS), respectively.

(7) Value for 'GCS_bucket' key: a string indicating a bucket name on GCS. This parameter is necessary only when the exporting destination is GCS ('storage' for 'out_location' key). Note that the specified bucket must exist on your GCS before exporting. 

(8) Value for 'out_folder' key: the folder name on GD or GCS for exporting composites. If you prefer not to export all the composites to the same directory, leave an empty string for this key. In this case, the Tool will automatically create separate folders for the composites of different tiles according to tile name and acquisition year.

(9) Value for 'custom_region' key: an "ee.Geometry" object created with the "ee.Geometry.Polygon()" function, taking a list of Latitude and Longitas coordinates as inputs. This 'key:value' pair is required only when a customized region has to be defined. Otherwise, DO NOT include this 'key:value' pair in parameter dictionary, as it will overwrite the values for the 'tile_names' key. 

(10) Value 'start_date' key: a string (e.g., '2022-06-15') for specifying the start date of a customized compositing period. 

(11) Value for 'end_date' key: a string (e.g., '2022-09-15') for specifying the end date of a custmoized compositing period. Please be aware that the strings for 'start_date' and 'end_date' keys should be omitted from this parameter dictionary unless a user-defined compositing period needs to be specified.

Among the 11 input parameters, two keys ('months' and 'tile_names') require list inputs. With different combinations between these two lists, various scenarios for composite production can be carried out. For instance, providing [7, 8] and ['tile41', 'tile42', 'tile43']) to 'months' and 'tile_names' keys, respectively, will result in the creation of three composites for each of July and August.
'''




# user_region = ee.Geometry.Polygon([[-76.12016546887865,45.183832177265906], 
#                                    [-75.38339483899584,45.170763450281996],
#                                    [-75.39026129407397,45.5639242833682], 
#                                    [-76.10505926770678,45.56776998764525], 
#                                    [-76.12016546887865,45.183832177265906]])

# params =  {
#     'sensor': 'S2_SR',            # A sensor type string (e.g., 'S2_SR' or 'L8_SR')
#     'year': 2022,                 # An integer representing image acquisition year
#     'nbYears': -1,                 # positive int for annual product, or negative int for monthly product
#     'months': [7,8,9],                # A list of integers represening one or multiple monthes     
#     'tile_names': ['tile33'],     # A list of (sub-)tile names (defined using CCRS' tile griding system) 
#     'out_location': 'drive',      # Exporting location ('drive', 'storage' or 'asset') 
#     'prod_names': ['mosaic'],
#     'resolution': 20,             # Exporting spatial resolution
#     'GCS_bucket': 's2_mosaic_2020',   # An unique bucket name on Google Cloud Storage
#     'out_folder': 'LEAF_mosaic',   # the folder name for exporting

#     #'custom_region': user_region, # A given user-defined region. Only include this 'key:value' pair as necessary
#     #'start_dates': ['2022-06-15'], # A list of strings representing the start dates of customized compositing periods.
#     #'end_dates': ['2022-09-15'],   # A list of strings representing the end dates of customized compositing periods.
#     #'CloudScore': False
# }


# Mosaic_production(params, False)
