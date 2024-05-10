import ee 

import ImgSet as IS
import eoTileGrids as eoTG


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
    'prod_way': '',              # The way of generating products, 'tile' or 'customized'
    'CloudScore': False
}




############################################################################################################# 
# Description: Obtain a parameter dictionary for LEAF tool
#############################################################################################################
def get_LEAF_params(inParams):
  out_Params = update_default_params(inParams)  # Modify default parameter dictionary with a given one
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
# Description: This function modifies default parameter dictionary based on a given parameter dictionary.
# 
# Note:        The given parameetr dictionary does not have to include all "key:value" pairs, just only the
#              pairs need to be modified.
#
# Revision history:  2022-Mar-29  Lixin Sun  Initial creation
#
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

  # return modified parameter dictionary 
  return out_Params



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
  #stop_len  = len(inParams['stop_date'])
  print('<is_custom_window> The string lengths of start and end dates are:', start_len, end_len)

  return True if start_len > 7 and end_len > 7 else False





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
  elif 'tile_name' in all_keys:
    tile   = inParams['tile_name']    
    return eoTG.PolygonDict.get(tile)
  else:
    tile   = inParams['tile_names'][0]
    return eoTG.PolygonDict.get(tile)




#############################################################################################################
# Description: This function returns a valid time window defined in parameter dictionary.
# 
# Revision history:  2024-Feb-27  Lixin Sun  Initial creation
#
#############################################################################################################
def get_time_window(inParams):
  all_keys = inParams.keys()

  if is_custom_window(inParams) == True:
    #year      = inParams['year']
    start_str = inParams['start_date']
    end_str   = inParams['end_date']
    return ee.Date(start_str), ee.Date(end_str)
  elif 'month' in all_keys:
    return IS.month_range(inParams['year'], inParams['month'])
  elif 'nbYears' in all_keys:
    nYears = inParams['nbYears']
    year   = inParams['year']
    return IS.summer_range(year) if nYears < 0 else IS.month_range(year, inParams['months'][0])
  else:
    return IS.month_range(inParams['year'], inParams['months'][0])