
#############################################################################################################
# Description: Define a default execution parameter dictionary. 
# 
# Revision history:  2022-Mar-29  Lixin Sun  Initial creation
#
#############################################################################################################
DefaultParams = {
    'sensor': 'S2_SR',           # A sensor type and data unit string (e.g., 'S2_Sr' or 'L8_SR')    
    'year': 2019,                # An integer representing image acquisition year
    'nbYears': 1,                # positive int for annual product, or negative int for monthly product
    'months': [5,6,7,8,9,10],    # A list of integers represening one or multiple monthes     
    'tile_names': ['tile55'],    # A list of (sub-)tile names (defined using CCRS' tile griding system) 
    'prod_names': ['mosaic'],    #['mosaic', 'LAI', 'fCOVER', ]
    'out_location': 'drive',     # Exporting location ('drive', 'storage' or 'asset') 
    'spatial_scale': 30,        # Exporting spatial resolution
    'GCS_bucket': '',            # An unique bucket name on Google Cloud Storage
    'out_folder': '',            # the folder name for exporting
    'export_style': 'separate',
    'start_date': '',
    'stop_date':  ''}




def get_DefaultParams(): 
  return DefaultParams



############################################################################################################# 
# Description: Obtain a parameter dictionary for LEAF tool
#############################################################################################################
def get_LEAF_params(inParams):
  out_Params = modify_default_params(inParams)  # Modify default parameter dictionary with a given one
  out_Params['nbYears'] = -1         # Produce monthly products in most cases
  out_Params['unit']    = 2          # Always surface reflectance for LEAF production

  return out_Params  



#############################################################################################################
# Description: Obtain a parameter dictionary for Mosaic tool
#############################################################################################################
def get_mosaic_params(inParams):
  out_Params = modify_default_params(inParams)      # Modify default parameter dictionary with a given one
  out_Params['prod_names'] = ['mosaic']  # Of course, product name should be always 'mosaic'

  return out_Params  



#############################################################################################################
# Description: Obtain a parameter dictionary for land cover classification tool
#############################################################################################################
def get_LC_params(inParams):
  out_Params = modify_default_params(inParams)      # Modify default parameter dictionary with a given one
  out_Params['prod_names'] = ['mosaic']  # Of course, product name should be always 'mosaic'

  return out_Params 





#############################################################################################################
# Description: Obtain a parameter dictionary for land cover classification tool
#############################################################################################################
def LEAF_initial_func_Params(exe_Param_dict):
  fun_Param_dict = modify_default_params(exe_Param_dict)

  return fun_Param_dict



#############################################################################################################
# Description: This function modifies default parameter dictionary based on a given parameter dictionary.
# 
# Note:        The given parameetr dictionary does not have to include all "key:value" pairs, just only the
#              pairs need to be modified.
#
# Revision history:  2022-Mar-29  Lixin Sun  Initial creation
#
#############################################################################################################
def modify_default_params(inParams):  
  out_Params = DefaultParams

  # get the number of keys in the given dictionary
  inKeys = inParams.keys()  
  
  # For each key in the given dictionary, modify corresponding "key:value" pair
  for ikey in inKeys:
    out_Params[ikey] = inParams.get(ikey)

  # return modified parameter dictionary 
  return out_Params