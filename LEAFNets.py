import ee


import Image as Img
import ImgMask as IM
import eoTileGrids as eoTG
import eoParams
import Mosaic
import eoAuxData as eoAD
import LEAF_LS as LFLS


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
    'S2_SR': {
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
    'L8_SR': {
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
        "outmax": 1,  #(ee.Image(ee.Array([[1]])))
        "scale_factor": 200,
        "compact_factor": 1},
    'fAPAR': {
        "Name":      'fAPAR',
        "errorName": 'errorfAPAR',
        "maskName":   'maskfAPAR',
        "description": 'Fraction of absorbed photosynthetically active radiation',
        "variable": 2,
        "outmin": 0 ,  #(ee.Image(ee.Array([[0]]))),
        "outmax": 1,  #(ee.Image(ee.Array([[1]])))
        "scale_factor": 200,
        "compact_factor": 256},
    'fCOVER': {
        "Name": 'fCOVER',
        "errorName": 'errorfCOVER',
        "maskName": 'maskfCOVER',
        "description": 'Fraction of canopy cover',
        "variable": 3,
        "outmin": 0,  #(ee.Image(ee.Array([[0]]))),
        "outmax": 1,  #(ee.Image(ee.Array([[1]])))
        "scale_factor": 200,
        "compact_factor": 65536},
    'LAI': {
        "Name":        'LAI',
        "errorName":   'errorLAI',
        "maskName":    'maskLAI',
        "description": 'Leaf area index',
        "variable": 1,
        "outmin": 0,  #(ee.Image(ee.Array([[0]]))),
        "outmax": 15,  #(ee.Image(ee.Array([[1]])))
        "scale_factor": 20,
        "compact_factor": 16777216},
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
         networks(ee.List): a 2d matrix of networks (ee.Dictionary objects);
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
# Description: This function exports one 64-Bits image that contains FOUR biophysical parameter maps and one 
#              QC map to either Google Drive or Google Cloud Storage
#
# Revision history:  2022-Nov-14  Lixin Sun  Initial creation 
#
#############################################################################################################
def export_compact_params(fun_Param_dict, region, compactImg, task_list):
  '''Exports a 64-Bits image that contains FOUR biophysical parameter maps and one QC map to either GD or GCS.

     Args:
       fun_Param_dict(dictionary): a dictionary storing required running parameters;
       region(ee.Geometry): the spatial region of interest;       
       compactImg(ee.Image): an 64-bits image containing FOUR biophysical parameter maps and one QC map;
       task_list([]): a list storing the links to exporting tasks. '''
  #==========================================================================================================
  # Create the names of exporting folder anf files 
  #==========================================================================================================
  month        = int(fun_Param_dict['month'])
  year_str     = str(fun_Param_dict['year'])   
  tile_str     = str(fun_Param_dict['tile_name'])
  scale_str    = str(fun_Param_dict['resolution'])
  given_folder = str(fun_Param_dict['folder'])
  
  tile_name    = tile_str.split('_')[0]
  form_folder  = tile_name + '_' + year_str
  exportFolder = form_folder if len(given_folder) < 2 else given_folder

  month_name   = Img.get_MonthName(month)
  filename = tile_str + '_' + year_str
  if month < 1 or month > 12:
    filename = filename + '_bioParams_QC_' + scale_str + 'm'
  else:
    filename = filename + '_' + month_name + '_bioParams_QC_' + scale_str + 'm'

  #==========================================================================================================
  # Prepare initial export dictionary and output location 
  #==========================================================================================================
  export_dict = {'image': compactImg,
                 'description': filename,
                 'fileNamePrefix': filename,
                 'scale': int(fun_Param_dict['resolution']),
                 'crs': 'EPSG:3979',
                 'maxPixels': 1e11,
                 'region': region}

  #==========================================================================================================
  # Export a 64-bits image containing FOUR biophysical parameter maps and one map to either GD or GCS
  #==========================================================================================================
  out_location = str(fun_Param_dict['location']).lower()

  if out_location.find('drive') > -1:
    export_dict['folder'] = exportFolder
    task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())
  elif out_location.find('storage') > -1:
    export_dict['bucket'] = str(fun_Param_dict['bucket'])
    export_dict['fileNamePrefix'] = exportFolder + '/' + filename
    task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())




#############################################################################################################
# Description: This function exports one biophysical parameter map to either GD or GCS.
#
# Revision history:  2022-Nov-14  Lixin Sun  Initial creation 
#
#############################################################################################################
def export_one_param(fun_Param_dict, Region, ParamMap, task_list):
  '''Exports one biophysical parameter map to either GD or GCS.

     Args:
       fun_Param_dict(dictionary): a dictionary storing other required running parameters;
       Region(ee.Geometry): the spatial region of interest;
       ParamMap(ee.Image): the parameter map to be exported;
       task_list([]): a list storing the links to exporting tasks. '''
  #==========================================================================================================
  # Create the names of exporting folder anf files 
  #==========================================================================================================
  month        = int(fun_Param_dict['month'])
  year_str     = str(fun_Param_dict['year'])   
  tile_str     = str(fun_Param_dict['tile_name'])
  scale_str    = str(fun_Param_dict['resolution'])
  given_folder = str(fun_Param_dict['folder'])
  prod_name    = str(fun_Param_dict['prod_name'])

  tile_name    = tile_str.split('_')[0]
  form_folder  = tile_name + '_' + year_str
  exportFolder = form_folder if len(given_folder) < 2 else given_folder  

  month_name   = Img.get_MonthName(month)
  filename  = tile_str + '_' + year_str
  if month < 1 or month > 12:
    filename = filename + '_' + prod_name + '_' + scale_str + 'm'
  else:
    filename = filename + '_' + month_name + '_' + prod_name + '_' + scale_str + 'm'

  #==========================================================================================================
  # Prepare initial export dictionary and output location 
  #==========================================================================================================
  export_dict = {'image': ParamMap,
                 'description': filename,
                 'fileNamePrefix': filename,
                 'scale': int(fun_Param_dict['resolution']),
                 'crs': 'EPSG:3979',
                 'maxPixels': 1e11,
                 'region': Region}

  #==========================================================================================================
  # Export a 64-bits image containing FOUR biophysical parameter maps and one map to either GD or GCS
  #==========================================================================================================
  out_location = str(fun_Param_dict['location']).lower()

  if out_location.find('drive') > -1:
    export_dict['folder'] = exportFolder
    task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())
  elif out_location.find('storage') > -1:
    export_dict['bucket'] = str(fun_Param_dict['bucket'])
    export_dict['fileNamePrefix'] = exportFolder + '/' + filename
    task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())





#############################################################################################################
# Description: Exports a classification image associated with one tile to either GD or GCS.
#
# Revision history:  2021-Oct-18  Lixin Sun  Initial creation 
#                    2022-Oct-27  Lixin Sun  This function was separated from "export_ancillaries", which
#                                            does not exist anymore. 
#############################################################################################################
def export_ClassImg(ClassImg, fun_Param_dict, region, task_list):
  '''Exports a classification map associated with a tile to either GD or GCS.

  Args:
    ClassImg(ee.Image): The given class image;
    fun_Param_dict({}): a dictionary storing other required running parameters;
    region(ee.Geometry): the spatial boundary used in LEAF production;
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

  export_dict = {'image': ClassImg,
                 'scale': fun_Param_dict['resolution'],
                 'crs': 'EPSG:3979',
                 'maxPixels': 1e11,
                 'region': region,
                 'description': form_folder + '_Partition_' + scale_str + 'm'}
    
  if out_location.find('drive') > -1:
    print('<export_ClassImg> Exporting pratition to Google Drive......')  
    export_dict['folder']         = exportFolder    
    export_dict['fileNamePrefix'] = export_dict['description']

    task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())  

  elif out_location.find('storage') > -1:
    print('<export_ClassImg> Exporting partition to Google Cloud Storage......')    
    export_dict['bucket']         = str(fun_Param_dict['bucket'])
    export_dict['fileNamePrefix'] = exportFolder + '/' + export_dict['description']

    task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start()) 
    



#############################################################################################################
# Description: Exports Date image associated with one tile to either GD or GCS
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
  print('<export_DateImg> function started......')  
  month        = int(fun_Param_dict['month']) 
  year_str     = str(fun_Param_dict['year'])
  tile_str     = str(fun_Param_dict['tile_name'])
  scale_str    = str(fun_Param_dict['resolution'])
  given_folder = str(fun_Param_dict['folder'])

  form_folder  = tile_str + '_' + year_str
  exportFolder = form_folder if len(given_folder) < 2 else given_folder  

  if month >= 1 or month <= 12:
    filePrefix = form_folder + '_' + Img.get_MonthName(month)  
  
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
    export_dict['image']          = mosaic.select([Img.pix_date])
    export_dict['description']    = filePrefix + '_Date_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = filePrefix + '_Date_' + scale_str + 'm'

    task_list.append(ee.batch.Export.image.toDrive(**export_dict).start())

  elif out_location.find('storage') > -1:
    print('<export_DateImg> Exporting date image to Google Cloud Storage......')    
    export_dict['bucket']         = str(fun_Param_dict['bucket'])    
    export_dict['image']          = mosaic.select([Img.pix_date])
    export_dict['description']    = filePrefix + '_Date_' + scale_str + 'm'
    export_dict['fileNamePrefix'] = exportFolder + '/' + export_dict['description']

    task_list.append(ee.batch.Export.image.toCloudStorage(**export_dict).start())





#############################################################################################################
# Description: This function creates a pixel mask that masks out cloud/shadow, snow/ice and water. This mask
#              will be used to set a flag at the 3rd bit in a QC image. 
#
# Revision history:  2022-Jun-22  Lixin Sun  Initial creation 
#                    2022-Nov-16  Lixin Sun  Added water mask from a given classification map.
#
#############################################################################################################
def LEAF_valid_mask(Image, SsrData, MaxRef, ClassMap):
  '''Exports three ancillary maps associated with one set of LEAF products

  Args:
    Image(ee.Image): a given mosaic image;
    SsrData(Dictionary): a Dictionary containing metadata associated with a sensor and data unit;
    MaxRef(int): the maximum reflectance value in the given Image;
    ClassMap(ee.Image): a given classification map.'''

  # Invoke the functions to generate various masks. 
  # Note the value range in "Image" is [0, 1] since it is used for LEAF calculation 
  snow_mask   = IM.Img_SnowMask (Image, SsrData, MaxRef)
  #water_mask  = IM.Img_WaterMask(Image, SsrData, MaxRef)
  valid_mask  = IM.Img_ValidMask(Image, SsrData, MaxRef)  
  class_water = ClassMap.eq(0).Or(ClassMap.eq(18))  
  #return snow_mask.Or(water_mask).Or(valid_mask).Or(class_water)
  return snow_mask.Or(valid_mask).Or(class_water)




#############################################################################################################
# Description: This function applys ANN-based algorithm for Sentinel-2 data to generate a full set of LEAF
#              products for a specific region and time period and export them in separate files.
#
# Note:        (1) The reflectance value range of the given mosaic image must be within 0 and 1.
#              (2) The production time required by this function is higher than that required by
#                  "compact_params" function.
#
# Revision history:  2021-May-20  Lixin Sun  Initial creation 
#                    2021_Oct-11  Lixin Sun  Moved mosaic creation outside this function. This ensure the
#                                            same mosaic image can be used for generating different products.
#                    2021-Oct-15  Lixin Sun  Modified so that peak season ("month" argument is outside of 
#                                            1 and 12) product can also be generated. 
#############################################################################################################
def S2_separate_params(fun_Param_dict, inMosaic, Region, SsrData, ClassImg, task_list):
  '''Produces a full set of LEAF products for a specific region and time period and export them in separate files.

    Args:
       fun_Param_dict(Dictionary):
       inMosaic(ee.Image): a given mosaic image from which products will be generated;  
       Region(ee.Geometry): a ROI;     
       SsrData(Dictionary): a Dictionary containing metadata associated with a sensor and data unit;
       ClassImg(ee.Image): A given classification image;
       task_list([]): a list for storing the links to exporting tasks.'''
  #==========================================================================================================
  # Obtain the names of a GEE Data Catalog ('COPERNICUS/S2_SR_HARMONIZED' or 'LANDSAT/LC08/C01/T1_SR') and
  # a biophysical parameter (one of 'LAI', 'fCOVER', 'fAPAR' and 'Albedo').
  #==========================================================================================================
  coll_name = SsrData['NAME'] + "_SR"
  coll_dict = COLL_OPTIONS[coll_name] # ee.Dictionay object related to a selected collection type
 
  sl2pDomain = coll_dict["sl2pDomain"].aggregate_array("DomainCode").sort()
  bandList   = ee.List(coll_dict["inputBands"])
  LEAF_image = inMosaic.select(bandList.slice(3))  #Only select required spectral bands
  nBands     = bandList.slice(3).length()

  #==========================================================================================================
  # Create a QC image to mark the pixels where spectral values are out of the input range for calculating
  # biophysical parameters
  #==========================================================================================================
  QC_img = LEAF_image.multiply(ee.Image.constant(ee.Number(10))).ceil().mod(ee.Number(10))\
                     .multiply(ee.Image.constant(ee.List.sequence(0, nBands.subtract(1)).map(lambda value: ee.Number(10).pow(ee.Number(value))))) \
                     .reduce("sum").remap(sl2pDomain, ee.List.repeat(0, sl2pDomain.length()), 1).uint8()

  #==========================================================================================================
  # Mask out water bodies from the mosaic image
  #==========================================================================================================  
  water_mask  = ClassImg.neq(ee.Image(0)).And(ClassImg.neq(ee.Image(18)))
  mosaic      = inMosaic.updateMask(water_mask)

  #==========================================================================================================
  # Determine the number of land cover classes based on the number of networks and parameter types.
  #==========================================================================================================
  coll_nets  = coll_dict["Collection_SL2P"]
  total_nets = coll_nets.size()                         # the total number of networks (ee.Feature objects)  
  numbParams = int(coll_dict["numVariables"])           # the total number of biophysical parameters (normally 7)
  numClasses = total_nets.divide(ee.Number(numbParams)) # the number of land cover classes

  estim_net = ee.List.sequence(1, numbParams).map(lambda netNumb: make_DNet_arr(coll_nets, numClasses, netNumb))

  #==========================================================================================================
  # Define a function that can estimate a biophysical parameter and its corresponding QC image
  #==========================================================================================================   
  def estimate_param_QC(fun_Param_dict, QC_img):
    prod_dict = PROD_OPTIONS[fun_Param_dict['prod_name']]
    estim_img = wrapperNNets(estim_net, ClassImg, prod_dict, coll_dict, "estimate", mosaic)

    # Identify the pixels exceeding the output range 
    out_min    = ee.Image(prod_dict['outmin'])
    out_max    = ee.Image(prod_dict['outmax'])
    range_mask = estim_img.lt(out_min).Or(estim_img.gt(out_max)).multiply(ee.Image(2))
    QC_img     = QC_img.bitwiseOr(range_mask)

    scaling_factor = ee.Image(prod_dict['scale_factor'])
    estim_img      = estim_img.where(estim_img.lt(0), ee.Image(0)).multiply(scaling_factor)

    return estim_img.uint8(), QC_img.uint8()

  #==========================================================================================================
  # Estimate FOUR biophysical parameter maps and QC map, and then export them separately
  #==========================================================================================================
  fun_Param_dict['prod_name'] = 'LAI'
  param_map, QC_img = estimate_param_QC(fun_Param_dict, QC_img)  
  #export_one_param(fun_Param_dict, Region, param_map, task_list)  
  
  fun_Param_dict['prod_name'] = 'fCOVER'  
  param_map, QC_img = estimate_param_QC(fun_Param_dict, QC_img)
  #export_one_param(fun_Param_dict, Region, param_map, task_list)

  fun_Param_dict['prod_name'] = 'fAPAR'  
  param_map, QC_img = estimate_param_QC(fun_Param_dict, QC_img)
  #export_one_param(fun_Param_dict, Region, param_map, task_list)

  fun_Param_dict['prod_name'] = 'Albedo'
  param_map, QC_img = estimate_param_QC(fun_Param_dict, QC_img)
  #export_one_param(fun_Param_dict, Region, param_map, task_list)  
  
  #==========================================================================================================
  # Set flags/marks in the 3rd bit of "QC_img" for all kinds of invalid pixels (cloud, shadow, snow, ice, 
  # water, saturated or out of range) 
  #==========================================================================================================  
  fun_Param_dict['prod_name'] = 'QC'  
  invalid_mask = LEAF_valid_mask(inMosaic, SsrData, 1, ClassImg).multiply(ee.Image(4)).uint8()
  QC_img       = QC_img.unmask().bitwiseOr(invalid_mask)
  export_one_param(fun_Param_dict, Region, QC_img, task_list)




#############################################################################################################
# Description: This function applys a RF-based LEAF algorithm for Landsat-8/9 data to generate biophysical 
#              parameter maps for a specific region and time period and export them in separate files.
#
# Note:        (1) The reflectance value range of the given mosaic image must be within 0 and 1.
#              (2) The production time required by this function is higher than that required by
#                  "compact_params" function.
#
# Revision history:  2022-Dec-20  Lixin Sun  Initial creation 
#                   
#############################################################################################################
def LS_separate_params(fun_Param_dict, inMosaic, Region, BiomeImg, task_list):
  '''Produces a full set of LEAF products for a specific region and time period and export them in separate files.

    Args:
       fun_Param_dict(Dictionary):
       inMosaic(ee.Image): a given image/mosaic from which a bioparameter map will be generated;  
       Region(ee.Geometry): a ROI;     
       SsrData(Dictionary): a Dictionary containing metadata associated with a sensor and data unit;
       BiomeImg(ee.Image): A given biome image;
       task_list([]): a list for storing the links to exporting tasks.'''
  
  #================================================================================================
  # Construct RF-based models from the feature collections stored in GEE assets
  # A list of ee.FeatureColelction objects will be returned from "constructMethod" function
  #================================================================================================
  methodName    = "NAIVE"
  treeDirectory = "users/rfernand387/modisLandsatTrees/"

  method = LFLS.constructMethod(methodName, treeDirectory)
  print('\n\n<LS_separate_params> property names in used method = ', \
        ee.FeatureCollection(method.get(0)).propertyNames().getInfo())

  #================================================================================================
  # Attach the biome map/image to the given mosaic image
  # Note: For Landsat8/9 LEAF tool, biome map, instead of classification map, must be applied.
  #================================================================================================
  mosaic = inMosaic.addBands(BiomeImg.rename(['biome']))
  #print('<LS_separate_params> bands in mosaic = ', mosaic.bandNames().getInfo())
  
  biome_values = LFLS.uniqueValues(mosaic.select('biome'), Region, 0.0)
  print('<LS_separate_params> unique biome values = ', biome_values.getInfo())
  biome_values = ee.List([1,2,3,5])  # This line is only for testing purpose 
  
  #================================================================================================
  # Apply the models to the given mosaic image
  #================================================================================================
  biome_results = biome_values.map(lambda biomeID: LFLS.estimateResponse(method, biomeID, mosaic, Region))
  biome_results = biome_results.map(lambda image: ee.Image(image).unmask())

  final_result  = ee.ImageCollection(biome_results).max().clip(Region)

  return final_result





#############################################################################################################
# Description: This is a switch function that selects a algorithm suitable for Sentinel-2 or Landsat-8 data.
#              
# Revision history:  2022-Dec-20  Lixin Sun  Initial creation 
#                  
#############################################################################################################
def separate_params(fun_Param_dict, inMosaic, Region, SsrData, ClassImg, task_list):
  '''Produces a full set of LEAF products for a specific region and time period and export them in separate files.

    Args:
       fun_Param_dict(Dictionary):
       inMosaic(ee.Image): a given mosaic image from which products will be generated;  
       Region(ee.Geometry): a ROI;     
       SsrData(Dictionary): a Dictionary containing metadata associated with a sensor and data unit;
       ClassImg(ee.Image): A given classification image;
       task_list([]): a list for storing the links to exporting tasks.'''
  #==========================================================================================================
  # Obtain the names of a GEE Data Catalog ('COPERNICUS/S2_SR_HARMONIZED' or 'LANDSAT/LC08/C01/T1_SR') and
  # a biophysical parameter (one of 'LAI', 'fCOVER', 'fAPAR' and 'Albedo').
  #==========================================================================================================
  ssr_code = SsrData['SSR_CODE']

  if ssr_code > Img.MAX_LS_CODE:
    S2_separate_params(fun_Param_dict, inMosaic, Region, SsrData, ClassImg, task_list)
  else:
    LS_separate_params(fun_Param_dict, inMosaic, Region, SsrData, ClassImg, task_list)





#############################################################################################################
# Description: This function produces and exports a 64-bits image that contains a full set of vegetation 
#              parameter maps and one QC map for specified time period and region. 
#
# Note:        The reflectance value range of the given mosaic image must be within 0 and 1.
#
# Revision history:  2022-Nov-14  Lixin Sun  Created to increase the effiiciency of LEAF production. 
#
#############################################################################################################
def compact_params(inMosaic, SsrData, ClassImg):
  '''Produces and exports a 64-bits image that contains a full set of vegetation parameter maps 
     and one QC map for specified time period and region.
     
    Args:
       inMosaic(ee.Image): a given mosaic image to be used for biophysical parameter extraction;       
       SsrData(Dictionary): a Dictionary containing metadata associated with a sensor and data unit;
       ClassImg(ee.Image): a given classification image.'''
  
  #==========================================================================================================
  # Create a QC image that identifies the pixels that are out of input range  
  #========================================================================================================== 
  coll_name  = SsrData['NAME']         # Obtain the metadata dictionary associated with a sensor
  coll_dict  = COLL_OPTIONS[coll_name] # ee.Dictionay object related to a selected collection type  

  sl2pDomain = coll_dict["sl2pDomain"].aggregate_array("DomainCode").sort()
  bandList   = ee.List(coll_dict["inputBands"])
  LEAF_image = inMosaic.select(bandList.slice(3))  #Only select required spectral bands
  nBands     = bandList.slice(3).length()

  QC_img = LEAF_image.multiply(ee.Image.constant(10)).ceil().mod(ee.Number(10))\
                     .multiply(ee.Image.constant(ee.List.sequence(0, nBands.subtract(1)).map(lambda value: ee.Number(10).pow(ee.Number(value))))) \
                     .reduce("sum").remap(sl2pDomain, ee.List.repeat(0, sl2pDomain.length()), 1).uint8()

  #==========================================================================================================
  # Mask out water bodies from the mosaic image
  #==========================================================================================================  
  water_mask = ClassImg.neq(ee.Image(0)).And(ClassImg.neq(ee.Image(18)))
  mosaic     = inMosaic.updateMask(water_mask)

  #==========================================================================================================
  # Create a neural network for parameter estimation.
  #==========================================================================================================  
  coll_nets  = coll_dict["Collection_SL2P"]
  total_nets = coll_nets.size()                         # the total number of networks (ee.Feature objects)  
  numbParams = int(coll_dict["numVariables"])           # the total number of biophysical parameters (normally 7)
  numClasses = total_nets.divide(ee.Number(numbParams)) # the number of land cover classes

  estim_net = ee.List.sequence(1, numbParams).map(lambda netNumb: make_DNet_arr(coll_nets, numClasses, netNumb))

  #==========================================================================================================
  # Define a function that estimates a biophysical parameter map and its corresponding QC image
  #==========================================================================================================   
  def estimate_param_QC(paramName, compactImg, QCImg):
    # Estimate a vegetation parameter defined by "paramName"
    prod_dict = PROD_OPTIONS[paramName]       # get a production options corresponding to a parameter  
    estim_img = wrapperNNets(estim_net, ClassImg, prod_dict, coll_dict, "estimate", mosaic)    
    estim_img = estim_img.where(estim_img.lt(0), ee.Image(0))

    # Identify the pixels exceeding the output range 
    out_min    = ee.Image(prod_dict['outmin'])
    out_max    = ee.Image(prod_dict['outmax'])
    range_mask = estim_img.lt(out_min).Or(estim_img.gt(out_max)).multiply(ee.Image(2)).uint8()
    QCImg      = QCImg.bitwiseOr(range_mask)
    
    # Rescale estimated parameter map so that it can be emdebed into a compact image  
    combin_factor = ee.Image(prod_dict['scale_factor']*prod_dict['compact_factor']).toInt64()
    compactImg    = compactImg.add(estim_img.multiply(combin_factor))

    return compactImg, QC_img

  #==========================================================================================================
  # Estimate FOUR biophysical parameters
  #==========================================================================================================
  compact_img = inMosaic.select([0]).multiply(0).toInt64()

  compact_img, QC_img = estimate_param_QC('LAI',    compact_img, QC_img)  
  compact_img, QC_img = estimate_param_QC('fCOVER', compact_img, QC_img)
  compact_img, QC_img = estimate_param_QC('fAPAR',  compact_img, QC_img)
  compact_img, QC_img = estimate_param_QC('Albedo', compact_img, QC_img)

  #==========================================================================================================
  # Set flags/marks in the 3rd bit of QC_img for all invalid pixels (cloud, shadow, snow, ice, water,
  # saturated or out of range) and then Embed QC image into the compact image and returns it
  #==========================================================================================================
  invalid_mask = LEAF_valid_mask(inMosaic, SsrData, 1, ClassImg).multiply(ee.Image(4)).uint8()

  QC_img = QC_img.unmask().bitwiseOr(invalid_mask)  

  return compact_img.add(QC_img.multiply(4294967296))





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
# Description: Produces monthly biophysical parameter maps for a number of tiles and months.
#
# Note:        This function involves two parameter dictionaries, "exe_Param_dict" and "fun_Param_dict".
#              Both of them are used for transfering parameters to 'LEAF_tool_main' and other functions. 
#              The relationship of these two dictionaries is that a "fun_Param_dict" object is one of the
#              combinations between the elements of the three vectors members ('months', 'prod_names' and
#              'tile_names') of "exe_Param_dict". In "fun_Param_dict", the key names of the elements that
#              corresponds to the three vectors in "exe_Param_dict" are 'month', 'prod_name' and 'tile_name'.
#              An example of a 'exe_Param_dict' object is something looks like as follows:
#     
#              EXE_LEAF_PARAMS = {'sensor': 'S2_SR',                   
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
# Revision history:  2022-Nov-20  Lixin Sun  Rewrote so that biopgysical parameter maps can be produced 
#                                            efficiently. There are two different ways to export parameter 
#                                            maps, all the maps are in one compact image or in separate
#                                            images. The compact image exporting way is the most efficient,
#                                            but needs a post-processing to separate the parameter maps out
#                                            of the compact image. 
#
#############################################################################################################
def LEAF_production(ExeParamDict):
  '''Produces monthly biophysical parameter maps for a number of tiles and months.

     Args:
       exe_Param_dict({}): A Python dictionary storing parameters for one execution of LEAF Production Tool.'''

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
                    'folder':     exe_Param_dict['folder'],
                    'export_style': exe_Param_dict['export_style']}
    
  #==========================================================================================================
  # Three Loops through the combinations between the elements of the vectors with 'tile_names', 'months' and
  # 'prod_names' as keys in 'exe_Param_dict'.
  # Note that, for the same month, one mosaic can be reused for generating different products. 
  #==========================================================================================================
  SsrData     = Img.SSR_META_DICT[exe_Param_dict['sensor']]
  ssr_code    = SsrData['SSR_CODE']
  year        = int(exe_Param_dict['year'])
  ProductList = exe_Param_dict['prod_names']
  task_list   = []

  # Produce porducts for eath tile specified in the list with 'tile_names' as key
  for tile in exe_Param_dict['tile_names']:  
    fun_Param_dict['tile_name'] = tile   # Add an element with 'tile_name' as key to 'fun_Param_dict'    

    region     = eoTG.PolygonDict.get(tile) if eoTG.is_valid_tile_name(tile) == True else eoTG.custom_RegionDict.get(tile)
    region     = eoTG.expandSquare(region, 0.02)
    cloud_rate = eoTG.get_tile_cloud_rate(tile) if eoTG.is_valid_tile_name(tile) == True else -100

    # Create a classification map image based on region and targeted year
    IsBiome  = True if ssr_code < Img.MAX_LS_CODE else False
    ClassImg = eoAD.get_GlobLC(region, year, IsBiome).uint8()

    # Export a classification for a tile only once. 
    if Is_export_required('parti', ProductList):
      export_ClassImg(ClassImg, fun_Param_dict, region, task_list)

    # Produce monthly porducts with the images acquired within the months in the vector corresponding to 'months' key
    for month in exe_Param_dict['months']:
      # Add an element with 'month' as key to 'fun_Param_dict'  
      fun_Param_dict['month'] = month     

      # Generate a mosaic image for a month with either S2 or LS8/9 data 
      mosaic = Mosaic.LEAF_Mosaic(fun_Param_dict, region, cloud_rate)

      if Is_export_required('date', ProductList):
        export_DateImg(mosaic, fun_Param_dict, region, task_list)

      # Produce vegetation parameter maps and export them in a specified way (a compact image or separate images)      
      out_style = str(fun_Param_dict['export_style']).lower()
      if out_style.find('comp') > -1:
        out_params = compact_params(mosaic, SsrData, ClassImg)

        # Export the 64-bits image to either GD or GCS
        export_compact_params(fun_Param_dict, region, out_params, task_list)
      else: # Create separate parameter maps
        separate_params(fun_Param_dict, mosaic, region, SsrData, ClassImg, task_list)
      
  return task_list