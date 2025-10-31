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
    'sensor': '',                # A sensor type and data unit string (e.g., 'S2_SR' or 'L8_SR')    
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
    'score_weights': {'spectral': 1.0, 'temporal': 0.4, 'spatial': 0.9},   #or {'spectral': 1.0, 'temporal': 0.5, 'spatial': 0.9} for seasonal composite

    'monthly': True,             # A flag indicating if time windows are monthly. An user is not supposed to set this parameter
    'start_dates': [],
    'end_dates':  [],
    'regions':{},
    'scene_ID': '',         # A specified scene ID. An user is not supposed to set this parameter 
    'current_time': 0,      # The index in 'start_dates'/'end_dates'. An user is not supposed to set this parameter
    'current_region': '',   # Current region key. An user is not supposed to set this parameter

    'time_str': ''          #Current time string. An user is not supposed to set this parameter
}

MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']



#############################################################################################################
# Description: This function returns a list of valid month integers based on a given list of month integers.
#              (1) Keep only one negative integer if there are multiple negatives in original list;
#              (2) 
# Revision history:  2022-Aug-10  Lixin Sun  Initial creation
#
#############################################################################################################
def standard_months(inMonths):  
  out_months = []

  # Add one negative value (e.g., the first one found)
  negatives = [m for m in inMonths if m < 0]
  if negatives:
    out_months.append(negatives[0])

  # Add positive values greater than zero and less than 13
  out_months.extend([m for m in inMonths if 0 < m < 13])

  return list(dict.fromkeys(out_months))  # Only keep unique values





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
  nRegions     = len(inParams['regions'])  if 'regions'  in inParams else 0  
  scene_ID_len = len(inParams['scene_ID']) if 'scene_ID' in inParams else 0

  return True if nRegions > 0 or scene_ID_len > 5 else False 




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
  nStarts = len(inParams['start_dates'])
  nEnds   = len(inParams['end_dates'])

  if nStarts != nEnds:
    print('\n<set_current_time> The number of start_dates does not match end_dates!')
    return None
  elif current_time < 0 or current_time >= nStarts or current_time >= nEnds:
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
  region_names = inParams['regions'].keys() if 'regions' in inParams else []

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
def form_full_params(inParams):
  all_valid = True
  outParams = {}

  #==========================================================================================================
  # Confirm 'sensor' parameter
  #==========================================================================================================
  sensor_name = str(inParams['sensor']).upper() if 'sensor' in inParams else ''
  if sensor_name not in ['S2_SR', 'L5_SR', 'L7_SR', 'L8_SR', 'L9_SR']:
    all_valid = False
    outParams['sensor'] = ['S2_SR']
  else:
    outParams['sensor'] = sensor_name

  #==========================================================================================================
  # Confirm 'unit' parameter
  #==========================================================================================================  
  unit = int(inParams['unit']) if 'unit' in inParams else 0
  if unit not in [1, 2]:
    all_valid = False
    outParams['unit'] = 2
  else:
    outParams['unit'] = unit  
  
  #==========================================================================================================
  # Confirm 'year' parameter
  #==========================================================================================================
  year = int(inParams['year']) if 'year' in inParams else 0
  current_year = datetime.now().year
  if year < 1970 or year > current_year:
    all_valid = False
    outParams['year'] = current_year
  else:
    outParams['year'] = year  
  
  #==========================================================================================================
  # Confirm 'nbYears' parameter
  #==========================================================================================================
  nYears = int(inParams['nbYears']) if 'nbYears' in inParams else 0
  if nYears not in [1, 2, 3]:
    all_valid = False
    outParams['nbYears'] = 1
  else:
    outParams['nbYears'] = nYears  
  
  #==========================================================================================================
  # Confirm 'months' parameter
  #==========================================================================================================
  outParams['current_time'] = 0  # The index in 'start_dates'/'end_dates'
  if not has_custom_windows(inParams):
    months = standard_months(inParams['months']) if 'months' in inParams else [8]  
    outParams['monthly'] = True   

    if len(months) < 1:
      all_valid = False
      outParams['months'] = [8]
    else:      
      outParams['months'] = months
  else:
    outParams['monthly'] = False
    outParams['start_dates'] = inParams['start_dates']
    outParams['end_dates']   = inParams['end_dates']

  #==========================================================================================================
  # Confirm 'tile_names' parameter
  #==========================================================================================================
  if not has_custom_region(inParams):
    temp_names = inParams['tile_names'] if 'tile_names' in inParams else []  
    tile_names = []
    for tile in temp_names:
      if eoTG.is_valid_tile_name(tile):
        tile_names.append(tile)

    nTiles = len(tile_names)
    if nTiles < 1:
      all_valid = False
      outParams['tile_names'] = ['tile55']
    else:
      outParams['tile_names'] = tile_names
  else:
    outParams['regions'] = inParams['regions'],

  #==========================================================================================================
  # Confirm 'prod_names' parameter
  #==========================================================================================================
  prod_names = inParams['prod_names'] if 'prod_names' in inParams else []
  nProds = len(prod_names)
  if nProds < 1:
    all_valid = False
    outParams['prod_names'] = ['mosaic', 'pix_score', 'date', 'ssr_code']
  else:
    valid_prod_names        = ['LAI', 'fAPAR', 'fCOVER', 'Albedo', 'QC', 'date', 'partition', 'mosaic', 'pix_score', 'ssr_code']
    outParams['prod_names'] = [elem for elem in prod_names if elem in valid_prod_names]
    
    if len(outParams['prod_names']) < 1:
      outParams['prod_names'] = ['mosaic', 'pix_score', 'date', 'ssr_code']

  #==========================================================================================================
  # Confirm 'out_location' parameter
  #==========================================================================================================
  out_location = str(inParams['out_location']).upper() if 'out_location' in inParams else '' 
  if out_location not in ['DRIVE', 'STORAGE', 'ASSET']:
    all_valid = False
    outParams['out_location'] = 'drive'
  else:
    outParams['out_location'] = out_location

  #==========================================================================================================
  # Confirm 'resolution' parameter
  #==========================================================================================================
  resolution = int(inParams['resolution']) if 'resolution' in inParams else 0
  if resolution < 1:
    all_valid = False
    outParams['resolution'] = 20
  else:
    outParams['resolution'] = resolution

  #==========================================================================================================
  # Confirm 'GCS_bucket' parameter
  #==========================================================================================================
  out_bucket = str(inParams['GCS_bucket']) if 'GCS_bucket' in inParams else ''
  if len(out_bucket) < 2:
    all_valid = False
    outParams['GCS_bucket'] = 'leaf_gcs_default_bucket'
  else:
    outParams['GCS_bucket'] = out_bucket  

  #==========================================================================================================
  # Confirm 'out_folder' parameter
  #==========================================================================================================
  out_folder = str(inParams['out_folder']) if 'out_folder' in inParams else ''
  if Path(out_folder) == False or len(out_folder) < 2:
    all_valid = False
    outParams['out_folder'] = 'leaf_default_out_folder'
  else:
    outParams['out_folder'] = out_folder  
    
  #==========================================================================================================
  # Confirm 'export_style' parameter
  #==========================================================================================================  
  out_style = str(inParams['export_style']) if 'export_style' in inParams else ''
  if 'separ' not in out_style and 'comp' not in out_style:
    all_valid = False
    outParams['export_style'] = 'separate'
  else:
    outParams['export_style'] = out_style  

  #==========================================================================================================
  # Confirm 'projection' parameter
  #==========================================================================================================  
  out_proj = str(inParams['projection']).upper() if 'projection' in inParams else ''
  if 'EPSG:' not in out_proj:
    all_valid = False
    outParams['projection'] = 'EPSG:3979'
  else:
    outParams['projection'] = out_proj

  #==========================================================================================================
  # Confirm 'CloudScore' parameter
  #==========================================================================================================  
  if 'CloudScore' not in inParams:  
    outParams['CloudScore'] = False

  #==========================================================================================================
  # Confirm 'extra_bands' parameter
  #==========================================================================================================  
  if 'extra_bands' not in inParams:  
    outParams['extra_bands'] = Img.EXTRA_NONE

  #==========================================================================================================
  # Confirm 'extra_bands' parameter
  #==========================================================================================================  
  if 'scene_ID' not in inParams:  
    outParams['scene_ID'] = ''

  if 'current_time' not in inParams:  
    outParams['current_time'] = 0

  if 'current_region' not in inParams:  
    outParams['current_region'] = ''

  if 'time_str' not in inParams:  
    outParams['time_str'] = ''

  #==========================================================================================================
  # Confirm 'score_weights', which contains the wieghting factors for spectral, temporal and spatial scores  
  #==========================================================================================================  
  if 'score_weights' not in inParams:  
    outParams['score_weights'] = {'spectral': 1, 'temporal': 1, 'spatial': 1}
  else:
    weights = inParams['score_weights']
    outParams['score_weights'] = inParams['score_weights']
    if 'spectral' not in weights:
      outParams['score_weights']['spectral'] = 1

    if 'temporal' not in weights:
      outParams['score_weights']['temporal'] = 1

    if 'spatial' not in weights:
      outParams['score_weights']['spatial'] = 1

  return all_valid, outParams




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
    STD_months = standard_months(inParams['months']) if 'months' in inParams else []
    nMonths    = len(STD_months) # get the number of specified months

    year = inParams['year']
    inParams['start_dates'] = []
    inParams['end_dates']   = []
    for index in range(nMonths):
      month = STD_months[index]
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
  #out_Params = DefaultParams
  all_valid, out_Params = form_full_params(inParams)

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
  inParams['prod_names'] = ['mosaic', 'pix_score', 'date', 'ssr_code']  # Of course, product name should be always 'mosaic'
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





params =  {
     'sensor': 'S2',           # A sensor type string (e.g., 'S2_SR' or 'L8_SR')
     'unit': 3,                   # A data unit code (1 or 2 for TOA or surface reflectance)   
     'year': 2024,                # An integer representing image acquisition year
     'nbYears': 10,                # positive int for annual product, or negative int for monthly product
     'months': [-1,-2, 0, 1,3,3,5, 20, 32],         # A list of integers represening one or multiple monthes     
     'tile_names': ['tile231'],    # A list of (sub-)tile names (defined using CCRS' tile griding system) 
     'prod_names': ['mosa'],    #['mosaic', 'LAI', 'fCOVER', ]
     'out_location': 'dri',     # Exporting location ('drive', 'storage' or 'asset') 
     'resolution': 0,            # Exporting spatial resolution
     'GCS_bucket': 's2_mosaic_2020',  # An unique bucket name on Google Cloud Storage
     'out_folder': 'water_samples_May10',   # the folder name for exporting
     'score_weights': {'spectral': 1, 'temporal': 1, },

     'start_dates': [],
     'end_dates': []
}


update_default_params(params)
