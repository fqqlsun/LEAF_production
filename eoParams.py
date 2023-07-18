#############################################################################################################
# Automatically set searching path for eo****.py code
# 
# Revision history:  2022-Mar-29  Lixin Sun  Initial creation
#
#############################################################################################################
import ee


sensor_name = 'sensor'
data_unit   = 'unit'

#############################################################################################################
# Description: Define a default execution parameter dictionary. 
# 
# Revision history:  2022-Mar-29  Lixin Sun  Initial creation
#
#############################################################################################################
DefaultParams = {
    'sensor': 'S2_SR',           # A sensor type and data unit string (e.g., 'S2_Sr' or 'L8_SR')
    'unit': 2,                   # A data unit code (1 or 2 for TOA or surface reflectance)    
    'year': 2019,                # An integer representing image acquisition year
    'nbYears': 1,                # positive int for annual product, or negative int for monthly product
    'months': [5,6,7,8,9,10],    # A list of integers represening one or multiple monthes     
    'tile_names': ['tile55'],    # A list of (sub-)tile names (defined using CCRS' tile griding system) 
    'prod_names': ['mosaic'],    #['mosaic', 'LAI', 'fCOVER', ]
    'location': 'storage',       # Exporting location ('drive', 'storage' or 'asset') 
    'resolution': 30,            # Exporting spatial resolution
    'bucket': 's2_mosaic_2020',  # An unique bucket name on Google Cloud Storage
    'folder': '',                # the folder name for exporting
    'reducer': ee.Reducer.mean(),
    'buff_radius': 10, 
    'tile_scale': 4,
    'export_style': 'separate'}



def get_DefaultParams(): 
  return DefaultParams



############################################################################################################# 
# Description: Obtain a parameter dictionary for LEAF tool
#############################################################################################################
def get_LEAF_params(inParams):
  out_Params = set_Params(inParams)  # Modify default parameter dictionary with a given one
  out_Params['nbYears'] = -1         # Produce monthly products in most cases
  out_Params['unit']    = 2          # Always surface reflectance for LEAF production

  return out_Params  



#############################################################################################################
# Description: Obtain a parameter dictionary for Mosaic tool
#############################################################################################################
def get_mosaic_params(inParams):
  out_Params = set_Params(inParams)      # Modify default parameter dictionary with a given one
  out_Params['prod_names'] = ['mosaic']  # Of course, product name should be always 'mosaic'

  return out_Params  



#############################################################################################################
# Description: Obtain a parameter dictionary for land cover classification tool
#############################################################################################################
def get_LC_params(inParams):
  out_Params = set_Params(inParams)      # Modify default parameter dictionary with a given one
  out_Params['prod_names'] = ['mosaic']  # Of course, product name should be always 'mosaic'

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
def set_Params(inParams):  
  out_Params = DefaultParams

  # get the number of keys in the given dictionary
  inKeys = inParams.keys()  
  
  # For each key in the given dictionary, modify corresponding "key:value" pair
  for ikey in inKeys:
    out_Params[ikey] = inParams.get(ikey)

  # return modified parameter dictionary 
  return out_Params