######################################################################################################
# Description: most codes in this file were converted from JavaScript on 2021-Apr-09
######################################################################################################
import ee 

import Image as Img
import ImgMask as IM




######################################################################################################
# Description: This function returns the last date of a specified month.
#
# Revision history:  2022-Aug-08  Lixin Sun  Initial creation
#
######################################################################################################
def month_end(Month):
  month = ee.Number(Month)
  cond  = month.eq(ee.Number(1)).Or(month.eq(ee.Number(3))).Or(month.eq(ee.Number(5))) \
         .Or(month.eq(ee.Number(7))).Or(month.eq(ee.Number(8))).Or(month.eq(ee.Number(10))) \
         .Or(month.eq(ee.Number(12)))

  return ee.Algorithms.If(cond, ee.Number(31), ee.Algorithms.If(month.eq(ee.Number(2)), ee.Number(28), ee.Number(30)))



######################################################################################################
# Description: Creates the start and end date strings of a specified year and month
#
# Revision history:  2021-May-20  Lixin Sun  Initial creation
#                    2021-Oct-15  Lixin Sun  Added a new case when "inMonth" is out of valid range
#                                            (1 to 12), then the start and end dates of the peak season
#                                            will be returned. 
######################################################################################################
def month_range(Year, Month):
  '''Creates the start and end date strings of a specified year and month
     Args:
       Year(int or ee.Number): A specified year;
       Month(int or ee.Number): A specified month. When the value of this argument is out of range
                               (1 to 12), a time range for a peak season is returned. '''
  year  = ee.Number(Year)
  month = ee.Number(Month)
  
  year  = ee.Algorithms.If(year.lt(ee.Number(1980)).Or(year.gt(ee.Number(2050))), ee.Number(2020), year)
  month = ee.Algorithms.If(month.lt(ee.Number(1)).Or(month.gt(ee.Number(12))), ee.Number(7), month)

  start_date = ee.Date.fromYMD(year, month, ee.Number(1))
  stop_date  = ee.Date.fromYMD(year, month, month_end(month))

  return start_date, stop_date  






######################################################################################################
# Description: This function creates starting and stoping ee.Dates for a summer 
#
# Revision history:  2021-May-20  Lixin Sun  Initial creation
#
######################################################################################################
def summer_range(Year):
  '''Returns the stop date of growing peak season. 
  Arg: 
     Year(int): A regular pyhton integer, rather than a GEE object'''
  start = ee.Date.fromYMD(2000, 6, 15).update(Year)
  stop  = ee.Date.fromYMD(2000, 9, 15).update(Year)
  
  return start, stop





######################################################################################################
# Description: This function creates a summer centre date string 
######################################################################################################
def summer_centre(Year):
  '''Returns the middle date of growing peak season. 
  Arg: 
    Year(int): A regular pyhton integer, rather than a GEE object'''
  return ee.Date.fromYMD(Year, 7, 31)




######################################################################################################
# Description: This function returns the middle date of a given time period.
# 
# Revision history:  2021-May-20  Lixin Sun  Initial creation 
#  
######################################################################################################
def period_centre(StartD, StopD):
  '''Returns the middle date of a given time period. 
  Arg: 
    StartD(string or ee.Date): Start date string;
    StopD(string or ee.Date): Stop date string.'''  
  start = ee.Date(StartD)
  stop  = ee.Date(StopD)

  return ee.Date(start.millis().add(stop.millis()).divide(ee.Number(2.0)))





######################################################################################################
# Description: This function returns a time range based on a given centre date and time window size.
# 
# Revision history:  2023-Nov-20  Lixin Sun  Initial creation 
#  
######################################################################################################
def time_range(MidDate, WinSize):
  '''Returns a time range based on a given centre date and time window size.
  Arg: 
    MidDate(string or ee.Date): A given centre date or string;
    WinSize(int): Stop date string.'''  
  millis_per_day = ee.Number(86400000)
  half_millis    = ee.Number(WinSize/2).multiply(millis_per_day)
  centre         = ee.Date(MidDate)
  #year   = centre.get('year')
  centre_millis = centre.millis()
  start_millis  = centre_millis.subtract(half_millis)
  stop_millis   = centre_millis.add(half_millis)

  return ee.Date(start_millis), ee.Date(stop_millis)





######################################################################################################
# Description: This function returns the time window size based on given start and stop dates.
# 
# Revision history:  2023-Nov-20  Lixin Sun  Initial creation 
#  
######################################################################################################
def time_window_size(StartD, StopD):
  '''Returns the middle date of a given time period. 
  Arg: 
    StartD(string or ee.Date): Start date string;
    StopD(string or ee.Date): Stop date string.'''  
  millis_per_day = ee.Number(86400000)

  return ee.Date(StopD).millis().subtract(ee.Date(StartD).millis()).abs().divide(millis_per_day)





######################################################################################################
# Description: This function creates a image collection acquired by a sensor over a geographical 
#              region during a period of time.
#
# Revision history:  2021-May-20  Lixin Sun  Updated with newly developed function "GEE_catalog_name" 
#                    2021-Jun-09  Lixin Sun  Modified by using "get_cloud_rate" to deteremine cloud
#                                            coverage percentage.
#                    2022-Nov-10  Lixin Sun  Added a default input parameter called "CloudRate", which 
#                                            is an optional cloud coverage percentage/rate.  
#                    2023-Apr-14  Lixin Sun  Added a case for "MODIS/061/MOD09A1", which does have any
#                                            image property
#                    2023-Sep-30  Lixin Sun  For Landsat 8 or 9, if target year is after 2022, then
#                                            both of them will be put into the returned collection.
#                    2023-Nov-09  Lixin Sun  Attach a "Cloud Score+" band to each image in a 
#                                            Sentinel-2 image collection.
######################################################################################################
def getCollection(SsrData, Region, StartDate, StopDate, ExtraBandCode, CloudRate = -100):  
  '''Returns a image collection acquired by a sensor over a geographical region during a period of time  

  Arg: 
     SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
     Region(ee.Geometry): A geospatial polygon of ROI;
     start_date(string or ee.Date): The start acquisition date string (e.g., '2020-07-01');
     stop_date(string or ee.Date): The stop acquisition date string (e.g., '2020-07-31');
     CloudRate(float): a given cloud coverage rate.'''
  
  print('<getCollection> SsrData info:', SsrData)
  # Cast the input parameters into proper formats  
  region = ee.Geometry(Region)
  start  = ee.Date(StartDate)
  stop   = ee.Date(StopDate)
  year   = int(start.get('year').getInfo())
  print('\n<getCollection> The year of time window = ', year) 

  #===================================================================================================
  # Determine a cloud coverage percentage/rate 
  # Note: there are two ways to determine a cloud coverage percebtage/rate
  # (1) based on sensor type and the centre of the given spatial region
  # (2) a given cloud coverage percentage/rate (CloudRate) 
  #===================================================================================================
  cloud_rate = Img.get_cloud_rate(SsrData, region) if CloudRate < 0 or CloudRate > 99.99 else CloudRate 
  print('<getCollection> Used cloud rate = ', cloud_rate.getInfo())

  #===================================================================================================
  # "filterMetadata" Has been deprecated. But tried to use "ee.Filter.gte(property, value)", did 
  # not work neither.
  #===================================================================================================
  CollName  = SsrData['GEE_NAME']  
  ssr_code  = SsrData['SSR_CODE']
  data_unit = SsrData['DATA_UNIT'] 

  if ssr_code == Img.MOD_sensor: # for MODIS data
    coll = ee.ImageCollection(CollName).filterBounds(region).filterDate(start, stop) 
  elif ssr_code > Img.MAX_LS_CODE and ssr_code < Img.MOD_sensor: 
    # for Sentinel-2 data   
    # Note: Limiting SZA < 70.0 could lead to an empty image coolection for some Canadian Northen regions 
    coll = ee.ImageCollection(CollName).filterBounds(region).filterDate(start, stop) \
               .filterMetadata(SsrData['CLOUD'], 'less_than', cloud_rate) \
               .filterMetadata('system:asset_size', 'greater_than', 1000000) # Added on Feb 13, 2024
               #.filterMetadata(SsrData['SZA'], 'less_than', 70.0) \
               #.limit(10000)
               #.filterMetadata(SsrData['CLOUD'], 'less_than', cloud_up) \
               
    #-------------------------------------------------------------------------------------------
    # Attach a "Cloud Score+" band to each image in Sentinel-2 image collection
    # Note: This function is unstable for now (Feb. 10, 2024)
    #-------------------------------------------------------------------------------------------
    csPlus = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED') \
               .filterBounds(region).filterDate(start, stop)
    
    coll   = coll.map(lambda img: img.linkCollection(csPlus, ['cs']))

  elif ssr_code < Img.MAX_LS_CODE: 
    # for Landsat data
    if year < 2022 or ssr_code < Img.LS_sensor:
      # For one single Landsat sensor
      coll = ee.ImageCollection(CollName).filterBounds(region).filterDate(start, stop).filterMetadata(SsrData['CLOUD'], 'less_than', cloud_rate) 

      if ExtraBandCode == Img.EXTRA_ANGLE and data_unit == Img.sur_ref: 
        toa_ssr_data = Img.SSR_META_DICT['L8_TOA']
        toa_coll     = ee.ImageCollection(toa_ssr_data['GEE_NAME']).filterBounds(region).filterDate(start, stop).filterMetadata(toa_ssr_data['CLOUD'], 'less_than', cloud_rate) 
        
        coll = coll.map(lambda img: img.linkCollection(toa_coll, ['SZA', 'SAA', 'VZA', 'VAA']))

    else:
      if data_unit == Img.sur_ref:
        L8_sr_ssr_data = Img.SSR_META_DICT['L8_SR']
        L9_sr_ssr_data = Img.SSR_META_DICT['L9_SR']

        L8_sr_coll     = ee.ImageCollection(L8_sr_ssr_data['GEE_NAME']).filterBounds(region).filterDate(start, stop).filterMetadata(L8_sr_ssr_data['CLOUD'], 'less_than', cloud_rate)         
        L9_sr_coll     = ee.ImageCollection(L9_sr_ssr_data['GEE_NAME']).filterBounds(region).filterDate(start, stop).filterMetadata(L9_sr_ssr_data['CLOUD'], 'less_than', cloud_rate) 
        
        if ExtraBandCode == Img.EXTRA_ANGLE:
          L8_toa_ssr_data = Img.SSR_META_DICT['L8_TOA']
          L9_toa_ssr_data = Img.SSR_META_DICT['L9_TOA']
        
          L8_toa_coll = ee.ImageCollection(L8_toa_ssr_data['GEE_NAME']).filterBounds(region).filterDate(start, stop).filterMetadata(L8_toa_ssr_data['CLOUD'], 'less_than', cloud_rate) 
          L9_toa_coll = ee.ImageCollection(L9_toa_ssr_data['GEE_NAME']).filterBounds(region).filterDate(start, stop).filterMetadata(L9_toa_ssr_data['CLOUD'], 'less_than', cloud_rate) 

          L8_sr_coll = L8_sr_coll.map(lambda img: img.linkCollection(L8_toa_coll, ['SZA', 'SAA', 'VZA', 'VAA']))
          L9_sr_coll = L9_sr_coll.map(lambda img: img.linkCollection(L9_toa_coll, ['SZA', 'SAA', 'VZA', 'VAA']))

        coll = L8_sr_coll.merge(L9_sr_coll)
      else:
        L8_toa_ssr_data = Img.SSR_META_DICT['L8_TOA']
        L9_toa_ssr_data = Img.SSR_META_DICT['L9_TOA']
        
        L8_toa_coll = ee.ImageCollection(L8_toa_ssr_data['GEE_NAME']).filterBounds(region).filterDate(start, stop) 
        L9_toa_coll = ee.ImageCollection(L9_toa_ssr_data['GEE_NAME']).filterBounds(region).filterDate(start, stop) 

        coll = L8_toa_coll.merge(L9_toa_coll)

  elif ssr_code == Img.HLS_sensor:  # For harmonized Landsat and Sentinel-2
    coll = ee.ImageCollection(CollName).filterBounds(region) \
                                       .filterDate(start, stop) \
                                       .filterMetadata(SsrData['CLOUD'], 'less_than', cloud_rate) \
                                       #.filterMetadata(SsrData['SZA'], 'less_than', 70.0) 

  print('\n<getCollection> The name of data catalog = ', CollName)             
  print('<getCollection> The number of images in selected image collection = ', coll.size().getInfo())

  return coll 
  
  



######################################################################################################
# Description: This function Applies mask to each image in a given image collection 
#
# Note:  In the mask input to "ee.Image.updateMask" function, 1 = valid, while 0 = invalid. This is 
#        different from most mask, where 1 and 0 represent invalid and valid pixels. 
#
# Revision history:  2023-Nov-09  Lixin Sun  Initial creation 
#                    2023-Nov-20  Lixin Sun  Added CloudScore input parameter.
######################################################################################################
def mask_collection(ImgColl, SsrData, CloudScore):  
  '''Returns a image collection acquired by a sensor over a geographical region during a period of time  

  Arg: 
     ImgColl(ee.ImageCollection): a given image collection;
     SsrData(Dictionary): a Dictionary containing metadata associated with a sensor and data unit;     
     CloudScore(Boolean): a boolean variable indicating if to apply CloudScore+ mask to S2 image.'''
  
  ssr_code = dict(SsrData)['SSR_CODE']

  def apply_mask(image):
      mask = IM.Img_VenderMask(image, SsrData, IM.CLEAR_MASK)
      return image.updateMask(mask.Not()) 
  
  if ssr_code == Img.MOD_sensor: # for MODIS data
    return ImgColl
  
  elif ssr_code > Img.MAX_LS_CODE and ssr_code < Img.MOD_sensor: # for Sentinel-2 data
    if CloudScore == True:
      thresh = 0.6    
      return ImgColl.map(lambda img: img.updateMask(img.select('cs').gte(thresh)))
    else:
      return ImgColl.map(lambda img: apply_mask(img))  
    
  elif ssr_code < Img.MAX_LS_CODE: # for Landsat data
    return ImgColl.map(lambda img: apply_mask(img))
  elif ssr_code == Img.HLS_sensor:
    return ImgColl.map(lambda img: apply_mask(img))





######################################################################################################
# Description: Creates a collection of satellite images acquired during a summer.
#
# Revision history:  2021-Apr-09  Lixin Sun  Converted from JavaScript
#
######################################################################################################
def peak_collection(SsrData, Year, Region, CloudRate):
  '''Creates a collection of satellite images acquired during a summer.   

  Args: 
     SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
     Year(int): A targeted year integer;  
     Region(ee.Geometry): The geospatial polygon of ROI;
     CloudRate(float): A specified cloud coverage rate.'''  
  region      = ee.Geometry(Region)
  start, stop = summer_range(Year)

  return ee.ImageCollection(getCollection(SsrData, region, start, stop, Img.EXTRA_NONE, CloudRate))




######################################################################################################
# Description: This function return median blue mosaic band of a peak season
#
# Revision history:  2022-Jan-22  Lixin Sun  Initial creation
#                    2023-Mar-14  Lixin Sun  It was found that even peak season median blue does not
#                                            work well. 
######################################################################################################
def peak_median_blue(SsrData, Year, Region, CloudRate):
  peak_coll = peak_collection(SsrData, Year, Region, CloudRate)
  
  blue_name = SsrData['BLU'] 

  def get_blue(img) :
    #valid_mask = eoImgMsk.ValidMask(img, ssr_code, data_unit).Not() 
    return img.select([blue_name])  #.updateMask(valid_mask) # Applying mask is important here
  
  blue_coll = peak_coll.map(lambda image: get_blue(image))
  return blue_coll.median()




###################################################################################################
# Description: This function creates a image collection acquired over the summer seasons of 
#              multiple years.
#
# Revision history:  2021-May-20  Lixin Sun  Initial creation 
#
###################################################################################################
def get_MultiSummers_Coll(SsrData, Region, SeasonStart, SeasonStop, StartYear, StopYear):  
  '''Creates a image collection acquired over the summer seasons of multiple years.

  Arg: 
     SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
     Region(ee.Geometry): A geospatial polygon of ROI;
     season_start(string): The start date string (e.g., '06-15') of a season;
     season_stop(string): The stop date string (e.g., '09-15') of a season;
     start_year(int): A start year integer;
     stop_year(int): A stop year integer.'''
  #================================================================================================
  # Cast the input parameters into proper types  
  #================================================================================================
  region = ee.Geometry(Region)
  startD = str(SeasonStart)
  stopD  = str(SeasonStop)
  startY = int(StartYear) 
  stopY  = int(StopYear)
  
  season_start = ee.Date(str(startY) + '-' + startD)
  season_stop  = ee.Date(str(startY) + '-' + stopD)

  #================================================================================================
  # Create a raw image collection filtered only with region and cloud coverage
  #================================================================================================
  # Determine a cloud coverage percentage/rate based on sensor type and location 
  cloud_rate = Img.get_cloud_rate(SsrData, region)  

  # Determine the name of image collection and its property
  CollName   = SsrData['GEE_NAME']

  # Create a raw image collection filtered with only boundary and cloud covereage
  raw_coll = ee.ImageCollection(CollName) \
               .filterBounds(region) \
               .filterMetadata(SsrData['CLOUD'], 'less_than', cloud_rate)

  print('<get_MultiSummers_Coll> nb of images in raw coll = ', raw_coll.size().getInfo())               
  #================================================================================================
  # Define a function that can extract a annual image collection from raw image collection
  #================================================================================================ 
  def annual_coll(year, prev_coll):
    ann_coll = raw_coll.filterDate(season_start.update(year), season_stop.update(year))
    
    return ee.ImageCollection(prev_coll).merge(ann_coll)
  
  #================================================================================================
  # Create a list of years by generating a sequence from start and end years 
  #================================================================================================
  years = ee.List.sequence(startY+1, stopY)
  print('<get_MultiSummers_Coll> year list = ', years.getInfo())
  #================================================================================================
  # Generate annual image collection collected in summer season
  #================================================================================================
  start0 = str(startY) + '-' + startD
  stop0  = str(startY) + '-' + stopD

  init_coll = raw_coll.filterDate(start0, stop0)
  print('\n<get_MultiSummers_Coll> nb of images in init coll = ', init_coll.size().getInfo())  

  return ee.ImageCollection(years.iterate(annual_coll, init_coll))
