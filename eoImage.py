import ee
import math
import eoAuxData as eoAD


UNKNOWN_sensor = 0
LS5_sensor     = 5
LS7_sensor     = 7
LS8_sensor     = 8
LS9_sensor     = 9
MAX_LS_CODE    = 20
ST2A_sensor    = 21
ST2B_sensor    = 22

S2_ssr_name    = 'S2'
L5_ssr_name    = 'LT05'
L7_ssr_name    = 'LE07'
L8_ssr_name    = 'LC08'
L9_ssr_name    = 'LC09'

DPB_band       = 0
BLU_band       = 1
GRN_band       = 2
RED_band       = 3
NIR_band       = 4
SW1_band       = 5
SW2_band       = 6
RED1_band      = 7
RED1_band      = 8
RED1_band      = 9
WV_band        = 10


TOA_ref        = 1
sur_ref        = 2


Img_Standard   = 1
Img_Fraction   = 2
Img_Regular    = 3


ST2_12_BANDS    = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
ST2_10_BANDS    = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']

# Regular output band names for Landsat data Collection 2
LS89_TOA_BANDS  = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']
LS89_SR_BANDS   = ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']

LS57_TOA_BANDS  = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7']
LS57_SR_BANDS   = ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']

# The names of the bands that are not heavily affected by aerosol
ST2_NoA_BANDS      = ['B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']
LS89_TOA_NoA_BANDS = ['B4', 'B5', 'B6', 'B7']
LS89_SR_NoA_BANDS  = ['SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']
LS57_TOA_NoA_BANDS = ['B3', 'B4', 'B5', 'B7']      
LS57_SR_NoA_BANDS  = ['SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']

STD_6_BANDS     = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']

pix_score       = 'pix_score'
pix_date        = 'date'
neg_blu_score   = 'neg_blu_score'
Texture_name    = 'texture'
mosaic_ssr_code = 'ssr_code'
PARAM_NDVI      = 'ndvi'

MONTH_NAMES     = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']



#############################################################################################################
# Description: This function returns a visulization parameter dictionary based on given SensorCode, DataUnit,
#              ImgType and MaxRef.
#             
# Revision history:  2021-May-20  Lixin Sun  Initial creation
#
#############################################################################################################
def mosaic_Vis(SensorCode, DataUnit, ImgType, MaxRef):
  '''Returns a visulization parameter dictionary based on given SensorCode, DataUnit, ImgType and MaxRef.
     Args:
       SensorCode(int): A given sensor type code (one of 5, 7, 8, 9, 101 or 102);
       DataUnit(int): A data unit code (1 or 2 for TOA and surface reflectance);
       ImgType(int): A image type code representing STD or fraction or regular image;
       MaxRef(int): A maximum reflectance value (normally 1 or 100).'''
  ssr_code  = int(SensorCode)
  data_unit = int(DataUnit)
  img_type  = int(ImgType)
  max_ref   = int(MaxRef)

  core_dict_1   = {'min': 0, 'max': 0.6, 'gamma': 1.8}
  core_dict_100 = {'min': 0, 'max': 60, 'gamma': 1.8}

  if img_type == Img_Standard: # For a standard image
    if max_ref < 10:
      core_dict_1['bands'] = ['nir', 'red', 'green']
      return core_dict_1
    else:
      core_dict_100['bands'] = ['nir', 'red', 'green']
      return core_dict_100
  
  if img_type == Img_Fraction: # For a fraction image
    if max_ref < 10:
      core_dict_1['bands'] = ['band_0', 'band_1', 'band_2']
      return core_dict_1
    else:
      core_dict_100['bands'] = ['band_0', 'band_1', 'band_2']
      return core_dict_100
  

  if ssr_code > MAX_LS_CODE or (ssr_code < MAX_LS_CODE and data_unit == 1):  # For Senstinel-2 or Landsat TOA reflectance image
    if max_ref < 10:
      core_dict_1['bands'] = ['B4', 'B3', 'B2']
      return core_dict_1
    else:
      core_dict_100['bands'] = ['B4', 'B3', 'B2']
      return core_dict_100
  
  elif ssr_code < MAX_LS_CODE and data_unit == 2:   # For a Landsat surface reflectance image
    if max_ref < 10:
      core_dict_1['bands'] = ['SR_B4', 'SR_B3', 'SR_B2']
      return core_dict_1
    else:
      core_dict_100['bands'] = ['SR_B4', 'SR_B3', 'SR_B2']
      return core_dict_100




###################################################################################################
# Description: Returns a GEE Data Catalog name corresponding to a given sensor and unit code
#             
# Revision history:  2021-May-20  Lixin Sun  Initial creation
#                    2022-Mar-23  Lixin Sun  Change Landsat data catalog from Collection 1 to 
#                                            Collection 2
###################################################################################################
def GEE_catalog_name(SensorCode, DataUnit):
  '''Returns a GEE Catalog name corresponding to given sensor name and data unit code.
     Args:
       inSensorCode: A given sensor type code (one of 5, 7, 8, 9, 101 or 102);
       inDataUnit: Data unit code (1 or 2 for TOA and surface reflectance). '''
  # Cast input parameters into python integer  
  ssr_code  = int(SensorCode)
  unit_code = int(DataUnit)

  # Determine GEE Dataa Catalog name based on sensor type and data unit codes
  if unit_code == 1:
    if ssr_code == LS5_sensor:
      return "LANDSAT/LT05/C02/T1_TOA"  
    elif ssr_code == LS7_sensor:
      return "LANDSAT/LE07/C02/T1_TOA"  
    elif ssr_code == LS8_sensor:
      return "LANDSAT/LC08/C02/T1_TOA"  
    elif ssr_code == LS9_sensor:
      return "LANDSAT/LC09/C02/T1_TOA" 
    else:
      return "COPERNICUS/S2"
  else:
    if ssr_code == LS5_sensor:
      return "LANDSAT/LT05/C02/T1_L2"  
    elif ssr_code == LS7_sensor:
      return "LANDSAT/LE07/C02/T1_L2"  
    elif ssr_code == LS8_sensor:
      return "LANDSAT/LC08/C02/T1_L2"  
    elif ssr_code == LS9_sensor:
      return "LANDSAT/LC09/C02/T1_L2"  
    else:
      return "COPERNICUS/S2_SR_HARMONIZED"




###################################################################################################
# Description: This function returns a dictionary containing the imaging angle names related to a
#              specified sensor type and data unit.
#
# Revision history:  2021-June-09  Lixin Sun  Initial creation
#
###################################################################################################
def get_property_names(SensorCode):
  '''Returns a dictionary containing property names related to a specified sensor type and data unit.

     Args:
        SensorCode(int): A sensor type code (one of 5, 7, 8, 9, 101 or 102);
        DataUnit(int): A data unit code (1 or 2). '''   
  ssr_code = int(SensorCode)
  
  if ssr_code > MAX_LS_CODE:
    return {"Cloudcover": 'CLOUDY_PIXEL_PERCENTAGE',
            "sza": 'MEAN_SOLAR_ZENITH_ANGLE',
            "vza": 'MEAN_INCIDENCE_ZENITH_ANGLE_B8A',
            "saa": 'MEAN_SOLAR_AZIMUTH_ANGLE', 
            "vaa": 'MEAN_INCIDENCE_AZIMUTH_ANGLE_B8A'  
           }
  elif ssr_code < MAX_LS_CODE:
    return {"Cloudcover": 'CLOUD_COVER',
            "sza": 'SUN_ELEVATION',
            "vza": 'SUN_ELEVATION',
            "saa": 'SUN_AZIMUTH', 
            "vaa": 'SUN_AZIMUTH'}

   



###################################################################################################
# Description: This function returns a cloud coverage percentage based on the given location and 
#              sensor type.
#
# Revision history:  2021-June-09  Lixin Sun  Initial creation
#
###################################################################################################
def get_cloud_rate(SensorCode, Polygon):
  '''Returns a cloud coverage percentage based on the given location and sensor type. 
     Args:
        inSensorCode: A sensor type code (one of 5, 7, 8, 9, 101 or 102);
        inPolygon(ee.Geometry): A geospatial region of ROI.'''
  ssr_code = ee.Number(SensorCode)
  polygon  = ee.Geometry(Polygon)
  
  # Determine the centre point of the given geographical region
  centre   = polygon.centroid()
  latitude = float(ee.Number(centre.coordinates().get(1)).getInfo())
  
  # Determine cloud coverage percentage based on sensor type and location
  ST2_rate = 90 if latitude < 50 else 80 if latitude < 60 else 60
  LS_rate  = ee.Algorithms.If(ssr_code.gt(4).And(ssr_code.lt(MAX_LS_CODE)), 90, 50)

  return ee.Algorithms.If(ssr_code.gt(MAX_LS_CODE), ST2_rate, LS_rate)




###################################################################################################
# Description: This function returns an image containing only SIX (blue, green, red, NIR, SWIR1 
#              and SWIR2) bands with pixel values rescaled to the range between 0.0 and 100.0.
#
# Revision history:  2021-May-10  Lixin Sun  Converted from Lixin's JavaScript code
#
###################################################################################################
def get_STD_image(image, ssr_code, data_unit):
  '''Returns an image containing SIX critical bands (blue, green, red, NIR, SWIR1 and SWIR2)
     with pixel values rescaled
     Args:
        image(ee.Image): A given image;
        ssr_code: A sensor type code (one of 5, 7, 8, 9, 101 or 102);
        data_unit: A data unit code (one of 1 or 2).'''
  # Obtain the names of raw SIX band 
  raw_6bands = get_raw_6BandNames(ssr_code, data_unit)
  
  return image.select(raw_6bands, STD_6_BANDS)




###################################################################################################
# Description: This function creates a standardized sensor name based on a given sensor code
#
# Revision history:  2021-May-10  Lixin Sun  Converted from Lixin's JavaScript code
#
###################################################################################################
def SensorCode2Name(SensorCode):
  '''Returns a standardized sensor name based on a given sensor code integer
  
     Args:
       ssr_code: The sensor type code (one of 5, 7, 8, 9, 101 or 102).'''
  ssr_code = int(SensorCode)

  if ssr_code > MAX_LS_CODE:
    return S2_ssr_name    
  elif ssr_code == LS8_sensor:
    return L8_ssr_name
  elif ssr_code == LS9_sensor:
    return L9_ssr_name  
  elif ssr_code == LS5_sensor:
    return L5_ssr_name
  elif ssr_code == LS7_sensor:
    return L7_ssr_name  
  else:
    return 'none'




###################################################################################################
# Description: This function returns a sensor code number based on a given sensor name string
# Note:        This function assumes the given "name_str" must be a Python string, instead of a
#              ee.String object.
#  
# Revision history:  2021-May-20  Lixin Sun  Initial creation
#
###################################################################################################
def SensorName2Code(name_str):
  '''Returns a sensor code integer based on a given sensor name string
  
     Args: 
       name_str (string): the name string of a sensor (not a ee.String object)'''
  sensor_name = str(name_str).lower()   # Covert to lowercase Python string 
  
  if sensor_name.find('s2') != -1 or sensor_name.find('st2') != -1 or sensor_name.find('sentin') != -1:
    return ST2A_sensor if sensor_name.find('2a') != -1 else ST2B_sensor
  elif sensor_name.find('l8')  != -1 or sensor_name.find('l08') != -1 or\
       sensor_name.find('lc8') != -1 or sensor_name.find('lc08') or\
       sensor_name.find('ls8') != -1 or sensor_name.find('ls08'):
    return LS8_sensor  
  elif sensor_name.find('l7')  != -1 or sensor_name.find('l07') != -1 or\
       sensor_name.find('le7') != -1 or sensor_name.find('le07') or\
       sensor_name.find('ls7') != -1 or sensor_name.find('ls07'):
    return LS7_sensor
  elif sensor_name.find('l5')  != -1 or sensor_name.find('l05') != -1 or\
       sensor_name.find('lt5') != -1 or sensor_name.find('lt05') or\
       sensor_name.find('ls5') != -1 or sensor_name.find('ls05'):
    return LS5_sensor
  elif sensor_name.find('l9')  != -1 or sensor_name.find('l09') != -1 or\
       sensor_name.find('lc9') != -1 or sensor_name.find('lc09') or\
       sensor_name.find('ls9') != -1 or sensor_name.find('ls09'):
    return LS9_sensor  
  else:
    return UNKNOWN_sensor   
 

 

###################################################################################################
# Description: This function can detect the sensor type code of a given ee.Image object.
#
# Note:        (1) The given image must have associated properties, which is not always the case
#              (2) "system:index" is a property shared by most satellite images 
#              (3) This function is not supposed to be invoked by a mapped function 
#
# Revision history:  2021-May-10  Lixin Sun  Converted from Lixin's JavaScript code
#
###################################################################################################
def get_SensorCode(inImage):
  '''Returns a sensor code integer corresponding to a given ee.Image object.
  
     Args:
       image (ee.Image): a ee.Image object with "system:index" property. '''

  image = ee.Image(inImage)

  sys_indx = image.getString('system:index').getInfo()  # Ensure "sys_indx" is a Python string
  
  if sys_indx.find('_T') > -1:
    S2_name  = image.getString('SPACECRAFT_NAME').getInfo()
    return SensorName2Code(S2_name)
  else:
    return SensorName2Code(sys_indx)




###################################################################################################
# Description: This function detects the data unit of a given ee.Image object.
#
# Note:        (1) The given image must have associated properties, which is not always the case
#              (2) This function is not supposed to be called by a mapped function 
#
# Revision history:  2021-May-10  Lixin Sun  Converted from Lixin's JavaScript code
#
###################################################################################################
def get_DataUnit(inImage):
  '''Returns a data unit integer of a given ee.Image object.
     Args:
       image(ee.Image): a ee.Image object with "system:index" property.'''

  ssr_code = get_SensorCode(inImage)  #Get sensor code number    
  image    = ee.Image(inImage)

  if ssr_code > MAX_LS_CODE:    
    S2_PROD_ID  = image.getString('PRODUCT_ID').getInfo()  #Get 'PRODUCT_ID' if it is a S2 image
    return TOA_ref if S2_PROD_ID.find('L1C') > -1 else sur_ref    
  else:
    nProperties = image.propertyNames().size().getInfo()  #Get the number of properties  
    return TOA_ref if nProperties > 50 else sur_ref




###################################################################################################
# Description: This function return a data unit name (TOA or BOA) according to a data unit code.
#
# Revision history:  2021-Jun-25  Lixin Sun  Initial creation
#
###################################################################################################
def DataUnit2Name(DataUnit):
  '''Returns a standardized sensor name based on a given sensor code integer
  
     Args:
       DataUnit: A data unit code (1 or 2).'''
  data_unit = int(DataUnit)

  return 'TOA' if data_unit == 1 else 'BOA'




###################################################################################################
# Description: This function returns rescaling factors for converting the pixel values of a given
#              image (either TOA or surface rflectance) to a range between 0 and 100.
#
# Note:        The gain and offset for diffrent sensors and different data units are gathered from
#              GEE Data Catalog and summarized as follows:
#
#    Sensor  |  TOA reflectance  |  surface reflectance | TOA reflectance  |  surface reflectance |
#            | out range [0,100] | out range [1,100]    | out range [0,1]  | out range [1,1]      | 
#  ------------------------------------------------------------------------------------------------
#   coeffs   |    gain  offset   |    gain     offset   |  gain  offset   |  gain      offset     |             
#   S2       |    0.01   +0      |    0.01       +0     | 0.0001   0.0    | 0.0001       0.0      | 
#   L9 coll2 |    100    +0      |    0.00275    -20    | 1.0      0.0    | 0.0000275   -0.2      |
#   L8 coll2 |    100    +0      |    0.00275    -20    | 1.0      0.0    | 0.0000275   -0.2      |
#   L7 coll2 |    100    +0      |    0.00275    -20    | 1.0      0.0    | 0.0000275   -0.2      |
#   L5 coll2 |    100    +0      |    0.00275    -20    | 1.0      0.0    | 0.0000275   -0.2      |
#  ------------------------------------------------------------------------------------------------
#
# Revision history:  2021-May-10  Lixin Sun  Converted from Lixin's JavaScript code
#                    2022-Mar-24  Lixin Sun  Renamed the function from "get_rescale" to 
#                                            "get_gain_offset" since Landsat Collection-2 data uses
#                                            gain/scale and offset, instead of just scale only. 
#                    2022-Mar-29  Lixin Sun  Add 'MaxRef' parameter so that different reflectance
#                                            output ranges ([0 to 1] or [0 to 100]) can be handled.  
###################################################################################################
def get_gain_offset(SensorCode, DataUnit, MaxRef):
  '''Returns a rescaling factor based on given sensor code and data unit.

     Args:        
        ssr_code: A sensor type code (one of 5, 7, 8, 9, 101 or 102);
        data_unit: A data unit code (one of 1 or 2);
        MaxRef: The maximum output reflectance value (1 or 100)''' 
  ssr_code  = int(SensorCode)
  data_unit = int(DataUnit)
  max_ref   = int(MaxRef)

  if ssr_code > MAX_LS_CODE:  # Sentinel-2 data
    return [0.01, 0.0] if max_ref > 10 else [0.0001, 0.0]
  elif ssr_code > 4 and ssr_code < 15:  # New gain and offset changed by Landsat Collection-2
    if data_unit == 1:
      return [100.0, 0.0] if max_ref > 10 else [1.0, 0.0]
    else:
      return [0.00275, -20.0] if max_ref > 10 else [0.0000275, -0.2]  
  else:
    return [1.0, 0.0]  





###################################################################################################
# Description: This function applys gain and offset to the optical bands of a given image.
#
# Revision history:  2022-Mar-24  Lixin Sun  Initial creation
#                    2022-Mar-28  Lixin Sun  Add 'MaxRef' parameter so that different reflectance
#                                            ranges ([0 to 1] or [0 to 100]) can be handled.  
###################################################################################################
def apply_gain_offset(Image, ssr_code, data_unit, MaxRef, all_bands):
  '''Returns a rescaling factor based on given sensor code and data unit.

     Args:        
       image(ee.Image): A given ee.Image object to which gain and offset will be applied  
       ssr_code: A sensor type code (one of 5, 7, 8, 9, 101 or 102);
       data_unit: A data unit code (one of 1 or 2);
       MaxREF: The maximum reflectance value (1 or 100);
       all_bands(Boolean): A flag indicating if apply gain and offset to all bands or not.''' 
  image = ee.Image(Image)
  
  gain_offset = get_gain_offset(ssr_code, data_unit, MaxRef)
  #print('<apply_gain_offset> Rescaling gain and offset = \n',gain_offset[0], gain_offset[1])
  
  if all_bands == True:
    return image.multiply(ee.Image(gain_offset[0])).add(ee.Image(gain_offset[1]))
  else:
    opti_bands = get_raw_OptiBandNames(ssr_code, data_unit)  # Get the names of all optical bands
    opti_img   = image.select(opti_bands)                    # Extract all optical bands from the given image
    opti_img   = opti_img.multiply(ee.Image(gain_offset[0])).add(ee.Image(gain_offset[1]))  # Apply gain and offset

    return image.addBands(opti_img, opti_bands, True)  # Put back the rescaled optical bands into original image





###################################################################################################
# Description: This function returns the footprint geometry of an image
#
# Revision history:  2020-Mar-24  Lixin Sun  Initial creation
#
###################################################################################################    
def ImgGeometry(image):
  '''Returns the footprint of a given image'''
  return ee.Geometry(image.get('system:footprint'))





###################################################################################################
# Description: This function returns the original band names of SIX important bands
#
# Note:        The "input" parameter could be an image object or a sensor code
#
# Revision history:  2021-May-10  Lixin Sun  Converted from Lixin's JavaScript code
#                    2022-Mar-28  Lixin Sun  Removed de definitions for SIX band name arraies
###################################################################################################
def get_raw_6BandNames(ssr_code, unit_code):
  '''Returns the raw names of SIX critical bands

     Args:        
        ssr_code: A sensor type code (one of 5, 7, 8, 9, 101 or 102).
        unit_code: A data unit type code.
  '''
  ssr_code  = int(ssr_code)
  unit_code = int(unit_code)  
                      
  if ssr_code > MAX_LS_CODE:
    blu = ST2_10_BANDS[0]
    grn = ST2_10_BANDS[1]
    red = ST2_10_BANDS[2]
    nir = ST2_10_BANDS[6]
    sw1 = ST2_10_BANDS[8]
    sw2 = ST2_10_BANDS[9]
    return [blu, grn, red, nir, sw1, sw2]
  elif ssr_code == LS8_sensor or ssr_code == LS9_sensor:
    if unit_code == 1:
      blu = LS89_TOA_BANDS[1]
      grn = LS89_TOA_BANDS[2]
      red = LS89_TOA_BANDS[3]
      nir = LS89_TOA_BANDS[4]
      sw1 = LS89_TOA_BANDS[5]
      sw2 = LS89_TOA_BANDS[6]
      return [blu, grn, red, nir, sw1, sw2]
    else:  
      blu = LS89_SR_BANDS[1]
      grn = LS89_SR_BANDS[2]
      red = LS89_SR_BANDS[3]
      nir = LS89_SR_BANDS[4]
      sw1 = LS89_SR_BANDS[5]
      sw2 = LS89_SR_BANDS[6]
      return [blu, grn, red, nir, sw1, sw2]
  elif ssr_code == LS5_sensor or ssr_code == LS7_sensor:
    return LS57_TOA_BANDS if unit_code == 1 else LS57_SR_BANDS
  else:
    return []         




###################################################################################################
# Description: This function can be used to obtain the original names of optical bands
#
# Revision history:  2021-May-10  Lixin Sun  Converted from Lixin's JavaScript code
#
###################################################################################################
def get_raw_OptiBandNames(ssr_code, unit_code):
  '''Returns the raw names of all the optical bands of a sensor

     Args:        
       ssr_code: A sensor type code (one of 5, 7, 8, 9, 101 or 102).
       unit_code: A data unit type code.
  '''  
  ssr_code  = int(ssr_code)
  unit_code = int(unit_code)

  if ssr_code > MAX_LS_CODE:
    return ST2_12_BANDS
  elif ssr_code == LS8_sensor or ssr_code == LS9_sensor:
    return LS89_TOA_BANDS if unit_code == 1 else LS89_SR_BANDS
  elif ssr_code == LS5_sensor or ssr_code == LS7_sensor:
    return LS57_TOA_BANDS if unit_code == 1 else LS57_SR_BANDS
  else:
    return []    
  



###################################################################################################
# Description: This function can be used to obtain the band names for regular output
#
# Revision history:  2021-Oct-04  Lixin Sun  Initial creation
#
###################################################################################################
def get_out_BandNames(ssr_code, unit_code):
  '''Returns the raw names of all the optical bands of a sensor

     Args:        
        ssr_code(Integer): A sensor type code (one of 5, 7, 8, 9, 101 or 102);
        unit_code(Integer): A data unit code (1 or 2)
  '''  
  ssr_code  = int(ssr_code)
  unit_code = int(unit_code)

  if ssr_code > MAX_LS_CODE:
    return ST2_10_BANDS
  elif ssr_code == LS8_sensor or ssr_code == LS9_sensor:
    return LS89_TOA_BANDS if unit_code == 1 else LS89_SR_BANDS 
  elif ssr_code == LS5_sensor or ssr_code == LS7_sensor:
    return LS57_TOA_BANDS if unit_code == 1 else LS57_SR_BANDS 
  else:
    return []    
  



###################################################################################################
# Description: This function can be used to obtain the names of the bands that are not heavily 
#              affected by aerosol
#
# Revision history:  2022-Jun-10  Lixin Sun  Initial creation
#
###################################################################################################
def get_NoA_BandNames(ssr_code, unit_code):
  '''Returns the names of the bands that are not heavily affected by aerosol

     Args:        
        ssr_code(Integer): A sensor type code (one of 5, 7, 8, 9, 101 or 102);
        unit_code(Integer): A data unit code (1 or 2)
  '''  
  ssr_code  = int(ssr_code)
  unit_code = int(unit_code)

  if ssr_code > MAX_LS_CODE:
    return ST2_NoA_BANDS
  elif ssr_code == LS8_sensor or ssr_code == LS9_sensor:
    return LS89_TOA_NoA_BANDS if unit_code == 1 else LS89_SR_NoA_BANDS 
  elif ssr_code == LS5_sensor or ssr_code == LS7_sensor:
    return LS57_TOA_NoA_BANDS if unit_code == 1 else LS57_SR_NoA_BANDS 
  else:
    return []    




###################################################################################################
# Description: This function can be used to obtain the RGB band names 
#
# Revision history:  2022-Jun-20  Lixin Sun  Initial creation
#
###################################################################################################
def get_RGB_BandNames(ssr_code, unit_code):
  '''Returns RGB band names

     Args:        
        ssr_code(Integer): A sensor type code (one of 5, 7, 8, 9, 101 or 102);
        unit_code(Integer): A data unit code (1 or 2). '''  
  ssr_code  = int(ssr_code)
  unit_code = int(unit_code)

  if ssr_code > MAX_LS_CODE:
    return ST2_10_BANDS[:3]
  elif ssr_code == LS8_sensor or ssr_code == LS9_sensor:
    return LS89_TOA_BANDS[1:4] if unit_code == 1 else LS89_SR_BANDS[1:4] 
  elif ssr_code == LS5_sensor or ssr_code == LS7_sensor:
    return LS57_TOA_BANDS[:3] if unit_code == 1 else LS57_SR_BANDS[:3] 
  else:
    return []    




###################################################################################################
# Description: This function returns a list of standard band names to be used in a classification
#
# Revision history:  2021-Jun-30  Lixin Sun  Initial creation
###################################################################################################
def get_STD_classf_bands():
  return ['green', 'red', 'nir', 'swir1', 'swir2', eoAD.NightLight_name, eoAD.RoadDensity_name]




###################################################################################################
# Description: This function returns the original band names of a specified band
#
# All defined band codes are listed as follows:
#  DPB_band  = 0
#  BLU_band  = 1
#  GRN_band  = 2
#  RED_band  = 3
#  NIR_band  = 4
#  SW1_band  = 5
#  SW2_band  = 6
#  RED1_band = 7
#  RED1_band = 8
#  RED1_band = 9
#  WV_band   = 10
#
# Revision history:  2021-May-10  Lixin Sun  Converted from Lixin's JavaScript code
#
###################################################################################################
def get_BandName(BandCode, SensorCode, DataUnit):
  '''Returns an original band name based on a specified "BandCode"
     Args:        
        band_code: An integer representing a band number
        ssr_code: A sensor type code (one of 5, 7, 8, 9, 101 or 102);
        data_unit: A data unit code (one of 1 or 2).''' 
  band_code = int(BandCode)        
  ssr_code  = int(SensorCode)
  data_unit = int(DataUnit)

  if ssr_code > MAX_LS_CODE:
    if band_code >= 0 and band_code < 4: 
      return ST2_12_BANDS[band_code]
    elif band_code == 4:
      return ST2_12_BANDS[7]
    elif band_code == 5 or band_code == 6:
      return ST2_12_BANDS[band_code + 5]
    elif band_code >=7  or band_code <= 9:
      return ST2_12_BANDS[band_code - 3] 
    elif band_code == 10:
      return ST2_12_BANDS[9]
  elif ssr_code == LS8_sensor or ssr_code == LS9_sensor:
    if band_code >= 0 and band_code < 7:
      return LS89_TOA_BANDS[band_code] if data_unit == 1 else LS89_SR_BANDS[band_code]
  elif ssr_code == LS5_sensor or ssr_code == LS7_sensor:
    if band_code > 0 and band_code < 7:
      return LS57_TOA_BANDS[band_code - 1] if data_unit == 1 else LS57_SR_BANDS[band_code - 1]
  else:
    return ''





###################################################################################################
# Description: This function attaches a date band to the given ee.Image object.
#
# Revision history:  2020-Juy-10  Lixin Sun  Initial creation
#                    2021-May-10  Lixin Sun  Converted from Lixin's JavaScript code
#
###################################################################################################
def attach_Date(image):
  '''Attaches an image acquisition date band to a given image
  Args:
    image(ee.Image): A given ee.Image object.
  '''
  date     = ee.Date(image.date()).millis().divide(31536000)
  date_img = ee.Image.constant(date).rename(pix_date).toUint16()
  return image.addBands(date_img)



###################################################################################################
# Description: This function adds three angle bands to a satellite SURFACE reflectance image
#
# Note:        This function is mainly used by LEAF tool
#  
# Revision history:  2021-May-19  Lixin Sun  Initial creation
#                    2021-May-10  Lixin Sun  Converted from Lixin's JavaScript code
#                    2022_Jun-22  Lixin Sun  Removed scaling factor
###################################################################################################
def attach_AngleBands(Image, SensorCode):
  '''Attaches three angle bands to a satallite SURFACE REFLECTANCE image
  Args:
    ssr_code: A sensor type code (one of 5, 7, 8, 9, 101 or 102);
    image(ee.Image): A given Sentinel-2 surface reflectance image.'''  
  ssr_code = int(SensorCode)
  Property = get_property_names(ssr_code)
  rad      = ee.Number(math.pi/180.0)  

  if ssr_code > MAX_LS_CODE:
    vza_rad = ee.Image(Image.metadata(Property['vza']).multiply(rad))    
  else:
    vza_rad = ee.Image(0.0)

  sza_rad = ee.Image(Image.metadata(Property['sza']).multiply(rad))
  raa_rad = ee.Image(Image.metadata(Property['saa']).subtract(Image.metadata(Property['vaa'])).multiply(rad))

  return (Image.addBands(vza_rad.cos().rename(['cosVZA'])) \
               .addBands(sza_rad.cos().rename(['cosSZA'])) \
               .addBands(raa_rad.cos().rename(['cosRAA'])))





###################################################################################################
# Description: This function attach a NDVI band to a given image.
#  
# Revision history:  2022-Aug-10  Lixin Sun  Initial creation
#
###################################################################################################
def attach_NDVIBand(Image, SensorCode, DataUnit):
  '''Attaches three angle bands to a satallite SURFACE REFLECTANCE image
  Args:
    Image(ee.Image): A given Satellite image
    SensorCode(int): A sensor type code (one of 5, 7, 8, 9, 21 or 22);
    DataUnit(int): A data unit type code (1 or 2).'''  
  ssr_code  = int(SensorCode)
  data_unit = int(DataUnit)

  gain_offset = get_gain_offset(ssr_code, data_unit, 100)  
  STD_img     = get_STD_image(Image, ssr_code, data_unit)
  
  red = STD_img.select('red').multiply(ee.Image(gain_offset[0])).add(ee.Image(gain_offset[1]))
  nir = STD_img.select('nir').multiply(ee.Image(gain_offset[0])).add(ee.Image(gain_offset[1]))
    
  ndvi  = nir.subtract(red).divide(nir.add(red)).rename(PARAM_NDVI)
  return Image.addBands(ndvi)





def get_MonthName(month_numb):
  month = int(month_numb)

  if month > 0 and month < 13:
    return MONTH_NAMES[month-1]
  else:
    return 'Mone'





###################################################################################################
# Description: This function normalizes the spectral values with the sum of corresponding spectrum. 
#
# Revision history:  2022-Jun-10  Lixin Sun  Initial creation
#
###################################################################################################
def normalize_pixValues(Image, ValScale):
  '''Attaches three angle bands to a satallite SURFACE REFLECTANCE image
  Args:
    Image(ee.Image): A given ee.Image object;
    ValScale(float): A given value scaling factor to be applied to normalized values.'''
  # Cast the input parameters to right type
  image = ee.Image(Image)
  scale = float(ValScale)
  
  img_sum = image.reduce(ee.Reducer.sum()) 
 
  return image.divide(img_sum).multiply(ee.Image(scale))
 





###################################################################################################
# Description: This function creates a spectral angle map based on two given ee.Image objects
#              covering the same ground area. 
#
# Revision history:  2022-Jun-10  Lixin Sun  Initial creation
#
###################################################################################################
def CVA_SAM(Image1, Image2, ValScale):
  '''Attaches three angle bands to a satallite SURFACE REFLECTANCE image
  Args:
    Image1(ee.Image): The first given ee.Image object;
    Image2(ee.Image): The second given ee.Image object;
    ValScale(float): A given value scaling factor to be applied to normalized values.'''
  # Cast the input parameters to right type
  image1 = ee.Image(Image1)
  image2 = ee.Image(Image2)
  scale  = float(ValScale)

  #Conduct pixel value normalization if "scale" is greater than 1
  if scale > 1:
    image1 = normalize_pixValues(image1, scale)
    image2 = normalize_pixValues(image2, scale)
  
  #Calculate numerate and denominator of spectral angle formula
  numerate     = image1.multiply(image2).reduce(ee.Reducer.sum()) 
  
  denominator1 = image1.multiply(image1).reduce(ee.Reducer.sum())
  denominator2 = image2.multiply(image2).reduce(ee.Reducer.sum())
  denominator  = denominator1.multiply(denominator2).sqrt()
  
  #Create spectral angle map
  SAM_map =  numerate.divide(denominator).acos()

  return SAM_map.where(SAM_map.lt(ee.Image(0.35)), ee.Image(0))





###################################################################################################
# Description: This function can be used to create a HOT image based SWIR2 and BLUE bands
#
# Note:        This function assumes the pixel values are 100 times of reflectance. e.g., for 12.34
#              reflectance is represented by 1234.
#
# Revision history:  2020-Jun-15  Lixin Sun  Initial creation
#                    2021-May-10  Lixin Sun  Converted from Lixin's JavaScript code
#
###################################################################################################
def SB_HOT_map(img):
  blu      = img.select('blue')
  sw2      = img.select('swir2')
  zero_img = ee.Image(0.0)

  HOT_map = blu.subtract(sw2.multiply(ee.Image(0.1)).add(ee.Image(800.0)))
  HOT_map = HOT_map.where(HOT_map.lt(zero_img), zero_img)

  return HOT_map





###################################################################################################
# Description: This function returns a superpixel ee.Image object corresponding to the give image
#
# Revision history:  2022-Apr-01  Lixin Sun  Initial creation
#
###################################################################################################
def superpixel_img(inImage): 
  all_bands = inImage.bandNames().getInfo()

  seg_mosaic = ee.Algorithms.Image.Segmentation.SNIC(inImage, 3, 0.01, 8, 10)
  
  seg_bands = []
  for band in all_bands:
    seg_bands.append(band + '_mean')

  return seg_mosaic.select(seg_bands, all_bands)




  

#############################################################################################################
# Description: This function manages a list of exporting tasks
#
# Revision history:  2022-Feb-10  Lixin Sun  Initial creation 
#
#############################################################################################################
def manage_tasks(manage_type, filter):
  '''This function manages a list of exporting tasks.
     Args:
       manage_type(string): a string representing a task type, such as 'status' or 'cancel';
       filter(string): a string for filtering task names. '''
  #==========================================================================================================
  # Get a list of exporting tasks
  #==========================================================================================================  
  task_list = ee.data.listOperations()

  if manage_type.find('status') > -1:
    for task in task_list:
      if task['metadata']['description'].find(filter) > -1: 
        print(task['metadata']['description']+': ' + task['metadata']['state'])
    
  elif manage_type.find('cancel') > -1:
    for task in task_list:
      if task['metadata']['description'].find(filter) > -1:         
        ee.data.cancelOperation(task['name'])
        print(task['metadata']['description'] + ' has been cancelled.')
    
  elif manage_type.find('list') > -1:  
    print('<manage_tasks> the list of all exporting tasks:', ee.data.listOperations())
  
  elif manage_type.find('count') > -1:
    print('<manage_tasks> the number of tasks = ', len(task_list))

  elif manage_type.find('meta') > -1:
    for task in task_list:
      if task['metadata']['description'].find(filter) > -1: 
        print(task['metadata'])
