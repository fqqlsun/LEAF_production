import ee 

import ImgSet as IS
import Image as Img
import eoTileGrids as eoTG
import re


#############################################################################################################
# Description: Define a default execution parameter dictionary. 
# 
# Revision history:  2022-Mar-29  Lixin Sun  Initial creation
#
#############################################################################################################
DefaultParams = {
    'sensor': 'S2_SR',           # A sensor type and data unit string (e.g., 'S2_Sr' or 'L8_SR')    
    'unit': 2,                   # data unite (1=> TOA reflectance; 2=> surface reflectance)
    'year': 2019,                # An integer representing image acquisition year
    'nbYears': 1,                # positive int for annual product, or negative int for monthly product
    'months': [5,6,7,8,9,10],    # A list of integers represening one or multiple monthes     
    'tile_names': ['tile55'],    # A list of (sub-)tile names (defined using CCRS' tile griding system) 
    'prod_names': ['mosaic'],    # ['mosaic', 'LAI', 'fCOVER', ]
    'out_location': 'drive',     # Exporting location ('drive', 'storage' or 'asset') 
    'spatial_scale': 30,         # Exporting spatial resolution
    'GCS_bucket': '',            # An unique bucket name on Google Cloud Storage
    'out_folder': '',            # the folder name for exporting
    'export_style': 'separate',
    'start_date': '',
    'end_date':  '',
    'scene_ID': '',
    'projection': 'EPSG:3979',
    'CloudScore': False,

    'current_month': -1,
    'current_tile': '',
    'time_str': '',
    'region_str': ''
}



#############################################################################################################
# Description: This function tells if there is a customized region defined in parameter dictionary.
# 
# Revision history:  2024-Feb-27  Lixin Sun  Initial creation
#
#############################################################################################################
def is_custom_region(inParams):
  all_keys = inParams.keys()

  if 'custom_region' in all_keys:
    return True
  elif 'scene_ID' in all_keys: 
    return True if len(inParams['scene_ID']) > 5 else False
  else:
    return False 



#############################################################################################################
# Description: This function tells if there is a customized time window defined in parameter dictionary.
# 
# Revision history:  2024-Feb-27  Lixin Sun  Initial creation
#
#############################################################################################################
def is_custom_window(inParams):
  start_len = len(inParams['start_date'])
  end_len   = len(inParams['end_date'])
  #print('<is_custom_window> start and end date lengthes are:', start_len, end_len)
  
  return True if start_len > 7 and end_len > 7 else False
  


#############################################################################################################
# Description: This function makes the year values corresponding to 'start_date', 'end_date' and 'year' keys
#              in a execution parameter dictionary are consistent.
# 
# Revision history:  2024-Apr-08  Lixin Sun  Initial creation
#
#############################################################################################################
def year_consist(inParams):
  start_date = str(inParams['start_date'])
  end_date   = str(inParams['end_date'])  
  
  if len(start_date) > 7 and len(end_date) > 7:
    # Modify the year of 'end_date' string using the year of 'start_date'  
    start_tokens = re.split('-|_', start_date)
    end_tokens   = re.split('-|_', end_date)
    inParams['end_date'] = start_tokens[0] + '-' + end_tokens[1] + '-' + end_tokens[2]
  
    # Modify the value corresponding 'year' key in parameter dictionary
    inParams['year'] = start_tokens[0]

  return inParams



#############################################################################################################
# Description: This function sets value for 'time_str' key based on if a customized time window has been 
#              specified.
# 
# Revision history:  2024-Apr-08  Lixin Sun  Initial creation
#
#############################################################################################################
def set_time_str(inParams, custon_window = True):
  current_month = inParams['current_month']

  if custon_window == True:
    inParams['time_str'] = str(inParams['start_date']) + '_' + str(inParams['end_date'])

  elif current_month > 0 and current_month < 13:
    inParams['time_str'] = Img.get_MonthName(current_month)

  else:
    inParams['time_str'] = 'season'

  return inParams



#############################################################################################################
# Description: This function sets value for 'region_str' key based on if a customized spatial region has been 
#              specified.
# 
# Revision history:  2024-Apr-08  Lixin Sun  Initial creation
#
#############################################################################################################
def set_region_str(inParams, custon_region = True):
  if custon_region == True:
    inParams['region_str'] = 'custom_region'
    
  else:
    inParams['region_str'] = inParams['current_tile']

  return inParams





#############################################################################################################
# Description: This function modifies default parameter dictionary based on a given parameter dictionary.
# 
# Note:        The given parameetr dictionary does not have to include all "key:value" pairs, only the pairs
#              as needed.
#
# Revision history:  2022-Mar-29  Lixin Sun  Initial creation
#                    2024-Apr-08  Lixin Sun  Incorporated modifications according to customized time window
#                                            and spatial region.
#############################################################################################################
def update_default_params(inParams):  
  out_Params = DefaultParams

  # get the number of keys in the given dictionary
  inKeys = inParams.keys()  
  
  # For each key in the given dictionary, modify corresponding "key:value" pair
  for ikey in inKeys:
    out_Params[ikey] = inParams.get(ikey)
  
  # Ensure "CloudScore" is False if sensor type is not Sentinel-2 data
  sensor_type = out_Params['sensor'].lower()
  if sensor_type.find('s2') < 0:
    out_Params['CloudScore'] = False 
  
  #==========================================================================================================
  # If a customized time window has been provided
  #==========================================================================================================
  if is_custom_window(out_Params) == True:
    #Ensure all the year values in a parameter dictionary are consistent 
    out_Params = year_consist(out_Params)
    #Set value associated with 'time_str' key
    out_Params = set_time_str(out_Params, True)
 
  #==========================================================================================================
  # If a customized spatial region has been provided
  #==========================================================================================================
  if is_custom_region(out_Params) == True: 
    #Set value associated with 'region_str' key
    out_Params = set_region_str(out_Params, True)
  
  # return modified parameter dictionary 
  return out_Params



############################################################################################################# 
# Description: Obtain a parameter dictionary for LEAF tool
#############################################################################################################
def get_LEAF_params(inParams):
  out_Params = update_default_params(inParams)  # Modify default parameters with given ones
  out_Params['nbYears'] = -1                    # Produce monthly products in most cases
  out_Params['unit']    = 2                     # Always surface reflectance for LEAF production

  return out_Params  



#############################################################################################################
# Description: Obtain a parameter dictionary for Mosaic tool
#############################################################################################################
def get_mosaic_params(inParams):
  out_Params = update_default_params(inParams)  # Modify default parameter dictionary with a given one
  out_Params['prod_names'] = ['mosaic']         # Of course, product name should be always 'mosaic'

  return out_Params  



#############################################################################################################
# Description: Obtain a parameter dictionary for land cover classification tool
#############################################################################################################
def get_LC_params(inParams):
  out_Params = update_default_params(inParams) # Modify default parameter dictionary with a given one
  out_Params['prod_names'] = ['mosaic']        # Of course, product name should be always 'mosaic'

  return out_Params 







#############################################################################################################
# Description: This function returns a valid spatial region defined in parameter dictionary.
# 
# Revision history:  2024-Feb-27  Lixin Sun  Initial creation
#
#############################################################################################################
def get_spatial_region(inParams):
  all_keys = inParams.keys()

  if 'custom_region' in all_keys:
    return inParams['custom_region']
  
  elif len(inParams['current_tile']) > 2:
    return eoTG.PolygonDict.get(inParams['current_tile'])
  
  elif len(inParams['tile_names'][0]) > 2:
    return eoTG.PolygonDict.get(inParams['tile_names'][0])
  
  else:
    print('<get_spatial_region> No spatial region defined!!!!')




#############################################################################################################
# Description: This function returns a valid time window defined in parameter dictionary.
# 
# Revision history:  2024-Feb-27  Lixin Sun  Initial creation
#
#############################################################################################################
def get_time_window(inParams):  
  if is_custom_window(inParams) == True:
    # Get a customized timeframe    
    start_date = ee.Date(inParams['start_date'])
    end_date   = ee.Date(inParams['end_date'])

    # Ensure the years for start_date and end_date are consistent 
    start_year = start_date.get('year')
    end_date   = end_date.update(start_year)

    # Return the start and end dates of a customized timeframe
    return start_date, end_date
  
  else:
    current_month = inParams['current_month']
    if current_month > 0:
      if current_month > 12:
        current_month = 12

      # Return the start and end dates of a month
      return IS.month_range(inParams['year'], current_month)
    else:  
      nYears = inParams['nbYears']
      year   = inParams['year']
   
      if nYears < 0 or current_month < 0:
        # Return start and end dates of a peak season
        return IS.summer_range(year) 
      else:
        month = max(inParams['months'])
        if month > 12:
          month = 12

        if month < 1:
          month = 1

        return IS.month_range(year, month)
