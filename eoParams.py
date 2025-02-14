import ee 
#ee.Authenticate()
ee.Initialize()


import ImgSet as IS
import Image as Img
import eoTileGrids as eoTG

import re
from pathlib import Path
from datetime import datetime


#############################################################################################################
# Description: Define a default execution parameter dictionary. 
# 
# Revision history:  2022-Mar-29  Lixin Sun  Initial creation
#                    2024-Aug-30  Lixin Sun  Changed two keys, 'start_date' and 'end_date', to 'start_dates'
#                                            and 'end_dates', and their corresponding values to lists. 
#############################################################################################################
DefaultParams = {
    'sensor': '',                # A sensor type and data unit string (e.g., 'S2_Sr' or 'L8_SR')    
    'unit': 2,                   # data unite (1=> TOA reflectance; 2=> surface reflectance)
    'year': 2019,                # An integer representing image acquisition year
    'nbYears': 1,                # positive int for annual product, or negative int for monthly product
    'months': [],                # A list of integers represening one or multiple monthes     
    'tile_names': [],            # A list of (sub-)tile names (defined using CCRS' tile griding system) 
    'prod_names': [],            # ['mosaic', 'LAI', 'fCOVER', 'date' ]
    'out_location': 'drive',     # Exporting location ('drive', 'storage' or 'asset') 
    'resolution': 30,            # Exporting spatial resolution
    'GCS_bucket': '',            # An unique bucket name on Google Cloud Storage
    'out_folder': '',            # the folder name for exporting
    'export_style': 'separate',  # Two values for this key: "separate" or "compact"   
    'projection': 'EPSG:3979',
    'CloudScore': False,
    'extra_bands': Img.EXTRA_NONE, 

    'monthly': True,             # A flag indicating if time windows are monthly
    'start_dates': [],
    'end_dates':  [],
    'regions':{},
    'scene_ID': '',
    'current_time': 0,  # The index in 'start_dates'/'end_dates'
    'current_region': '',

    'time_str': ''
}

# all_param_keys = ['sensor', 'unit', 'year', 'nbYears', 'months', 'tile_names', 'prod_names', 'out_location', 'resolution',
#                   'GCS_bucket', 'out_folder', 'export_style', 'projection', 'CloudScore', 'extra_bands',
#                   'monthly', 'start_dates', 'end_dates', 'regions', 'scene_ID', 'current_time', 'current_region', 'time_str']


MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


#############################################################################################################
# Description: This function returns a month name string according to a month number integer.
#  
# Revision history:  2022-Aug-10  Lixin Sun  Initial creation
#
#############################################################################################################
def get_MonthName(month_numb):
  month = int(month_numb)

  if month > 0 and month < 13:
    return MONTH_NAMES[month-1]
  else:
    return 'season'
  




#############################################################################################################
# Description: This function tells if there is a customized region defined in parameter dictionary.
# 
# Revision history:  2024-Feb-27  Lixin Sun  Initial creation
#
#############################################################################################################
def has_custom_region(inParams):  
  n_custom_regions = len(inParams['regions']) if 'regions' in inParams else 0
  
  if 'scene_ID' not in inParams:
    inParams['scene_ID'] = ''

  return True if n_custom_regions > 0 or len(inParams['scene_ID']) > 5 else False 





#############################################################################################################
# Description: This function tells if customized time windows are defined in a given parameter dictionary.
# 
# Revision history:  2024-Feb-27  Lixin Sun  Initial creation
#
#############################################################################################################
def has_custom_windows(inParams):
  start_len = len(inParams['start_dates']) if 'start_dates' in inParams else 0
  end_len   = len(inParams['end_dates']) if 'end_dates' in inParams else 0

  custom_time = False
  if start_len >= 1 and end_len >= 1 and start_len == end_len:
    custom_time = True
  
  elif start_len >= 1 and end_len >= 1 and start_len != end_len:  
    print('\n<has_custom_window> Inconsistent customized time list!')
  
  return custom_time
  




#############################################################################################################
# Description: This function sets values for 'curent_time' and 'time_str' keys based on 'current_time' input
# 
# Revision history:  2024-Apr-08  Lixin Sun  Initial creation
#
#############################################################################################################
def set_current_time(inParams, current_time):
  '''Sets values for 'curent_time' and 'time_str' keys based on 'current_time' input
     Args:
       inParams(Dictionary): A dictionary storing required input parameters;
       current_time(Integer): An index in 'start_dates' and 'end_dates' lists.'''
  
  if 'start_dates' not in inParams or 'end_dates' not in inParams:
    print('\n<set_current_time> There is no \'start_dates\' or \'end_dates\' key!')
    return None
  
  #==========================================================================================================
  # Ensure the given 'current_time' is valid.
  #==========================================================================================================
  ndates = len(inParams['start_dates'])

  if current_time < 0 or current_time >= ndates:
    print('\n<set_current_time> Invalid \'current_time\' was provided!')
    return None
  
  #==========================================================================================================
  # Set values for 'current_time' and 'time_str' keys
  #==========================================================================================================
  inParams['current_time'] = current_time

  if inParams['monthly']:
    inParams['time_str'] = get_MonthName(int(inParams['months'][current_time]))
  else:  
    inParams['time_str'] = str(inParams['start_dates'][current_time]) + '_' + str(inParams['end_dates'][current_time])

  return inParams





#############################################################################################################
# Description: This function sets value for 'region_str' key based on if a customized spatial region has been 
#              specified.
# 
# Revision history:  2024-Apr-08  Lixin Sun  Initial creation
#
#############################################################################################################
def set_spatial_region(inParams, region_name):
  region_names = inParams['regions'].keys()

  if region_name not in region_names:
    print('\n<set_spatial_region> Invalid region name!')
    return None
    
  inParams['current_region'] = region_name

  return inParams




#############################################################################################################
# Description: This function validate a given user parameter dictionary.
#
# Revision history:  2024-Jun-07  Lixin Sun  Initial creation
#       
#############################################################################################################
def valid_params(inParams):
  all_valid = True
  #==========================================================================================================
  # Validate values of critical parameters
  #==========================================================================================================
  # Confirm 'sensor' parameter
  sensor_name = str(inParams['sensor']).upper()  
  if sensor_name not in ['S2_SR', 'L5_SR', 'L7_SR', 'L8_SR', 'L9_SR']:
    all_valid = False
    print('<valid_user_params> Invalid sensor or unit was specified!')
  
  # Confirm 'unit' parameter
  unit = int(inParams['unit'])
  if unit not in [1, 2]:
    all_valid = False
    print('<valid_user_params> Invalid data unit was specified!')
  
  # Confirm 'year' parameter
  year = int(inParams['year'])
  if year < 1970 or year > datetime.now().year:
    all_valid = False
    print('<valid_user_params> Invalid year was specified!')
  
  # Confirm 'nbYears' parameter
  nYears = int(inParams['nbYears'])
  if nYears > 3:
    all_valid = False
    print('<valid_user_params> Invalid number of years was specified!')
  
  # Confirm 'months' parameter
  if not has_custom_windows(inParams):
    nMonths = len(inParams['months'])
    if nMonths < 1:
      all_valid = False
      print('<valid_user_params> No month was specified!')
    else:
      max_month = max(inParams['months'])
      min_month = min(inParams['months'])
      if max_month > 12 or min_month < 1:
        all_valid = False
        print('<valid_user_params> Invalid month number was specified!')
  
  # Confirm 'tile_names' parameter
  if not has_custom_region(inParams):
    tile_names = inParams['tile_names']
    nTiles = len(tile_names)
    if nTiles < 1:
      all_valid = False
      print('<valid_user_params> No tile name was specified for tile_names key!')
  
    for tile in tile_names:
      if eoTG.is_valid_tile_name(tile) == False:
        all_valid = False
        print('<valid_user_params> {} is an invalid tile name!'.format(tile))

  # Confirm 'prod_names' parameter
  prod_names = inParams['prod_names']
  nProds = len(prod_names)
  if nProds < 1:
    all_valid = False
    print('<valid_user_params> No product name was specified for prod_names key!')
  
  valid_prod_names = ['LAI', 'fAPAR', 'fCOVER', 'Albedo', 'mosaic', 'QC', 'date', 'partition']
  presence = [element in valid_prod_names for element in prod_names]
  if False in presence:
    all_valid = False
    print('<valid_user_params> At least one of the specified products is invalid!')
  
  # Confirm 'out_location' parameter
  out_location = str(inParams['out_location']).upper()  
  if out_location not in ['DRIVE', 'STORAGE', 'ASSET']:
    all_valid = False
    print('<valid_user_params> Invalid out location was specified!')

  # Confirm 'resolution' parameter
  resolution = int(inParams['resolution'])
  if resolution < 1:
    all_valid = False
    print('<valid_user_params> Invalid spatial resolution was specified!')

  # Confirm 'out_folder' parameter
  out_folder = str(inParams['out_folder'])
  if Path(out_folder) == False or len(out_folder) < 2:
    all_valid = False
    print('<valid_user_params> The specified output path is invalid!')
    
  return all_valid




#############################################################################################################
# Description: This function creates the start and end dates for a list of user-specified months and save 
#              them into two lists with 'start_dates' and 'end_dates' keys.
#
# Revision history  2024-Sep-03  Lixin Sun  Initial creation
#
#############################################################################################################
def form_time_windows(inParams):
  if not has_custom_windows(inParams):
    #There is no customized time window defined
    inParams['monthly'] = True
    nMonths = len(inParams['months'])  # get the number of specified months

    year = inParams['year']
    inParams['start_dates'] = []
    inParams['end_dates']   = []
    for index in range(nMonths):
      month = inParams['months'][index]
      start, end = IS.month_range(year, month, False)

      inParams['start_dates'].append(start)
      inParams['end_dates'].append(end) 

  else:  #There are customized time windows defined
    inParams['monthly'] = False
    # nStarts = len(inParams['start_dates'])
    # nEnds   = len(inParams['end_dates'])

    # if nStarts != nEnds:
    #   print('<form_time_windows>')

  return set_current_time(inParams, 0)
  




#############################################################################################################
# Description: This function creates the start and end dates for a list of user-specified months and save 
#              them into two lists with 'start_dates' and 'end_dates' keys.
#
# Revision history  2024-Sep-03  Lixin Sun  Initial creation
#
#############################################################################################################
def form_spatial_regions(inParams):
  if not has_custom_region(inParams):
    inParams['regions'] = {}
    for tile_name in inParams['tile_names']:      
      if eoTG.is_valid_tile_name(tile_name):
        inParams['regions'][tile_name] = eoTG.PolygonDict.get(tile_name)
    
    return set_spatial_region(inParams, inParams['tile_names'][0])  
  
  else:
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
#                    2024-Sep-03  Lixin Sun  Adjusted to ensure that regular months/season will also be 
#                                            handled as customized time windows.    
#############################################################################################################
def update_default_params(inParams):  
  out_Params = DefaultParams
  
  #==========================================================================================================
  # Merge given user parameters into "out_Params"
  #==========================================================================================================
  user_keys      = list(inParams.keys())  
  invalid_params = {}

  for user_key in user_keys:
    if user_key in out_Params:
      out_Params[user_key] = inParams[user_key]
    else:
      invalid_params[user_key] = inParams[user_key]
  
  if len(invalid_params) > 0:
    print('\n\n<update_default_params>The following given key-value pairs are invalid!')
    print(invalid_params)
    return None

  #==========================================================================================================
  # Confirm all required parameters are valid
  #==========================================================================================================
  if not valid_params(out_Params):
    print('\n\n<update_default_params>The following given key-value pairs are invalid!')
    return None
  
  #==========================================================================================================
  # If regular months (e.g., 5,6,7) or season (e.g., -1) are specified, then convert them to date strings and
  # save in the lists corresponding to 'start_dates' and 'end_dates' keys. In this way, regular months/season
  # will be dealed with as customized time windows.    
  #==========================================================================================================
  out_Params = form_time_windows(out_Params)  
 
  #==========================================================================================================
  # If only regular tile names are specified, then create a dictionary with tile names and their 
  # corresponding 'ee.Geometry.Polygon' objects as keys and values, respectively.   
  #==========================================================================================================
  out_Params = form_spatial_regions(out_Params)  
 
  # return modified parameter dictionary 
  return out_Params





############################################################################################################# 
# Description: Obtain a parameter dictionary for LEAF tool
#############################################################################################################
def get_LEAF_params(inParams):
  print('\n\n<get_LEAF_params> input parameters:', inParams)
  inParams['unit'] = 2                     # Always surface reflectance for LEAF production
  out_Params = update_default_params(inParams)  # Modify default parameters with given ones    
  
  print('\n\n<get_LEAF_params> output parameters:', out_Params)
  return out_Params  





#############################################################################################################
# Description: Obtain a parameter dictionary for Mosaic tool
#############################################################################################################
def get_mosaic_params(inParams):
  inParams['prod_names'] = ['mosaic']           # Product name should always be 'mosaic'
  out_Params = update_default_params(inParams)  # Modify default parameter dictionary with a given one

  return out_Params  



#############################################################################################################
# Description: Obtain a parameter dictionary for land cover classification tool
#############################################################################################################
def get_LC_params(inParams):
  inParams['prod_names'] = ['mosaic']        # Of course, product name should be always 'mosaic'
  out_Params = update_default_params(inParams) # Modify default parameter dictionary with a given one  

  return out_Params 




#############################################################################################################
# Description: This function returns a valid spatial region defined in parameter dictionary.
# 
# Revision history:  2024-Feb-27  Lixin Sun  Initial creation
#
#############################################################################################################
def get_spatial_region(inParams):
  reg_name = inParams['current_region']
  valid_reg_names = inParams['regions'].keys()

  if reg_name in valid_reg_names:
    return inParams['regions'][reg_name]
  else:
    print('\n<get_spatial_region> Invalid spatial region name provided!')
    return None





#############################################################################################################
# Description: This function returns a valid time window defined in parameter dictionary.
# 
# Revision history:  2024-Feb-27  Lixin Sun  Initial creation
#                    2024-Sep-03  Lixin Sun  Added 'AutoIncr' input parameter so that the value 
#                                            corresponding to 'current_time' is increased automatically. 
#############################################################################################################
def get_time_window(inParams, ee_Date_format = True):
  current_time = inParams['current_time']
  nDates       = len(inParams['start_dates'])
    
  if current_time >= nDates:
    print('\n<get_time_window> Invalidate \'current_time\' value!')
    return None, None

  start = inParams['start_dates'][current_time]
  end   = inParams['end_dates'][current_time]
  
  if ee_Date_format:
    return ee.Date(start), ee.Date(end)  
  else:
    return start, end





# params =  {
#      'sensor': 'S2_SR',           # A sensor type string (e.g., 'S2_SR' or 'L8_SR')
#      'unit': 2,                   # A data unit code (1 or 2 for TOA or surface reflectance)   
#      'year': 2023,                # An integer representing image acquisition year
#      'nbYears': 1,                # positive int for annual product, or negative int for monthly product
#      'months': [7, 6, 8],               # A list of integers represening one or multiple monthes     
#      'tile_names': ['tile23'],    # A list of (sub-)tile names (defined using CCRS' tile griding system) 
#      'prod_names': ['mosaic'],          #['mosaic', 'LAI', 'fCOVER', ]
#      'out_location': 'drive',        # Exporting location ('drive', 'storage' or 'asset') 
#      'resolution': 30,            # Exporting spatial resolution
#      'GCS_bucket': 's2_mosaic_2020',  # An unique bucket name on Google Cloud Storage
#      'out_folder': 'water_samples_May10',   # the folder name for exporting

#      'start_dates': [],
#      'end_dates': []
# }


# update_default_params(params)
