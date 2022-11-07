import ee
from matplotlib.animation import ImageMagickBase

import eoImage as eoImg
import eoImgMask as eoIM
import eoTileGrids as eoTG
import eoParams
import eoMosaic
import eoAuxData as eoAD



#############################################################################################################
# Description: Functions is for reading parameters for creating the ANNs applicable to Sentinel-2 data 
# 
# Revision history:  2021-May-17  Lixin Sun  Copied from the Richard's Python code
#                    2022-Jan-17  Lixin Sun  Added more feature collections for diverse land covers. 
#############################################################################################################
def s2_createFeatureCollection_estimates(version_nb):
    if version_nb == 0:
      return ee.FeatureCollection ('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1')  
      #return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_dbf_big_NNT1_Single_0_1') 
    else:
      return  ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1') \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_dbf_big_clumped_NNT1_Single_0_1_v2')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_enf_big_clumped_NNT1_Single_0_1_v2')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_dbf_big_clumped_NNT1_Single_0_1_v2')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_mix_big_clumped_NNT1_Single_0_1_v2'))   


def s2_createFeatureCollection_errors(version_nb):
    if version_nb == 0:
      return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error')
    else:
      return   ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error') \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_dbf_big_clumped_NNT1_Single_0_1_v2_errors')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_enf_big_clumped_NNT1_Single_0_1_v2_errors')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_dbf_big_clumped_NNT1_Single_0_1_v2_errors')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_mix_big_clumped_NNT1_Single_0_1_v2_errors'))


def s2_createFeatureCollection_domains(version_nb):
    if version_nb == 0:
      return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')
     #return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_DOMAIN')
    else:
      return   ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN') \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN'))


def s2_createFeatureCollection_range(version_nb):
    if version_nb == 0:
      return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')
    else:
      return   ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE') \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')) 

    
def s2_createFeatureCollection_Network_Ind():
  return ee.FeatureCollection('users/rfernand387/Parameter_file_prosail_ccrs_big_clumped2')

'''
def createImageCollection_partition():  
  return ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V/Global") \
           .map(lambda image: image.select("discrete_classification") \
           .remap([0,20,30,40,50,60,70,80,90,100,111,112,113,114,115,116,121,122,123,124,125,126,200],[0,8,10,15,17,16,19,18,14,13,1,3,1,5,6,6,2,4,2,5,6,6,18],0).uint8().rename("partition")) \
           .merge(ee.ImageCollection('users/rfernand387/NA_NALCMS_2015_tiles') \
           .map(lambda image: image.select("b1").rename("partition")))
'''

def s2_createFeatureCollection_legend():
    #return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/Legend_sl2p')
    return ee.FeatureCollection('users/rfernand387/Legend_prosail_ccrs_big_clumped')


#############################################################################################################
# Description: Functions for reading parameters for creating ANNs applicable to Landsat-8 data 
# 
# Revision history:  2021-May-17  Lixin Sun  Copied from the Richard's Python code in Jupyter Notebook
# 
#############################################################################################################
def l8_createFeatureCollection_estimates():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/LANDSAT_LC08_C01_T1_SR_SL2P_OUTPUT')    
    
def l8_createFeatureCollection_errors():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/LANDSAT_LC08_C01_T1_SR_SL2P_ERRORS')

def l8_createFeatureCollection_domains():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/LANDSAT_LC08_C01_T1_SR_DOMAIN')    

def l8_createFeatureCollection_range():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/LANDSAT_LC08_C01_T1_SR_RANGE')
    
def l8_createFeatureCollection_Network_Ind():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/Parameter_file_sl2p')

#def l8_createImageCollection_partition():
#    return ee.ImageCollection('users/rfernand387/NA_NALCMS_2015_tiles') \
#             .map(lambda image: image.select("b1").rename("partition")) \
#             .merge(ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V/Global") \
#             .map(lambda image: image.select("discrete_classification") \
#             .remap([0,20,30,40,50,60,70,80,90,100,111,112,113,114,115,116,121,122,123,124,125,126,200],[0,8,10,15,17,16,19,18,14,13,1,3,1,5,6,6,2,4,2,5,6,6,18],0).uint8().rename("partition")))

def l8_createFeatureCollection_legend():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/Legend_sl2p')

   



#############################################################################################################
# Description: Constant dictionaries for storing parameters related to different image collections and 
#              different visualization/exporting options. 
# 
# Revision history:  2021-May-17  Lixin Sun  Copied from the Richard's Python code in Jupyter Notebook
#                    2022-Mar-28  Lixin Sun  Removed "inputScaling" key and its corresponding list object.
#                                            The rescaling factors will be obtained through calling
#                                            "apply_gain_offset" function. 
#############################################################################################################  
VERSION_NB = 1

COLL_OPTIONS = {
    'COPERNICUS/S2_SR_HARMONIZED': {
      "name": 'S2',
      "description": 'Sentinel 2A',      
      "Watercover": 'WATER_PERCENTAGE',
      "VIS_OPTIONS": 'VIS_OPTIONS',
      "Collection_SL2P":       ee.FeatureCollection(s2_createFeatureCollection_estimates(VERSION_NB)),      
      "Collection_SL2Perrors": ee.FeatureCollection(s2_createFeatureCollection_errors(VERSION_NB)),  
      "sl2pDomain":            ee.FeatureCollection(s2_createFeatureCollection_domains(VERSION_NB)),
      "Network_Ind":           ee.FeatureCollection(s2_createFeatureCollection_Network_Ind()),
      "legend":                ee.FeatureCollection(s2_createFeatureCollection_legend()),
      "numVariables": 7,
      "inputBands":   ['cosVZA','cosSZA','cosRAA','B3','B4', 'B5', 'B6', 'B7', 'B8A','B11','B12'],
    },
    'LANDSAT/LC08/C02/T1_L2': {
      "name": 'L8',
      "description": 'LANDSAT 8',      
      "Watercover": 'CLOUD_COVER',      
      "VIS_OPTIONS": 'VIS_OPTIONS',
      "Collection_SL2P":       ee.FeatureCollection(l8_createFeatureCollection_estimates()),
      "Collection_SL2Perrors": ee.FeatureCollection(l8_createFeatureCollection_errors()),
      "sl2pDomain":            ee.FeatureCollection(l8_createFeatureCollection_domains()),
      "Network_Ind":           ee.FeatureCollection(l8_createFeatureCollection_Network_Ind()),
      "legend":                ee.FeatureCollection(l8_createFeatureCollection_legend()),
      "numVariables": 7,
      "inputBands":   ['cosVZA','cosSZA','cosRAA', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'],
    }
}



PROD_OPTIONS = {
    "Surface_Reflectance": {
        "Name": 'Surface_Reflectance',
        "description": 'Surface_Reflectance',
        "inp":      [ 'B4', 'B5', 'B6', 'B7', 'B8A','B9','B11','B12']        
    },
    "Albedo": {
        "Name": 'Albedo',
        "errorName": 'errorAlbedo',
        "maskName": 'maskAlbedo',
        "description": 'Black sky albedo',
        "variable": 6,           
        "outmin": 0,  #(ee.Image(ee.Array([[0]]))),
        "outmax": 1  #(ee.Image(ee.Array([[1]])))
    },
    'fAPAR': {
        "Name":      'fAPAR',
        "errorName": 'errorfAPAR',
        "maskName":   'maskfAPAR',
        "description": 'Fraction of absorbed photosynthetically active radiation',
        "variable": 2,
        "outmin": 0 ,  #(ee.Image(ee.Array([[0]]))),
        "outmax": 1  #(ee.Image(ee.Array([[1]])))
    },
    'fCOVER': {
        "Name": 'fCOVER',
        "errorName": 'errorfCOVER',
        "maskName": 'maskfCOVER',
        "description": 'Fraction of canopy cover',
        "variable": 3,
        "outmin": 0,  #(ee.Image(ee.Array([[0]]))),
        "outmax": 1  #(ee.Image(ee.Array([[1]])))
    },
    'LAI': {
        "Name":        'LAI',
        "errorName":   'errorLAI',
        "maskName":    'maskLAI',
        "description": 'Leaf area index',
        "variable": 1,
        "outmin": 0,  #(ee.Image(ee.Array([[0]]))),
        "outmax": 15  #(ee.Image(ee.Array([[1]])))
    },
    'CCC': {
        "Name": 'CCC',
        "errorName": 'errorCCC',
        "maskName": 'maskCCC',
        "description": 'Canopy chlorophyll content',
        "variable": 1,
        "outmin": (ee.Image(ee.Array([[0]]))),
        "outmax": (ee.Image(ee.Array([[1000]])))
    },
    'CWC': {
        "Name": 'CWC',
        "errorName": 'errorCWC',
        "maskName": 'maskCWC',
        "description": 'Canopy water content',
        "variable": 1,
        "outmin": (ee.Image(ee.Array([[0]]))),
        "outmax": (ee.Image(ee.Array([[100]])))
    },
    'DASF': {
        "Name": 'DASF',
        "errorName": 'errorDASF',
        "maskName": 'maskDASF',
        "description": 'Directional area scattering factor',
        "variable": 1,
        "outmin": (ee.Image(ee.Array([[0]]))),
        "outmax": (ee.Image(ee.Array([[1]])))
    }
}





#############################################################################################################
# Description: Returns a single band image named "networkID" to map teh networks to be applied according to
#              a land cover map. 
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [162])
#                    2022-Jan-27  Updated to ensure this function works for both LEAF V0 (one network for
#                                 all land cover classes) and V1 (diverse networks for diffrent land covers).
#############################################################################################################
def makeIndexLayer(partition, numb_classes, legend, network_IDs):
    '''Returns a single band image named "networkID" to map teh networks to be applied according to
       a land cover map. 
       Args: 
         inPartition(ee.image): a land cover classification map;
         nbClsNets(ee.Number): the number of networks corresponding to one biophysical parameter;
         inLegend(ee.FeatureCollection): a feature collection containing class legends;
         inNetwork_Id(ee.FeatureCollection): a feature collection containing networkIDs. '''
    partition  = ee.Image(partition)               # land cover classification map
    classes    = ee.Number(numb_classes)           # the number of networks for one biophysical parameter (one or multiple)
    legend     = ee.FeatureCollection(legend)      # legend to convert class ID numbers to networks
    Network_Id = ee.FeatureCollection(network_IDs) # legend to convert networks to networkIDs
    
    #print('\n\n<makeIndexLayer> legend collection = ', legend.getInfo())
    #print('<makeIndexLayer> network ID collection = ', Network_Id.getInfo())
    #========================================================================================================
    # get a list of all valid class IDs
    #========================================================================================================
    legend_list = legend.toList(legend.size())
    lc_IDs      = legend_list.map(lambda feature: ee.Feature(feature).getNumber('Value'))
    
    print('\n\n<makeIndexLayer> land cover IDs = ', lc_IDs.getInfo())
    #========================================================================================================
    # get network indices corresponding to the class IDs
    #========================================================================================================
    print('<makeIndexLayer> numb of valid classes = ', classes.getInfo())
    if classes.getInfo() == 1:  # the case of LEAF V0
      nbClsIDs   = lc_IDs.size().getInfo()
      networkIDs = ee.List([0]*nbClsIDs)
      print('<makeIndexLayer> LEAF V0 network IDs = ', networkIDs.getInfo())
    else:  # the case of LEAF V1
      networkIDs = legend_list.map(lambda feature: ee.Feature(feature).get('SL2P Network')) \
                              .map(lambda propertyValue: ee.Feature(Network_Id.first()).toDictionary().getNumber(propertyValue))
      print('<makeIndexLayer> LEAF V1 network IDs = ', networkIDs.getInfo())

    #========================================================================================================
    # return a mapped network index map and name it as 'networkID'
    #========================================================================================================
    return partition.remap(lc_IDs, networkIDs, 0).rename('networkID')
    


    
#############################################################################################################
# Description: Extract a coefficient from "netData" based on the "index" value.
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [163])
# 
#############################################################################################################
def getCoefs(netData, index) :
  '''Extract a coefficient from "netData" based on the "index" value.
     Args:
     netData(ee.Feature): a ee.Feature object containing all coefficients;
     index(int): the index of an identified coefficient in "netData". '''
  col_name = ee.String('tabledata').cat(ee.Number(index).int().format())

  return (ee.Feature(netData)).getNumber(col_name)



#############################################################################################################
# Description: Convert a LEAF network from a ee.Feature object to a ee.Dictionary object with eight keys 
#              (“inpSlope”, “inpOffset”, “h1wt”, “h1bi”, “h2wt”, “h2bi”, “outSlope”, “outBias”).
#
# Note:  We assume a two-hidden-layer network with tansig functions but allow for variable nodes per layer
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [164])
#
#############################################################################################################
def FNet_to_DNet(feature_list, class_ID):
    '''Convert a LEAF network from a ee.Feature object to a ee.Dictionary object with eight keys
       (“inpSlope”, “inpOffset”, “h1wt”, “h1bi”, “h2wt”, “h2bi”, “outSlope”, “outBias”).
       Args:
         feature_list(ee.List): A list of network features (ee.Features) for one vegetation parameter;
         class_ID(ee.Number): A land cover class number/ID. '''
    cls_features = ee.List(feature_list)  # a list of networks (in ee.Feature format) for one vegetation parameter
    cls_ID       = ee.Number(class_ID)     
    
    #extract a LEAF network (ee.Feature object) from the "feature_list" based on class ID
    netData = ee.Feature(cls_features.get(cls_ID.subtract(1)))

    # initialize the created network dictionary
    net = {}
    
    # input slope (11 values)
    num   = ee.Number(6)
    start = num.add(1)
    end   = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["inpSlope"] = ee.List.sequence(start, end).map(lambda indx: getCoefs(netData, indx))
    
    # input offset (11 values)
    num   = end.add(1)
    start = num.add(1)
    end   = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["inpOffset"] = ee.List.sequence(start, end).map(lambda indx: getCoefs(netData, indx))

    # hidden layer 1 weight (55 values = 11 x 5) 
    num   = end.add(1)
    start = num.add(1)
    end   = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["h1wt"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(netData,indx))

    # hidden layer 1 bias (5 values)
    num   = end.add(1)
    start = num.add(1)
    end   = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["h1bi"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(netData,indx))

    # hidden layer 2 weight (5 values)
    num   = end.add(1)
    start = num.add(1)
    end   = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["h2wt"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(netData,indx))
  
    # hidden layer 2 bias (1 value)
    num   = end.add(1)
    start = num.add(1)
    end   = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["h2bi"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(netData,indx))

    # output slope (1 value)
    num   = end.add(1)
    start = num.add(1)
    end   = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["outSlope"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(netData,indx))
  
    # output offset (1 value)
    num   = end.add(1)
    start = num.add(1)
    end   = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["outBias"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(netData, indx))
    
    return(ee.Dictionary(net))




#############################################################################################################
# Description: Returns a list of LEAF networks (with ee.Dictionary objects as elements) for one biophysical
#              parameter and multiple land cover types. 
#              
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [165])
#
#############################################################################################################
def make_DNet_arr(all_nets, numClasses, ParamID):
    '''Returns a array of LEAF networks (with ee.Dictionary objects as elements) corresponding to one 
       biophysical parameter and multiple land cover types.
       Args:
         all_nets(ee.FeatureCollection): a collection of LEAF networks (with ee.Feature as elements) for
                                         different biophysical parameters and land covers; 
         numClasses(ee.Number): the total number of land cover types (1 or 11);
         ParamID(ee.Number): the ID number of a vegetation parameter (e.g., 1 for 'LAI'). '''
    all_nets   = ee.FeatureCollection(all_nets)  #A network matrix for different bio-parameters and land covers; 
    numClasses = ee.Number(numClasses)           #The total number of land cover types
    ParamID    = ee.Number(ParamID)              #The ID number of a vegetation parameter

    #extract a list of network features for one biophysical parameter and different land cover types  
    filtered_features = ee.FeatureCollection(all_nets.filter(ee.Filter.eq('tabledata3', ParamID))).toList(numClasses)
    
    # Return a list of network (in ee.Dictionary format) for different land cover types
    return ee.List.sequence(1, numClasses).map(lambda ClsID: FNet_to_DNet(filtered_features, ClsID))
    



#############################################################################################################
# Description: Applies a specified (defined by 'inNetIndex') two-layer neural network to a subset of land
#              covers and returns a single band image containing results.
#
# Note:        This function applys gain and offset to convert the image values to reflectance value range 
#              between 0 and 1 (instead of 100)
#
# Revision history:  2021-May-17              Copied from Richard's Python notebook (In [167])
#                    2021-May-27  Lixin Sun   Reviewed and added comments
#                    2022-Jan-27  Lixin Sun   Merged 'selectNet' function to 'applyNet'. The reason of 
#                                             doing this is to apply a spatial mask to resultant image
#                                             (see 'return' statment). 
#                    2022-Mar-28  Lixin Sun   Updated to use "apply_gain_offset" for image value conversion.
#                    2022-Jun-17  Lixin Sun   Removed gain/offset application to outside of this function.
#                                             So the reflectance value range in the given mosaic image must
#                                             be from 0 to 1.  
#############################################################################################################
def applyNet(inImage, net_list, band_names, net_indx, output_name):
    '''Applies a specified (defined by 'inNetIndex') two-layer neural network to a subset of land covers.
       Args: 
         inImage(ee.Image): a ee.Image object with network index band (named 'networkID') attached;
         inNetList():       a list of networks for one parameter and various land cover types;
         inBandNames(ee.List):  a list of band names to be used in parameter extraction;              
         inNetIndex(ee.Number): an index number to a land cover;
         ssr_code(int): a sensor type code (current: 5, 7, 8, 9 or 101)
         inOutputName(string): the name string of output band. '''
    image      = ee.Image(inImage)         # a mosaic image with a "networkID" band image attached 
    netList    = ee.List(net_list)         # a list of all available LEAF networks
    bandNames  = ee.List(band_names)       # [cosCZA,cosVZA,cosRAA,B3,B4,B5,B6,B7,B8,B11 and B12] for Sentinel2
    netIndex   = ee.Number(net_indx).int() # the index number of a specified LEAF network   
    outputName = ee.String(output_name)    # the name of the band containing output results

    #========================================================================================================
    # Mask unselected land cover areas and then rescale selected band images
    #========================================================================================================
    mask     = image.select('networkID').eq(netIndex)
    used_img = image.select(bandNames).updateMask(mask)
    
    # Select the network corresponding to a land cover type
    used_net = ee.Dictionary(netList.get(netIndex))    

    #========================================================================================================
    # Obtain the image and network objects separately from the given ee.Dictionay object, which is returned
    # from "selectNet" function
    #========================================================================================================
    #inSlope = used_net.toArray(ee.List(['inpSlope', 'inpOffset']), 0).transpose()

    # Input layer scaling and offsetting   
    inGain  = ee.Image(used_net.toArray(ee.List(['inpSlope']), 0).transpose()).arrayProject([0]).arrayFlatten([used_img.bandNames()])
    inBias  = ee.Image(used_net.toArray(ee.List(['inpOffset']),0).transpose()).arrayProject([0]).arrayFlatten([used_img.bandNames()])
    l1inp2D = used_img.multiply(inGain).add(inBias)
    
    # Hidden layers    
    # "l12D" is a 2D iamge/matrix with 4 bands ('h1w1','h1w2','h1w3','h1w4','h1w5')
    l12D = ee.Image(used_net.toArray(ee.List(['h1wt']), 0).reshape([ee.List(used_net.get('h1bi')).length(), ee.List(used_net.get('inpOffset')).length()])) \
              .matrixMultiply(l1inp2D.toArray().toArray(1)) \
              .add(ee.Image(used_net.toArray(ee.List(['h1bi']),0).transpose())) \
              .arrayProject([0]).arrayFlatten([['h1w1','h1w2','h1w3','h1w4','h1w5']])
    
    # apply tansig 2/(1+exp(-2*n))-1. "l2inp2D" is a 2D image with 5 bands ('h1w1','h1w2','h1w3','h1w4','h1w5')
    l2inp2D = ee.Image(2).divide(ee.Image(1).add((ee.Image(-2).multiply(l12D)).exp())).subtract(ee.Image(1))

    # purlin hidden layers. "l22D" is a 2D image with only one band ('h2bi')
    l22D = l2inp2D.multiply(ee.Image(used_net.toArray(ee.List(['h2wt']),0).transpose()) \
                              .arrayProject([0]).arrayFlatten([['h2w1','h2w2','h2w3','h2w4','h2w5']])) \
                              .reduce('sum') \
                              .add(ee.Image(used_net.toArray(ee.List(['h2bi']),0))) \
                              .arrayProject([0]).arrayFlatten([['h2bi']])
    
    # Output layer scaling and offsetting 
    outGain    = ee.Image(ee.Number(used_net.get('outSlope')))
    outBias    = ee.Image(ee.Number(used_net.get('outBias')))    
    outputBand = l22D.subtract(outBias).divide(outGain).rename(outputName)     
    
    # Return resultant output
    return outputBand.multiply(mask)

 


#############################################################################################################
# Description: Applies a set of shallow networks to an image based on a given land cover map of the same 
#              region and returns image (ee.Image object) containing three bands, a biophysical parameter 
#              map, a land cover map and a network index map. 
#
# Note:        The reflectance value range of the given mosaic image (inImage) must be within 0 and 1.
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [168])
#
#############################################################################################################
def wrapperNNets(networks, partition, prod_options, coll_options, suffix_name, inImage) :
    '''Applies a set of shallow networks to an image based on a given land cover map.
       Args: 
         network(ee.List): a 2d matrix of networks (ee.Dictionary objects);
         partition(ee.Image): a partition/classification map;
         prod_options(ee.Dictionary): a dictionary containing the info related to a selected parameter type;
         coll_options(ee.Dictionary): a dictionary containing the info related to a selected satellite type;
         suffix_name(string): a suffix name of output;
         inImage(ee.Image): a mosaic image for vegetation parameter extraction. '''
    #========================================================================================================
    # typecast function parameters 
    # Note that the dictionaries in this function are all ee.Dictionary objects, rather than regular Python
    # dictionary. So the items cannot be accessed through subscription (e.g., dictionary.['key']).
    #========================================================================================================     
    networks    = ee.List(networks)            # a 2D matrix of networks with rows and columns for parameters and land covers
    partition   = ee.Image(partition)          # a land cove classification map
    ProdOptions = ee.Dictionary(prod_options)  # ee.Dictionary related to a selected parameter type
    CollOptions = ee.Dictionary(coll_options)  # ee.Dictionary related to a selected satellite type
    image       = ee.Image(inImage)            # a given (mosaic) image cube
    
    #========================================================================================================
    # Determine a row in the network matrix based on a selected biophysical parameter type (the value 
    # associated with 'variable' key in product dictionary/PROD_OPTIONS)
    # Note: several networks should be associated with one parameter to account for different land covers
    #========================================================================================================
    netList   = ee.List(networks.get(ee.Number(ProdOptions.get('variable')).subtract(1))); 
    nbClsNets = netList.size()    

    #========================================================================================================
    # Attach a network index band to the given (mosaic) image cube
    #========================================================================================================
    net_indx_map = makeIndexLayer(partition, nbClsNets, CollOptions.get('legend'), CollOptions.get('Network_Ind'))
    used_image   = image.addBands(net_indx_map)

    #========================================================================================================
    # Apply each network in 'netList' to its corresponding land cover separately and then merge the results
    # to one image by calling 'max()' function.
    #========================================================================================================
    #ssr_code   = eoImg.SensorName2Code(CollOptions.getString('name')) 
    outName    = ee.String(suffix_name).cat(ProdOptions.getString('Name'))
    band_names = CollOptions.get('inputBands')
    
    return ee.ImageCollection(ee.List.sequence(0, nbClsNets.subtract(1)) \
             .map(lambda netIndex: applyNet(used_image, netList, band_names, netIndex, outName))) \
             .max()
             #.addBands(partition)  #.addBands(net_indx_map)





#############################################################################################################
# Description: Determine if inputs fall in domain of algorithm. Need to be updated to allow for the domain
#              to vary with partition
#
# Note: (1) The reflectance value range of the given mosaic image must be within 0 and 1.
#       (2) The reflectance value ranges for snow detection and QC_img are different 
#  
# Revision history:  2021-Oct-18  Copied from Richard's Python notebook (In [161])
#
#############################################################################################################
def invalidInput(sl2pDomain, bandList, Mosaic, SensorCode, DataUnit) :
  '''Determine if inputs fall in the domain of the algorithm.
     Args: 
       sl2pDomain(ee.FeatureCollection): a feature collection storing value domains;
       bandList(ee.List): the band list (imaging angles and spectral bands) to be used in LEAF production;
       mosaic(ee.Image): a given mosaic image with gain and offset applied;
       SensorCode(int): an integer indicating the sensor type (LS5, 7, 8, 9 or S2);
       DataUnit(int): an integer indicating data type (TOA or surface reflectance).'''
  ssr_code   = int(SensorCode)
  data_unit  = int(DataUnit) 
  sl2pDomain = ee.FeatureCollection(sl2pDomain).aggregate_array("DomainCode").sort()
  bandList   = ee.List(bandList)  # ['cosVZA','cosSZA','cosRAA', other spectral band names]
  image      = ee.Image(Mosaic)   #Note: the pixel values of this mosaic must be within 0 and 1 
  
  #==========================================================================================================
  # Create a snow mask and later on add it into QC band
  # Note: The value range required for snow detection is from 0 to 100 and the value range of the given
  #       mosaic image is from 0 to 1. 
  #==========================================================================================================
  STD_img   = eoImg.get_STD_image(image, ssr_code, data_unit).multiply(ee.Image(100.0))
  snow_mask = eoIM.STD_Img_SnowMask(STD_img).uint8()

  #==========================================================================================================
  # Code image bands into a single band and compare to valid codes to make QC band
  # Note: (1) the value range required by QC image creation is from 0 to 1;
  #       (2) the imaging angle bands are not involved in the generation of QC image.
  #==========================================================================================================  
  LEAF_image = image.select(bandList.slice(3))  #Only select required spectral bands without imaging angle bands
  nBands     = bandList.slice(3).length()       

  QC_img = LEAF_image.multiply(ee.Image.constant(ee.Number(10))).ceil().mod(ee.Number(10))\
                     .multiply(ee.Image.constant(ee.List.sequence(0, nBands.subtract(1)).map(lambda value: ee.Number(10).pow(ee.Number(value))))) \
                     .reduce("sum").remap(sl2pDomain, ee.List.repeat(0, sl2pDomain.length()), 1).uint8()
  
  QC_img = QC_img.multiply(ee.Image(2)).bitwiseOr(snow_mask)

  return image.addBands(QC_img.rename("QC"))





#############################################################################################################
# Description: This function creates a QC band image for a LEAF product.
#
# Revision history:  2022-Jun-24  Lixin Sun  Initial creation
#
#############################################################################################################
def LEAF_QCImage(Mosaic, Estimate, sl2pDomain, prod_dict, bandList, SensorCode, DataUnit):
  '''This function creates a QC band image for a LEAF product.
     
    Args:
      Mosaic(ee.Image): a given mosaic image with the value ranges of the spectral bands are all between 0 and 1;
      Estimate(ee.Image): an estimated parameter image; 
      sl2pDomain(ee.FeatureCollection): a feature collection storing value domains;
      prod_dict({}): a dictionary corresponding to a particaluar product;
      bandList(ee.List): the band list (imaging angles and spectral bands) to be used in LEAF production;
      SensorCode(int): an integer indicating the sensor type (LS5, 7, 8, 9 or S2);
      DataUnit(int): an integer indicating data type (TOA or surface reflectance).'''
  #==========================================================================================================
  # Cast input parameters into correct types
  #==========================================================================================================  
  ssr_code   = int(SensorCode)
  data_unit  = int(DataUnit) 
  sl2pDomain = ee.FeatureCollection(sl2pDomain).aggregate_array("DomainCode").sort()
  bandList   = ee.List(bandList)  # ['cosVZA','cosSZA','cosRAA' and other spectral band names]
  image      = ee.Image(Mosaic)  #Note: the pixel values of this mosaic must be within 0 and 1 

  #==========================================================================================================
  # Create a QC image and set the flag for input out of range in the first bit of the image 
  # Note: (1) the value range required by QC image creation is from 0 to 1;
  #       (2) the imaging angle bands are not involved in the generation of QC image.
  #==========================================================================================================  
  LEAF_image = image.select(bandList.slice(3))  #Only select required spectral bands
  nBands     = bandList.slice(3).length()       

  QC_img = LEAF_image.multiply(ee.Image.constant(ee.Number(10))).ceil().mod(ee.Number(10))\
                     .multiply(ee.Image.constant(ee.List.sequence(0, nBands.subtract(1)).map(lambda value: ee.Number(10).pow(ee.Number(value))))) \
                     .reduce("sum").remap(sl2pDomain, ee.List.repeat(0, sl2pDomain.length()), 1).uint8()

  #==========================================================================================================
  # Set flags/marks in the 2nd bit of QC_img for the pixels with out-of-range estimated values 
  #==========================================================================================================
  min_img = ee.Image(prod_dict.get('outmin'))
  max_img = ee.Image(prod_dict.get('outmax'))
  range_mask = Estimate.lt(min_img).Or(Estimate.gt(max_img)).multiply(ee.Image(2)).uint8()

  QC_img  = QC_img.bitwiseOr(range_mask)

  #==========================================================================================================
  # Set flags/marks in the 3rd bit of QC_img for all invalid pixels (cloud, shadow, snow, ice, water,
  # saturated or out of range) 
  #==========================================================================================================
  invalid_mask = LEAF_valid_mask(Mosaic, ssr_code, data_unit).multiply(ee.Image(4)).uint8()

  QC_img = QC_img.bitwiseOr(invalid_mask)

  #==========================================================================================================
  # Set mosaic sensor code in the bits higher than 3 in the case of Landsat data has been used. 
  #==========================================================================================================
  if ssr_code < eoImg.MAX_LS_CODE:  # For Landsat imagery
    ssr_code_band = Mosaic.select([eoImg.mosaic_ssr_code]).multiply(ee.Image(8)).uint8()    
    #return ssr_code_band
    return QC_img.bitwiseOr(ssr_code_band)
  else:  # For Sentinel-2 imagery
    ssr_code_band = Mosaic.select([0]).multiply(ee.Image(0)).add(ee.Image(eoImg.ST2A_sensor)).multiply(ee.Image(8)).uint8()
    return QC_img.bitwiseOr(ssr_code_band)




def LEAF_QCImage_test(Mosaic, bandList, SensorCode, DataUnit):
  '''This function creates a QC band image for a LEAF product.
     
    Args:
      Mosaic(ee.Image): a given mosaic image with the value ranges of the spectral bands are all between 0 and 1;
      Estimate(ee.Image): an estimated parameter image; 
      sl2pDomain(ee.FeatureCollection): a feature collection storing value domains;
      prod_dict({}): a dictionary corresponding to a particaluar product;
      bandList(ee.List): the band list (imaging angles and spectral bands) to be used in LEAF production;
      SensorCode(int): an integer indicating the sensor type (LS5, 7, 8, 9 or S2);
      DataUnit(int): an integer indicating data type (TOA or surface reflectance).'''
  #==========================================================================================================
  # Cast input parameters into correct types
  #==========================================================================================================  
  ssr_code   = int(SensorCode)
  data_unit  = int(DataUnit) 
  bandList   = ee.List(bandList)  # ['cosVZA','cosSZA','cosRAA' and other spectral band names]
  image      = ee.Image(Mosaic).unmask()   #Note: the pixel values of this mosaic must be within 0 and 1 

  #==========================================================================================================
  # Set flags/marks in the 3rd bit of QC_img for all invalid pixels (cloud, shadow, snow, ice, water,
  # saturated or out of range) 
  #==========================================================================================================
  QC_img = LEAF_valid_mask(image, ssr_code, data_unit).multiply(ee.Image(4)).uint8()
  
  print('\n\n<LEAF_QCImage_test> QC_img info = ',QC_img.getInfo())
  #==========================================================================================================
  # Set mosaic sensor code in the bits higher than 3 in the case of Landsat data has been used. 
  #==========================================================================================================
  if ssr_code < eoImg.MAX_LS_CODE:  # For Landsat imagery
    ssr_code_band = Mosaic.select([eoImg.mosaic_ssr_code]).multiply(ee.Image(8)).uint8()    
    return QC_img.bitwiseOr(ssr_code_band) 
  else:  # For Sentinel-2 imagery
    ssr_code_band = Mosaic.select([0]).multiply(ee.Image(0)).add(ee.Image(eoImg.ST2A_sensor)).multiply(ee.Image(8)).uint8()
    return QC_img.bitwiseOr(ssr_code_band) 




#############################################################################################################
# Description: Exports two maps, a estimated biophysical parameter map and uncertainty map, to a specified
#              location (Google Drive or Google Cloud Storage). The filenames of the exported images will be
#              automatically generated based on tile name, image acquisition time, parameter type and spatial
#              resolution of the product.
#
# Revision history:  2021-Oct-18  Lixin Sun  Initial creation 
#                    2022-Oct-27  Lixin Sun  Revised so that 
#############################################################################################################
def export_products(fun_Param_dict, region, estimateImage, errorImage, QCImage, ExportCode, task_list):
  '''Exports one set of LEAF products to either Google Drive or Google Cloud Storage
     Args:
       fun_Param_dict(dictionary): a dictionary storing other required running parameters;
       region(ee.Geometry): the spatial region of interest;
       estimateImage(ee.Image): an estimated biophysical parameter map;
       errorImage(ee.Image): the uncertainty map corresponding to the estimated biophysical parameter map; 
       QCImage(ee.Image): The QC image to be exported;
       ExportCode(int): An integer code indicating which image needs to be exported;
       task_list([]): a list storing the links to exporting tasks. '''
  #==========================================================================================================
  # Create the names of exporting folder anf files 
  #==========================================================================================================
  month        = int(fun_Param_dict['month'])
  year_str     = str(fun_Param_dict['year'])   
  tile_str     = str(fun_Param_dict['tile_name'])
  scale_str    = str(fun_Param_dict['resolution'])
  given_folder = str(fun_Param_dict['folder'])
  PROD_name    = str(fun_Param_dict['prod_name'])

  form_folder  = tile_str + '_' + year_str

  exportFolder = form_folder if len(given_folder) < 2 else given_folder  
  month_name   = eoImg.get_MonthName(month)

  if month < 1 or month > 12:
    estimate_filePrefix  = form_folder + '_' + str(PROD_name) + '_' + scale_str + 'm'
    uncertain_filePrefix = form_folder + '_error' + str(PROD_name) + '_' + scale_str + 'm'
    QC_filePrefix        = form_folder + '_' + str(PROD_name) + '_QC_' + scale_str + 'm'
  else:
    estimate_filePrefix  = form_folder + '_' + month_name + '_' + str(PROD_name) + '_' + scale_str + 'm'
    uncertain_filePrefix = form_folder + '_' + month_name + '_error' + str(PROD_name) + '_' + scale_str + 'm'
    QC_filePrefix        = form_folder + '_' + month_name + '_' + str(PROD_name) + '_QC_' + scale_str + 'm'

  #==========================================================================================================
  # Prepare initial export dictionary and output location 
  #==========================================================================================================
  out_location = str(fun_Param_dict['location']).lower()
  
  export_dict = {'scale': int(fun_Param_dict['resolution']),
                 'crs': 'EPSG:3979',
                 'maxPixels': 1e11,
                 'region': region}

  #==========================================================================================================
  # Export an estimated LEAF parameter map to either GD or GCS
  #==========================================================================================================
  if ExportCode == 0 or ExportCode == 1:
    export_dict['image']          = estimateImage
    export_dict['description']    = estimate_filePrefix
    export_dict['fileNamePrefix'] = estimate_filePrefix
  
    if out_location.find('drive') > -1:
      export_dict['folder'] = exportFolder
      task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())
    elif out_location.find('storage') > -1:
      export_dict['bucket'] = str(fun_Param_dict['bucket'])
      export_dict['fileNamePrefix'] = exportFolder + '/' + estimate_filePrefix
      task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())

  #==========================================================================================================
  # Export an uncertainty map to either GD or GCS
  #==========================================================================================================
  if ExportCode == 0 or ExportCode == 2:
    export_dict['image']          = errorImage
    export_dict['description']    = uncertain_filePrefix
    export_dict['fileNamePrefix'] = uncertain_filePrefix
 
    if out_location.find('drive') > -1:
      export_dict['folder'] = exportFolder
      task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())    
    elif out_location.find('storage') > -1:
      export_dict['bucket'] = str(fun_Param_dict['bucket'])
      export_dict['fileNamePrefix'] = exportFolder + '/' + uncertain_filePrefix
      task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())  

  #==========================================================================================================
  # Export an QC map to either GD or GCS
  #==========================================================================================================
  if ExportCode == 0 or ExportCode == 3:
    export_dict['image']          = QCImage
    export_dict['description']    = QC_filePrefix
    export_dict['fileNamePrefix'] = QC_filePrefix
 
    if out_location.find('drive') > -1:
      export_dict['folder'] = exportFolder
      task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())
    elif out_location.find('storage') > -1:
      export_dict['bucket'] = str(fun_Param_dict['bucket'])
      export_dict['fileNamePrefix'] = exportFolder + '/' + QC_filePrefix
      task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())





#############################################################################################################
# Description: Exports three ancillary maps(QC, Date and partition) associated withfun_Param_dict one set of LEAF products
#
# Note: If month value is outside of range (1 to 12), then a peak season product will be created.
#
# Revision history:  2021-Oct-18  Lixin Sun  Initial creation 
#                    2022-Jun-20  Lixin Sun  Added capability for exporting RGB bands. This is necessary for
#                                            debugging purpose.  
#############################################################################################################
def export_partition(mosaic, fun_Param_dict, region, exportClass, exportDate, export_RGB, task_list):
  '''Exports three ancillary maps associated with one set of LEAF products
  Args:
    mosaic(ee.Image): a given mosaic image, which includes "Date" and "QC" bands;
    fun_Param_dict({}): a dictionary storing other required running parameters;
    mapBounds(ee.Geometry): the spatial boundary used in LEAF production;
    export_RGB(Boolean): a flag indicating if to export RGB mosaic images;
    task_list([]): a list for storing the links to exporting tasks.'''
  #==========================================================================================================
  # Create the names of exporting folder and files 
  #==========================================================================================================
  month        = int(fun_Param_dict['month']) 
  year_str     = str(fun_Param_dict['year'])
  tile_str     = str(fun_Param_dict['tile_name'])
  scale_str    = str(fun_Param_dict['resolution'])
  given_folder = str(fun_Param_dict['folder'])

  form_folder  = tile_str + '_' + year_str
  exportFolder = form_folder if len(given_folder) < 2 else given_folder  

  if month >= 1 or month <= 12:
    filePrefix = form_folder + '_' + eoImg.get_MonthName(month)

  #==========================================================================================================
  # Generate partition map (The partition map for Sentinel-2 and Landsat imagery should be the same)
  #==========================================================================================================
  partition = eoAD.get_GlobLC(region, int(year_str))
  #CollName  = eoImg.GEE_catalog_name(fun_Param_dict['sensor'], eoImg.sur_ref)  
  #partition = (COLL_OPTIONS[CollName]["partition"]).filterBounds(region).mosaic().rename('partition')

  #==========================================================================================================
  # Export ancillary maps associated with LEAF products 
  #==========================================================================================================
  out_location = str(fun_Param_dict['location']).lower()

  export_dict = {'scale': fun_Param_dict['resolution'],
                 'crs': 'EPSG:3979',
                 'maxPixels': 1e11,
                 'region': region}
  
  if out_location.find('drive') > -1:
    print('<export_ancillaries> Exporting to Google Drive......')  
    # Export 'partitiion' map to Google Drive
    export_dict['folder']         = exportFolder

    export_dict['image']          = partition
    export_dict['description']    = filePrefix + '_Partition_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = filePrefix + '_Partition_' + scale_str + 'm'   

    task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())

  elif out_location.find('storage') > -1:
    print('<export_ancillaries> Exporting to Google Cloud Storage......')  
    export_dict['bucket']         = str(fun_Param_dict['bucket'])

    # Export 'partition' map to Google Cloud Storage
    export_dict['image']          = partition
    export_dict['description']    = filePrefix + '_Partition_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = exportFolder + '/' + export_dict['description']

    task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start()) 
   
  if export_RGB == True:
    print('<export_ancillaries> function param = ', fun_Param_dict)
    RGB_names = eoImg.get_RGB_BandNames(int(fun_Param_dict['sensor']), eoImg.sur_ref)
    
    if out_location.find('drive') > -1:
      export_dict['folder']         = exportFolder

      scale_img = ee.Image(10000) 
      export_dict['image']          = mosaic.select([RGB_names[0]]).multiply(scale_img).toUint16()
      export_dict['description']    = filePrefix + '_blu_' + scale_str + 'm'
      export_dict['fileNamePrefix'] = filePrefix + '_blu_' + scale_str + 'm'

      task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())

      export_dict['image']          = mosaic.select([RGB_names[1]]).multiply(scale_img).toUint16()
      export_dict['description']    = filePrefix + '_grn_' + scale_str + 'm'
      export_dict['fileNamePrefix'] = filePrefix + '_grn_' + scale_str + 'm'
      
      task_list.append(ee.batch.Export.image.toDrive(**export_dict).start() )
      
      export_dict['image']          = mosaic.select([RGB_names[2]]).multiply(scale_img).toUint16()
      export_dict['description']    = filePrefix + '_red_' + scale_str + 'm'
      export_dict['fileNamePrefix'] = filePrefix + '_red_' + scale_str + 'm'
      
      task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())

    elif out_location.find('storage') > -1:
      print('<export_ancillaries> Exporting to Google Cloud Storage......')  
      export_dict['bucket'] = str(fun_Param_dict['bucket'])

      # Export 'partition' map to Google Cloud Storage
      export_dict['image']          = mosaic.select([RGB_names[0]]).multiply(scale_img).toUint16()
      export_dict['description']    = filePrefix + '_blu_' + scale_str + 'm'
      export_dict['fileNamePrefix'] = exportFolder + '/' + export_dict['description']
      
      task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())

      export_dict['image']          = mosaic.select([RGB_names[1]]).multiply(scale_img).toUint16()
      export_dict['description']    = filePrefix + '_grn_' + scale_str + 'm'
      export_dict['fileNamePrefix'] = exportFolder + '/' + export_dict['description']
      
      task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())

      export_dict['image']          = mosaic.select([RGB_names[2]]).multiply(scale_img).toUint16()
      export_dict['description']    = filePrefix + '_red_' + scale_str + 'm'
      export_dict['fileNamePrefix'] = exportFolder + '/' + export_dict['description']
      
      task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())





#############################################################################################################
# Description: Exports partition image associated with one tile to either GD or GCS
#
# Revision history:  2021-Oct-18  Lixin Sun  Initial creation 
#                    2022-Oct-27  Lixin Sun  This function was separated from "export_ancillaries", which
#                                            does not exist anymore. 
#############################################################################################################
def export_ClassImg(fun_Param_dict, region, task_list):
  '''Exports partition image to one of optional storages
  Args:
    fun_Param_dict({}): a dictionary storing other required running parameters;
    mapBounds(ee.Geometry): the spatial boundary used in LEAF production;
    task_list([]): a list for storing the links to exporting tasks.'''
  #==========================================================================================================
  # Create the names of exporting folder and files 
  #==========================================================================================================
  year_str     = str(fun_Param_dict['year'])
  tile_str     = str(fun_Param_dict['tile_name'])
  scale_str    = str(fun_Param_dict['resolution'])
  given_folder = str(fun_Param_dict['folder']) 
  
  #==========================================================================================================
  # Export ancillary maps associated with LEAF products 
  #==========================================================================================================
  form_folder  = tile_str + '_' + year_str
  exportFolder = form_folder if len(given_folder) < 2 else given_folder
  out_location = str(fun_Param_dict['location']).lower()

  export_dict = {'scale': fun_Param_dict['resolution'],
                 'crs': 'EPSG:3979',
                 'maxPixels': 1e11,
                 'region': region}
  
  partition = eoAD.get_GlobLC(region, int(year_str)).uint8()

  if out_location.find('drive') > -1:
    print('<export_ClassImg> Exporting pratition to Google Drive......')  
    export_dict['folder']         = exportFolder
    export_dict['image']          = partition
    export_dict['description']    = form_folder + '_Partition_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = form_folder + '_Partition_' + scale_str + 'm'   

    task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())  

  elif out_location.find('storage') > -1:
    print('<export_ClassImg> Exporting partition to Google Cloud Storage......')    
    export_dict['bucket']         = str(fun_Param_dict['bucket'])
    export_dict['image']          = partition
    export_dict['description']    = form_folder + '_Partition_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = exportFolder + '/' + export_dict['description']

    task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start()) 
    



#############################################################################################################
# Description: Exports three ancillary maps(QC, Date and partition) associated withfun_Param_dict one set of LEAF products
#
# Note: If month value is outside of range (1 to 12), then a peak season product will be created.
#
# Revision history:  2021-Oct-18  Lixin Sun  Initial creation 
#                    2022-Jun-20  Lixin Sun  Added capability for exporting RGB bands. This is necessary for
#                                            debugging purpose.  
#############################################################################################################
def export_DateImg(mosaic, fun_Param_dict, region, task_list):
  '''Exports three ancillary maps associated with one set of LEAF products
  Args:
    mosaic(ee.Image): a given mosaic image, which includes "Date" and "QC" bands;
    fun_Param_dict({}): a dictionary storing other required running parameters;
    mapBounds(ee.Geometry): the spatial boundary used in LEAF production;
    export_RGB(Boolean): a flag indicating if to export RGB mosaic images;
    task_list([]): a list for storing the links to exporting tasks.'''
  #==========================================================================================================
  # Create the names of exporting folder and files 
  #==========================================================================================================
  month        = int(fun_Param_dict['month']) 
  year_str     = str(fun_Param_dict['year'])
  tile_str     = str(fun_Param_dict['tile_name'])
  scale_str    = str(fun_Param_dict['resolution'])
  given_folder = str(fun_Param_dict['folder'])

  form_folder  = tile_str + '_' + year_str
  exportFolder = form_folder if len(given_folder) < 2 else given_folder  

  if month >= 1 or month <= 12:
    filePrefix = form_folder + '_' + eoImg.get_MonthName(month)  

  #==========================================================================================================
  # Export ancillary maps associated with LEAF products 
  #==========================================================================================================
  out_location = str(fun_Param_dict['location']).lower()

  export_dict = {'scale': fun_Param_dict['resolution'],
                 'crs': 'EPSG:3979',
                 'maxPixels': 1e11,
                 'region': region}
  
  if out_location.find('drive') > -1:
    print('<export_DateImg> Exporting date image to Google Drive......')  
    export_dict['folder']         = exportFolder
    export_dict['image']          = mosaic.select([eoImg.pix_date])
    export_dict['description']    = filePrefix + '_Date_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = filePrefix + '_Date_' + scale_str + 'm'

    task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())

  elif out_location.find('storage') > -1:
    print('<export_DateImg> Exporting date image to Google Cloud Storage......')    
    export_dict['bucket']         = str(fun_Param_dict['bucket'])    
    export_dict['image']          = mosaic.select([eoImg.pix_date])
    export_dict['description']    = filePrefix + '_Date_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = exportFolder + '/' + export_dict['description']

    task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())





#############################################################################################################
# Description: Exports three ancillary maps(QC, Date and partition) associated withfun_Param_dict one set of LEAF products
#
# Note: If month value is outside of range (1 to 12), then a peak season product will be created.
#
# Revision history:  2021-Oct-18  Lixin Sun  Initial creation 
#                    2022-Jun-20  Lixin Sun  Added capability for exporting RGB bands. This is necessary for
#                                            debugging purpose.  
#############################################################################################################
def export_RGBImg(mosaic, fun_Param_dict, region, task_list):
  '''Exports three ancillary maps associated with one set of LEAF products
  Args:
    mosaic(ee.Image): a given mosaic image, which includes "Date" and "QC" bands;
    fun_Param_dict({}): a dictionary storing other required running parameters;
    mapBounds(ee.Geometry): the spatial boundary used in LEAF production;
    task_list([]): a list for storing the links to exporting tasks.'''
  #==========================================================================================================
  # Create the names of exporting folder and files 
  #==========================================================================================================
  month        = int(fun_Param_dict['month']) 
  year_str     = str(fun_Param_dict['year'])
  tile_str     = str(fun_Param_dict['tile_name'])
  scale_str    = str(fun_Param_dict['resolution'])
  given_folder = str(fun_Param_dict['folder'])

  form_folder  = tile_str + '_' + year_str
  exportFolder = form_folder if len(given_folder) < 2 else given_folder  

  if month >= 1 or month <= 12:
    filePrefix = form_folder + '_' + eoImg.get_MonthName(month)  

  #==========================================================================================================
  # Export ancillary maps associated with LEAF products 
  #==========================================================================================================
  out_location = str(fun_Param_dict['location']).lower()

  export_dict = {'scale': fun_Param_dict['resolution'],
                 'crs': 'EPSG:3979',
                 'maxPixels': 1e11,
                 'region': region}
  
  #==========================================================================================================
  # Export RGB images 
  #==========================================================================================================
  print('<export_ancillaries> function param = ', fun_Param_dict)
  RGB_names = eoImg.get_RGB_BandNames(int(fun_Param_dict['sensor']), eoImg.sur_ref)
    
  if out_location.find('drive') > -1:
    print('<export_RGBImg> Exporting RGB images to Google Cloud Storage......')  
    export_dict['folder']         = exportFolder

    scale_img = ee.Image(10000) 
    export_dict['image']          = mosaic.select([RGB_names[0]]).multiply(scale_img).toUint16()
    export_dict['description']    = filePrefix + '_blu_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = filePrefix + '_blu_' + scale_str + 'm'
    task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())

    export_dict['image']          = mosaic.select([RGB_names[1]]).multiply(scale_img).toUint16()
    export_dict['description']    = filePrefix + '_grn_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = filePrefix + '_grn_' + scale_str + 'm'      
    task_list.append(ee.batch.Export.image.toDrive(**export_dict).start() )
      
    export_dict['image']          = mosaic.select([RGB_names[2]]).multiply(scale_img).toUint16()
    export_dict['description']    = filePrefix + '_red_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = filePrefix + '_red_' + scale_str + 'm'      
    task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())

  elif out_location.find('storage') > -1:
    print('<export_RGBImg> Exporting RGB images to Google Cloud Storage......')  
    export_dict['bucket'] = str(fun_Param_dict['bucket'])

    export_dict['image']          = mosaic.select([RGB_names[0]]).multiply(scale_img).toUint16()
    export_dict['description']    = filePrefix + '_blu_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = exportFolder + '/' + export_dict['description']      
    task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())

    export_dict['image']          = mosaic.select([RGB_names[1]]).multiply(scale_img).toUint16()
    export_dict['description']    = filePrefix + '_grn_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = exportFolder + '/' + export_dict['description']      
    task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())

    export_dict['image']          = mosaic.select([RGB_names[2]]).multiply(scale_img).toUint16()
    export_dict['description']    = filePrefix + '_red_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = exportFolder + '/' + export_dict['description']      
    task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())





#############################################################################################################
# Description: This function creates a mask that masks out cloud/shadow, snow/ice and water. This mask will
#              be used to set flag for the 3rd bit in the QC image of a LEAF product. 
#
# Revision history:  2022-Jun-22  Lixin Sun  Initial creation 
#
#############################################################################################################
def LEAF_valid_mask(Image, SensorCode, DataUnit):
  '''Exports three ancillary maps associated with one set of LEAF products
  Args:
    Image(ee.Image): a given mosaic image;
    SensorCode(int): an integer indicating a sensor type (LS 5,7,8,9 or S2);
    DataUnit(int): an integer indicating a data type (TOA or surface reflectance);
    max_ref(float or int): the maximum reflectance value in the given Image.'''
  # Cast some input parameters
  ssr_code  = int(SensorCode)
  data_unit = int(DataUnit) 

  # Invoke the functions to generate various masks. 
  # Note the value range in "Image" is [0, 1] since it is used for LEAF calculation 
  snow_mask  = eoIM.Img_SnowMask (Image, ssr_code, data_unit, 1)
  water_mask = eoIM.Img_WaterMask(Image, ssr_code, data_unit, 1)
  valid_mask = eoIM.Img_ValidMask(Image, ssr_code, data_unit, 1)  
  
  #return valid_mask
  return snow_mask.gt(0).Or(water_mask.gt(0)).Or(valid_mask.gt(0))




#############################################################################################################
# Description: Produces one vegetation parameter map for a specific region and time period
#
# Note:        The reflectance value range of the given mosaic image must be within 0 and 1.
#
# Revision history:  2021-May-20  Lixin Sun  Initial creation 
#                    2021_Oct-11  Lixin Sun  Moved mosaic creation outside this function. This ensure the
#                                            same mosaic image can be used for generating different products.
#                    2021-Oct-15  Lixin Sun  Modified so that peak season ("month" argument is outside of 
#                                            1 and 12) product can also be generated. 
#############################################################################################################
def one_LEAF_product(inMosaic, fun_Param_dict, region, output, task_list):
  '''Produces one LEAF product for a specific region and time period
    Args:
       mosaic(ee.Image): a given mosaic image from which products will be generated;       
       fun_Param_dict({}): a dictionary storing most required parameters;
       region(ee.Geometry): the spatial region of the production;
       output (Bool): the flag indicating whether or not to export the results;
       task_list([]): a list for storing the exporting tasks.'''  
  #==========================================================================================================
  # Obtain the names of a GEE Data Catalog ('COPERNICUS/S2_SR_HARMONIZED' or 'LANDSAT/LC08/C01/T1_SR') and
  # a biopgysical parameter (one of 'LAI', 'fCOVER', 'fAPAR' and 'Albedo').
  #==========================================================================================================
  ssr_code  = int(fun_Param_dict['sensor'])
  coll_name = eoImg.GEE_catalog_name(ssr_code, eoImg.sur_ref)  
  prod_name = fun_Param_dict['prod_name']
  
  #==========================================================================================================
  # Determine the collection and production dictionaries based on above two names. 
  #==========================================================================================================
  coll_dict = COLL_OPTIONS[coll_name] # ee.Dictionay object related to a selected collection type
  prod_dict = PROD_OPTIONS[prod_name] # ee.Dictionay object related to a selected product type
  
  #==========================================================================================================
  # Determine the number of land cover classes based on the number of networks and parameter types.
  #==========================================================================================================  
  total_nets = coll_dict["Collection_SL2P"].size()      # the total number of networks (ee.Feature objects)  
  numbParams = int(coll_dict["numVariables"])           # the total number of biophysical parameters (normally 7)
  numClasses = total_nets.divide(ee.Number(numbParams)) # the number of land cover classes

  #==========================================================================================================
  # Create two network matrices, estim_net and error_net, with their rows and columns corresponding to 
  # different biophysical parameters and land cover types.
  # Note: each element in the network matrices is a ee.Directory object with 8 keys.
  #==========================================================================================================   
  estim_net = ee.List.sequence(1, numbParams) \
                .map(lambda netNumb: make_DNet_arr(coll_dict["Collection_SL2P"], numClasses, netNumb))
    
  error_net = ee.List.sequence(1, numbParams) \
                .map(lambda netNumb: make_DNet_arr(coll_dict["Collection_SL2Perrors"], numClasses, netNumb))

  #==========================================================================================================
  # Produce biophysical parameter and its uncertainty maps
  #==========================================================================================================
  year      = int(fun_Param_dict['year'])
  partition = eoAD.get_GlobLC(region, year)  # A proper land cover map will be selected based on a given year
  
  estim_img = wrapperNNets(estim_net, partition, prod_dict, coll_dict, "estimate", inMosaic)
  error_img = wrapperNNets(error_net, partition, prod_dict, coll_dict, "error",    inMosaic)
    
  #==========================================================================================================
  # Select the parameter and uncertainty maps
  #==========================================================================================================
  #estim_img = estim_cube.select([0])
  #error_img = error_cube.select([0])  
  #networkID = estim_cube.select(['networkID'])

  #==========================================================================================================
  # Create a QC band image for a LEAF product
  #==========================================================================================================
  sl2pDomain = coll_dict["sl2pDomain"]
  bandList   = coll_dict["inputBands"]
  
  QC_img = LEAF_QCImage(inMosaic, estim_img, sl2pDomain, prod_dict, bandList, ssr_code, eoImg.sur_ref)

  #==========================================================================================================
  # Rescale parameter and uncertainty maps so that they be export in 8-bits images 
  #==========================================================================================================
  if prod_name == 'Albedo' or prod_name == 'fAPAR' or prod_name == 'fCOVER':
    scaling_factor = ee.Image(200);  # Could be 255, but 200 is easy to remember
  elif prod_name == 'LAI':
    scaling_factor = ee.Image(20);   # Modified on Jan. 28, 2021
  
  estim_img = estim_img.where(estim_img.lt(ee.Image(0.0)), ee.Image(0.0))        
  estim_img = estim_img.multiply(scaling_factor).uint8()
  error_img = error_img.multiply(scaling_factor).uint8()

  #estim_img = estim_img.where(partition.eq(ee.Image(18)), ee.Image(0))
  #error_img = error_img.where(partition.eq(ee.Image(18)), ee.Image(0))  

  #==========================================================================================================
  # export the results as necessary
  #==========================================================================================================
  if output == True:    
    export_products(fun_Param_dict, region, estim_img, error_img, QC_img, 0, task_list)
  else:
    return estim_img, QC_img





#############################################################################################################
# Description: This function answers if a "InquireStr" is included in "ProductList" list, which is a 
#              container for storing optional products (e.g., 'lai', 'fapar', 'fcover', 'albedo', 'date',
#              'partition' or 'RGB') to be exported by LEAF production tool.
#
# Revision history:  2022-Oct-27  Lixin Sun  Initial creation 
#
#############################################################################################################
def Is_export_required(InquireStr, ProductList):
  '''This function answers if a "InquireStr" is included in "ProductList" list.
     Args:
       InquireStr(string): A string that is inquired.
       ProductList(string): A list of strings that represent the prodcuts to be exported by LEAF production tool.'''  

  for prod in ProductList:
    prod_low = prod.lower()
    if prod_low.find(InquireStr) != -1:
      return True

  return False





#############################################################################################################
# Description: Produces monthly or annual vegetation parameter maps for a number of tiles using the images 
#              acquired within several summer months or an entire peak season.
#
# Note:        This function involves two parameter dictionaries, "exe_Param_dict" and "fun_Param_dict".
#              Both of them are used for transfering parameters to 'LEAF_tool_main' and other functions. 
#              The relationship of these two dictionaries is that a "fun_Param_dict" object is one of the
#              combinations between the elements of the three vectors members ('months', 'prod_names' and
#              'tile_names') of "exe_Param_dict". In "fun_Param_dict", the key names of the elements that
#              corresponds to the three vectors in "exe_Param_dict" are 'month', 'prod_name' and 'tile_name'.
#              An example of a 'exe_Param_dict' object is something looks like as follows:
#     
#              EXE_LEAF_PARAMS = {'sensor': 101,                   
#                                 'year': 2019,                    
#                                 'months': [5,6,7,8,9,10],        
#                                 'prod_names': ['LAI', 'fCOVER', 'Albedo', 'fAPAR', 'partition', 'date', 'rgb'],
#                                 'tile_names': ['tile41', 'tile42'],        
#                                 'resolution': 20, 
#                                 'location': 'drive', 
#                                 'bucket': 'leaf_products', 
#                                 'folder': ''}  
#
#              With this dictionary passed to 'LEAF_tool_main' function, a full set ('LAI', 'fCOVER',
#              'Albedo' and 'fAPAR') of monthly biophysical parameter maps will be produced for 'tile41'
#              and 'tile42' using the Sentinel-2 images acquired in the monthes from May to October of
#              2019. The product maps will be exported to Google Drive in 20m spatial resolution. 
#
# Revision history:  2021-May-20  Lixin Sun  Initial creation 
#                    2022-Jan-14  Lixin Sun  Modified so that multiple tiles can be processed for one 
#                                            one execution of LEAF production tool.
#                    2022-Oct-27  Lixin Sun  Added three new optional name strings to 'prod_names'. This 
#                                            makes exporting partition, date and RGB images is optional
#                                            and is usefull in case some exporting processes were failed,
#                                            then specific images need to reproduced and exported later on.
#############################################################################################################
def LEAF_production(ExeParamDict):
  '''Produces monthly or annual vegetation parameter maps for a number of tiles using the images acquired within 
     several summer months or an entire peak season.
     Args:
       exe_Param_dict({}): A Python dictionary storing parameters for one execution of LEAF Production Tool.
       export_RGB(Boolean): A flag indicating if to export RGB mosaic image.'''  
  # Standardize the given execution parameters
  exe_Param_dict = eoParams.get_LEAF_params(ExeParamDict)

  #==========================================================================================================
  # Create an initial/base "fun_Param_dict" dictionary from a subset of the elements of 'exe_Param_dict' 
  # dictionary. During the process of passing "fun_Param_dict" to 'LEAF_Mosaic', 'one_LEAF_Product' and
  # 'export_ancillaries' functions, missing elements will be added later on.
  #==========================================================================================================
  fun_Param_dict = {'sensor':     exe_Param_dict['sensor'],
                    'year':       exe_Param_dict['year'],
                    'resolution': exe_Param_dict['resolution'],
                    'location':   exe_Param_dict['location'],
                    'bucket':     exe_Param_dict['bucket'],
                    'folder':     exe_Param_dict['folder']}
    
  #==========================================================================================================
  # Three Loops through the combinations between the elements of the vectors with 'tile_names', 'months' and
  # 'prod_names' as keys in 'exe_Param_dict'.
  # Note that, for the same month, one mosaic can be reused for generating different products. 
  #==========================================================================================================
  ProductList = exe_Param_dict['prod_names']
  task_list   = []

  # Produce porducts for eath tile specified in the list with 'tile_names' as key
  for tile in exe_Param_dict['tile_names']:  
    fun_Param_dict['tile_name'] = tile   # Add an element with 'tile_name' as key to 'fun_Param_dict'
    
    if eoTG.is_valid_tile_name(tile) == True:
      region = eoTG.PolygonDict.get(tile)      
    else:
      region = eoTG.custom_RegionDict.get(tile)
    
    region = eoTG.expandSquare(region, 0.02)

    # Export a classification for a tile only once. 
    if Is_export_required('parti', ProductList):
      export_ClassImg(fun_Param_dict, region, task_list)

    # Produce monthly porducts with the images acquired within the months in the vector corresponding to 'months' key
    for month in exe_Param_dict['months']:
      fun_Param_dict['month'] = month     # Add an element with 'month' as key to 'fun_Param_dict'
      mosaic = eoMosaic.LEAF_Mosaic(fun_Param_dict, region)

      # Export date image or/and RGB image for every month
      if Is_export_required('date', ProductList):
        export_DateImg(mosaic, fun_Param_dict, region, task_list)
      
      if Is_export_required('rgb', ProductList):
        export_RGBImg(mosaic, fun_Param_dict, region, task_list)

      # Produce porducts specified in the vector corresponding to 'prod_names' key
      for prod in exe_Param_dict['prod_names']:
        prod_low = prod.lower()
        if prod_low.find('lai') != -1 or prod_low.find('fcover') != -1 or prod_low.find('albedo') != -1 or prod_low.find('fapar') != -1:
          fun_Param_dict['prod_name'] = prod   # Add a product to 'fun_Param_dict' with 'prod_name' as key
          one_LEAF_product(mosaic, fun_Param_dict, region, True, task_list)
      
  return task_list
