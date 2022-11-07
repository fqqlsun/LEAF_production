######################################################################################################
# Description: most codes in this file were converted from JavaScript on 2021-Apr-09
######################################################################################################
import ee 

import eoImage as eoImg



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

  return start_date, stop_date  #Start and stop ee.Dates




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
  start = ee.Date.fromYMD(2000, 6, 15)
  stop  = ee.Date.fromYMD(2000, 9, 15)
  
  return start.update(Year), stop.update(Year)





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
def period_centre(StartDate, StopDate):
  '''Returns the middle date of a given time period. 
  Arg: 
    Start(string or ee.Date): Start date string;
    Stop(string or ee.Date): stop date string.'''  
  start = ee.Date(StartDate)
  stop  = ee.Date(StopDate)

  return ee.Date(start.millis().add(stop.millis()).divide(ee.Number(2.0)))



######################################################################################################
# Description: This function creates a image collection acquired by a sensor over a geographical 
#              region during a period of time.
#
# Revision history:  2021-May-20  Lixin Sun  Updated with newly developed function "GEE_catalog_name" 
#                    2021-Jun-09  Lixin Sun  Modified by using "get_cloud_rate" to deteremine cloud
#                                            coverage percentage.          
######################################################################################################
def getCollection(SensorCode, DataUnit, Region, StartDate, StopDate):  
  '''Returns a image collection acquired by a sensor over a geographical region during a period of time  

  Arg: 
     SensorCode: A sensor type code (one of 5, 7, 8, 9, 101 or 102);
     DataUnit: A Data unit code (1 or 2 for TOA and surface reflectance);
     Region(ee.Geometry): A geospatial polygon of ROI;
     start_date(string or ee.Date): The start acquisition date string (e.g., '2020-07-01');
     stop_date(string or ee.Date): The stop acquisition date string (e.g., '2020-07-31').'''

  # Cast the input parameters into proper formats  
  region = ee.Geometry(Region)
  start  = ee.Date(StartDate)
  stop   = ee.Date(StopDate)

  #Determine a cloud coverage percentage/rate based on sensor type and location 
  cloud_rate = eoImg.get_cloud_rate(SensorCode, region)  

  #Filtering the image collection with spatial region, time period and cloud coverage
  CollName     = eoImg.GEE_catalog_name(SensorCode, DataUnit)  
  SSR_Property = eoImg.get_property_names(SensorCode)
  
  #print('<getCollection> data catalog name = ', CollName)
  #print('<getCollection> collection property = ', CollProperty)  
  '''
  coll = ee.ImageCollection(CollName) \
               .filterBounds(polygon) \
               .filterDate(start, stop) \
               .filter(ee.Filter.gte(SSR_Property['Cloudcover'], cloud_rate)) \
               .filter(ee.Filter.gte(SSR_Property['vza'], -0.01)) \
               .filter(ee.Filter.gte(SSR_Property['sza'], -0.01)) \
               .filter(ee.Filter.gte(SSR_Property['vaa'], -0.01)) \
               .filter(ee.Filter.gte(SSR_Property['saa'], -0.01)) \
               .limit(5000)
  '''
  #==============================================================================================
  # "filterMetadata" Has been deprecated. But tried to use "ee.Filter.gte(property, value)", did 
  # not work neither.
  #==============================================================================================
  coll = ee.ImageCollection(CollName).filterBounds(region).filterDate(start, stop) \
               .filterMetadata(SSR_Property['Cloudcover'], 'less_than', cloud_rate) \
               .filterMetadata(SSR_Property['vza'], 'greater_than', 0.0) \
               .filterMetadata(SSR_Property['sza'], 'greater_than', 0.0) \
               .filterMetadata(SSR_Property['vaa'], 'greater_than', 0.0) \
               .filterMetadata(SSR_Property['saa'], 'greater_than', 0.0) \
               .limit(5000)
  
  return coll 
  


######################################################################################################
# Description: Creates a collection of satellite images acquired during a summer.
#
# Revision history:  2021-Apr-09  Lixin Sun  Converted from JavaScript
#
######################################################################################################
def peak_collection(SensorCode, DataUnit, Year, Region):
  '''Creates a collection of satellite images acquired during a summer.   

  Args: 
     SensorCode(int): A sensor type code integer (e.g., 5, 7, 8 and 21);
     DataUnit(int): Data product level (1 and 2 represent TOA and surface reflectance);
     Year(int): A targeted year integer;  
     Region(ee.Geometry): The geospatial polygon of ROI.
  '''  
  region      = ee.Geometry(Region)
  start, stop = summer_range(Year)

  return ee.ImageCollection(getCollection(SensorCode, DataUnit, region, start, stop))





###################################################################################################
# Description: This function creates a image collection acquired over the summer seasons of 
#              multiple years.
#
# Revision history:  2021-May-20  Lixin Sun  Initial creation 
#
###################################################################################################
def get_MultiSummers_Coll(SensorCode, DataUnit, Region, SeasonStart, SeasonStop, StartYear, StopYear):  
  '''Creates a image collection acquired over the summer seasons of multiple years.

  Arg: 
     SensorCode: A sensor type code (one of 5, 7, 8, 9, 21 or 22);
     DataUnit: A Data unit code (1 or 2 for TOA and surface reflectance);
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
  cloud_rate = eoImg.get_cloud_rate(SensorCode, region)  

  # Determine the name of image collection and its property
  CollName     = eoImg.GEE_catalog_name(SensorCode, DataUnit)  
  SSR_Property = eoImg.get_property_names(SensorCode)  

  # Create a raw image collection filtered with only boundary and cloud covereage
  raw_coll = ee.ImageCollection(CollName) \
               .filterBounds(region) \
               .filterMetadata(SSR_Property['Cloudcover'], 'less_than', cloud_rate)
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