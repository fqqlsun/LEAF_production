######################################################################################################
# Description: The functions in this file can be used to facilitate the usage of some Auxiliary data
#              available in GEE. 
#
######################################################################################################
import ee 

import eoTileGrids as eoTG


NightLight_name  = 'night_light'
RoadDensity_name = 'road_density'




######################################################################################################
# Description: This function creates a global night-light mosaic image for a targeted year. 
#
# Revision history:  2021-May-06  Lixin Sun  Initial creation
#
######################################################################################################
def get_GlobNLight(target_year, Smooth, Radius):
  '''Create a global night-light mosaic image for a targeted year.
  Arg:
    target_year(string or int): A targeted year of mosaicing;
    Smooth(Boolean): A flag indicating if do smoothing to noght light map;
    inRadius(float): The radius of smoothing if applicable.'''
  year_int     = int(target_year)
  year_str     = str(target_year)
  night_lights = ee.Image(0.0)
  
  # Create a global night lights map 
  if year_int > 1991:
    start = year_str + '-01-01'
    stop  = year_str + '-12-30'
    if year_int >= 2014:
      dataset      = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG').filter(ee.Filter.date(start, stop))
      night_lights = dataset.mosaic().select(['avg_rad'], [NightLight_name]) 
    else:  
      dataset = ee.ImageCollection('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS').filter(ee.Filter.date(start, stop))
      night_lights = dataset.mosaic().select(['stable_lights'], [NightLight_name]) 
  else:
    dataset = ee.ImageCollection('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS').filter(ee.Filter.date('1992-01-01', '1992-12-30'))
    night_lights = dataset.mosaic().select(['stable_lights'], [NightLight_name])
  
  #==================================================================================================
  # Smooth the night light map as required
  #==================================================================================================
  if Smooth == True:
    kernel = ee.Kernel.circle(radius = Radius, units = 'pixels', normalize = True)
    night_lights = night_lights.convolve(kernel)
    
  return night_lights





#############################################################################################################
# Description: This function returns a road density mosaic image from an image collection stored on
#              GEE assets.
#
# Revision history:  2021-Jun-30  Lixin Sun  Initial creation
#                    2022-Feb-04  Lixin Sun  Removed road density filtering process.
#############################################################################################################
def get_roadDensity(region):
  '''Creates a road density mosaic image from an image collection stored on GEE assets and filter
     it with a urban area mask. 

     Args:
       region(ee.Geometry): The spatial region of ROI. '''
  CAN_road_density = ee.ImageCollection('users/ORS_code/Canada_road_density')

  #==================================================================================================
  # Give a band name to each road density tile so that they can be mosaiced  
  #==================================================================================================
  def select_road(img):
    return img.select([0], [RoadDensity_name])

  density_ImgColl = CAN_road_density.map(lambda img: select_road(img))
  
  #==================================================================================================
  # Conduct quality mosaic and then clip it with a given region
  #==================================================================================================
  return density_ImgColl.qualityMosaic(RoadDensity_name).clip(region)




#############################################################################################################
# Description: This function returns a proper land cover mosaic based on a given region and year.
# 
# Revision history:  2022-Jul-05  Lixin Sun  Initial creation
#                    2022-Sep-29  Lixin Sun  Fixed the issues related to the urban areas in CCRS 2020 LC map
#                    2023-Jan-10  Lixin Sun  Added "IsBiome" option, which determines if a biome map should 
#                                            be returned.
#############################################################################################################  
def get_GlobLC(Region, Year, IsBiome):
  '''Returns a proper land cover mosaic based on a given region and year.

     Args:
       Region(ee.Geometry): A spatial region defining the location of the mosaic;
       Year(int or string): The target year;
       IsBiome(Boolean): Flag indicating if a biome map will be returned.'''
  #==========================================================================================================
  # Choose a proper land cover image collection based on a given "Year"
  #==========================================================================================================
  year = int(Year)  
  ccrs_LC_assets = 'users/rfernand387/NA_NALCMS_2015_tiles'

  if year > 2017:
    ccrs_LC_assets = 'projects/ccmeo-ag-000007/assets/CanLC2020'
    ccrs_urban_map = ee.ImageCollection('projects/ccmeo-ag-000007/assets/Urban_Map_2020').mosaic()
    #ccrs_LC_assets = 'users/lsunott/CanLC2020'
    #ccrs_urban_map = ee.ImageCollection('users/lsunott/Urban2020').mosaic()

  print('\n<get_LC_map> Used LC map is: ', ccrs_LC_assets) 
  #==========================================================================================================
  # Create a CCRS land cover mosaic image
  #==========================================================================================================
  new_name = 'partirion'
  ccrs_LC = ee.ImageCollection(ccrs_LC_assets) \
              .map(lambda image: image.rename(new_name)) \
              .mosaic()

  if year > 2017:
    ccrs_LC = ccrs_LC.where(ccrs_urban_map.gt(0), ee.Image(17))

  ccrs_LC = ccrs_LC.selfMask()  # updateMask(mask)   # update mask for CCRS land cover mosaic

  #==========================================================================================================
  # Create Global land cover image collection
  #==========================================================================================================
  def remap_classIDs(Image):
    img = Image.select("discrete_classification").uint8()

    img = img.remap([0,20,30,40,50,60,70,80,90,100,111,112,113,114,115,116,121,122,123,124,125,126,200], \
                    [0,8, 10,15,17,16,19,18,14,13, 1,  3,  1,  5,  6,  6,  2,  4,  2,  5,  6,  6,  18], 0)
    
    return img.rename(new_name)
  
  #==========================================================================================================
  # The given "Region" might already be expended from original region, but here it is necesary to reexpend it
  # so that it can completely cover reprojected output result.    
  #==========================================================================================================
  region    = eoTG.expandSquare(Region, 0.2)
  global_LC = ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V/Global") \
                .filterBounds(region) \
                .map(lambda image: remap_classIDs(image)) \
                .mosaic()
  
  out_map = ccrs_LC.unmask(global_LC).clip(region)   # merge two land cover maps together and then clip it
  
  if IsBiome == True:
    out_map = out_map.remap([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19], [0,7,7,5,6,6,7,2,2,1,1,2,1,9,2,3,9,10,0,0])
  
  return out_map



#############################################################################################################
# Description: This function returns a specified global DEM mosaic.
# 
# Revision history:  2022-Aug-25  Lixin Sun  Initial creation
#
#############################################################################################################  
def get_GlobDEM(DEM_name):
  '''Returns a DEM covering a specified region.

     Args:
       DEM_name(string): A given DEM name string.'''

  glo30 = ee.ImageCollection("projects/sat-io/open-datasets/GLO-30").mosaic()



#############################################################################################################
# Description: This function returns a global tree and building height map.
# 
# Revision history:  2022-Aug-25  Lixin Sun  Initial creation
#
#############################################################################################################  
def get_GlobHeight():
  '''Returns a DEM covering a specified region.

     Args:'''

  glodem30 = ee.ImageCollection("projects/sat-io/open-datasets/GLO-30").mosaic()
  fabdem30 = ee.ImageCollection("projects/sat-io/open-datasets/FABDEM").mosaic()
  
  return glodem30.subtract(fabdem30)





#############################################################################################################
# Description: This function returns a global water mosaic.
# 
# Note: There is another global water map (called JRC Global Surface Water Mapping) in GEE. However it seems 
#       that JRC and forest change water maps are highly consistent.      
#
# Revision history:  2022-Aug-25  Lixin Sun  Initial creation
#                    2022_Aug-20  Lixin Sun  Using updated (2021_V1_9) global forest change map 
#                    2022-Sep-23  Lixin Sun  Ensure 1 and 0 represent water and land for every pixel, 
#                                            including the masked pixels in gfc2019 map
#    
#############################################################################################################  
def get_GlobWater():
  '''Returns a global water mosaic.
     Args: '''

  #gfc2019 = ee.Image('UMD/hansen/global_forest_change_2019_v1_7')
  gfc2021 = ee.Image("UMD/hansen/global_forest_change_2021_v1_9")

  return gfc2021.select('datamask').selfMask().unmask().neq(1)