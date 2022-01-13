import ee 
ee.Initialize()


import eoImgSet 
import eoImage as eoImg
import eoTileGrids as eoTG
#import eoWaterMap as eoWTMap
import eoMosaic




#############################################################################################################
# Description: Functions is for reading parameters for creating the ANNs applicable to Sentinel-2 data 
# 
# Revision history:  2021-May-17  Lixin Sun  Copied from the Richard's Python code
# 
#############################################################################################################
def s2_createFeatureCollection_estimates():           
    return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1')

def s2_createFeatureCollection_errors():
    return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error')
    
def s2_createFeatureCollection_domains():
    return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')
    #return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_DOMAIN')

def s2_createFeatureCollection_range():           
    return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')
    
def s2_createFeatureCollection_Network_Ind():
    return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/Parameter_file_sl2p')

def s2_createImageCollection_partition():           
    return ee.ImageCollection('users/rfernand387/NA_NALCMS_2015_tiles') \
           .map(lambda image: image.select("b1").rename("partition")) #\
           #.merge(ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V/Global")\
           #.map( lambda image: image.select("discrete_classification") \
           #.remap([0,20,30,40,50,60,70,80,90,100,111,112,113,114,115,116,121,122,123,124,125,126,200],[0,8,10,15,17,16,19,18,14,13,1,3,1,5,6,6,2,4,2,5,6,6,18],0) \
           #.toUint8().rename("partition")))    

def s2_createFeatureCollection_legend():
    return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/Legend_sl2p')



#############################################################################################################
# Description: Functions for reading parameters for creating ANNs applicable to Landsat-8 data 
# 
# Revision history:  2021-May-17  Lixin Sun  Copied from the Richard's Python code in Jupyter Notebook
# 
#############################################################################################################
def l8_createFeatureCollection_estimates():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/LANDSAT_LC08_C01_T1_SR_SL2P')    
    
def l8_createFeatureCollection_errors():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/LANDSAT_LC08_C01_T1_SR_SL2P_ERRORS')

def l8_createFeatureCollection_domains():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/LANDSAT_LC08_C01_T1_SR_DOMAIN')

def l8_createFeatureCollection_range():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/LANDSAT_LC08_C01_T1_SR_RANGE')

def l8_createFeatureCollection_Network_Ind():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/Parameter_file_sl2p')

def l8_createImageCollection_partition():
    return ee.ImageCollection('users/rfernand387/NA_NALCMS_2015_tiles')\
           .map(lambda image: image.select("b1").rename("partition"))
           #.merge(ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V/Global") \
           #.map( lambda image: image.select("discrete_classification") \
           #.remap([0,20,30,40,50,60,70,80,90,100,111,112,113,114,115,116,121,122,123,124,125,126,200],[0,8,10,15,17,16,19,18,14,13,1,3,1,5,6,6,2,4,2,5,6,6,18],0) \
           #.toUint8().rename("partition")))

def l8_createFeatureCollection_legend():
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/Legend_sl2p')    
    
    

#############################################################################################################
# Description: "LEAF_PARAMS" dictionary for storing the parameters required by running LEAF tool. 
# 
# Revision history:  2021-June-03  Lixin Sun  Initial creation
# 
#############################################################################################################    
'''LEAF_PARAMS = {
    'ssr_name': 'S2',  # Sensor name string (e.g., 'S2', 'L8', 'L7' and 'L5')
    'prod_names': ['LAI', 'fCOVER'], 
    'year': 2020,
    'months': [7, 8],  # Integer number represening a month 
    'tile_name': 'tile42',
    'spatial_scale': 30,    
    'out_folder': ''}
'''


#############################################################################################################
# Description: Constant dictionaries for storing parameters related to different image collections and 
#              different visualization/exporting options. 
# 
# Revision history:  2021-May-17  Lixin Sun  Copied from the Richard's Python code in Jupyter Notebook
# 
#############################################################################################################  
COLL_OPTIONS = {
    'COPERNICUS/S2_SR': {
      "name": 'S2',
      "description": 'Sentinel 2A',
      "Cloudcover": 'CLOUDY_PIXEL_PERCENTAGE',
      "Watercover": 'WATER_PERCENTAGE',
      "sza": 'MEAN_SOLAR_ZENITH_ANGLE',
      "vza": 'MEAN_INCIDENCE_ZENITH_ANGLE_B8A',
      "saa": 'MEAN_SOLAR_AZIMUTH_ANGLE', 
      "vaa": 'MEAN_INCIDENCE_AZIMUTH_ANGLE_B8A',
      "VIS_OPTIONS": 'VIS_OPTIONS',
      "Collection_SL2P":       ee.FeatureCollection(s2_createFeatureCollection_estimates()),      
      "Collection_SL2Perrors": ee.FeatureCollection(s2_createFeatureCollection_errors()),  
      "sl2pDomain":            ee.FeatureCollection(s2_createFeatureCollection_domains()),
      "Network_Ind":           ee.FeatureCollection(s2_createFeatureCollection_Network_Ind()),
      "partition":             ee.ImageCollection  (s2_createImageCollection_partition()),
      "legend":                ee.FeatureCollection(s2_createFeatureCollection_legend()),
      "numVariables": 7,
      "inputBands":   ['cosVZA','cosSZA','cosRAA','B3','B4', 'B5', 'B6', 'B7', 'B8A','B11','B12'],
      "inputScaling": [0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001]
    },
    'LANDSAT/LC08/C01/T1_SR': {
      "name": 'L8',
      "description": 'LANDSAT 8',
      "Cloudcover": 'CLOUD_COVER_LAND',
      "Watercover": 'CLOUD_COVER',
      "sza": 'SOLAR_ZENITH_ANGLE',
      "vza": 'SOLAR_ZENITH_ANGLE',
      "saa": 'SOLAR_AZIMUTH_ANGLE', 
      "vaa": 'SOLAR_AZIMUTH_ANGLE',
      "VIS_OPTIONS": 'VIS_OPTIONS',
      "Collection_SL2P":       ee.FeatureCollection(l8_createFeatureCollection_estimates()),
      "Collection_SL2Perrors": ee.FeatureCollection(l8_createFeatureCollection_errors()),
      "sl2pDomain":            ee.FeatureCollection(l8_createFeatureCollection_domains()),
      "Network_Ind":           ee.FeatureCollection(l8_createFeatureCollection_Network_Ind()),
      "partition":             ee.ImageCollection  (l8_createImageCollection_partition()),
      "legend":                ee.FeatureCollection(l8_createFeatureCollection_legend()),
      "numVariables": 7,
      "inputBands":   ['cosVZA','cosSZA','cosRAA','B3',  'B4',  'B5',  'B6',  'B7'],
      "inputScaling": [0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001]
    },
    'LANDSAT/LC08/C02/T1_L2': {
      "name": 'L8',
      "description": 'LANDSAT 8',
      "Cloudcover": 'CLOUD_COVER_LAND',
      "Watercover": 'CLOUD_COVER',
      "sza": 'SOLAR_ZENITH_ANGLE',
      "vza": 'SOLAR_ZENITH_ANGLE',
      "saa": 'SOLAR_AZIMUTH_ANGLE', 
      "vaa": 'SOLAR_AZIMUTH_ANGLE',
      "VIS_OPTIONS": 'VIS_OPTIONS',
      "Collection_SL2P":       ee.FeatureCollection(l8_createFeatureCollection_estimates()),
      "Collection_SL2Perrors": ee.FeatureCollection(l8_createFeatureCollection_errors()),
      "sl2pDomain":            ee.FeatureCollection(l8_createFeatureCollection_domains()),
      "Network_Ind":           ee.FeatureCollection(l8_createFeatureCollection_Network_Ind()),
      "partition":             ee.ImageCollection  (l8_createImageCollection_partition()),
      "legend":                ee.FeatureCollection(l8_createFeatureCollection_legend()),
      "numVariables": 7,
      "inputBands":   ['cosVZA','cosSZA','cosRAA','B3',  'B4',  'B5',  'B6',  'B7'],
      "inputScaling": [0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001,0.0001]
    }
}



'''PROD_OPTIONS = {
    "Surface_Reflectance": {
        "COPERNICUS/S2_SR": {
            "Name": 'Surface_Reflectance',
            "description": 'Surface_Reflectance',
            "inp":      [ 'B4', 'B5', 'B6', 'B7', 'B8A','B9','B11','B12']
        }
    },
    "Albedo": {
        "COPERNICUS/S2_SR": {
            "Name": 'Albedo',
            "errorName": 'errorAlbedo',
            "maskName": 'maskAlbedo',
            "description": 'Black sky albedo',
            "variable": 6,           
            "outmin": (ee.Image(ee.Array([[0]]))),
            "outmax": (ee.Image(ee.Array([[1]])))
        },
        "LANDSAT/LC08/C01/T1_SR": {
            "Name": 'Albedo',
            "errorName": 'errorAlbedo',
            "maskName": 'maskAlbedo',
            "description": 'Black sky albedo',
            "variable": 6,
            "outmin": (ee.Image(ee.Array([[0]]))),
            "outmax": (ee.Image(ee.Array([[1]])))
      },
    },
    'fAPAR': {
        "COPERNICUS/S2_SR": {
            "Name":      'fAPAR',
            "errorName": 'errorfAPAR',
            "maskName":   'maskfAPAR',
            "description": 'Fraction of absorbed photosynthetically active radiation',
            "variable": 2,
            "outmin": (ee.Image(ee.Array([[0]]))),
            "outmax": (ee.Image(ee.Array([[1]])))
        }
    },
    'fCOVER': {
        "COPERNICUS/S2_SR": {
            "Name": 'fCOVER',
            "errorName": 'errorfCOVER',
            "maskName": 'maskfCOVER',
            "description": 'Fraction of canopy cover',
            "variable": 3,
            "outmin": (ee.Image(ee.Array([[0]]))),
            "outmax": (ee.Image(ee.Array([[1]]))) 
        }
    },
    'LAI': {
        "COPERNICUS/S2_SR": {
            "Name":        'LAI',
            "errorName":   'errorLAI',
            "maskName":    'maskLAI',
            "description": 'Leaf area index',
            "variable": 1,
            "outmin": (ee.Image(ee.Array([[0]]))),
            "outmax": (ee.Image(ee.Array([[1]])))
        }  
    },
    'CCC': {
        "COPERNICUS/S2_SR": {
            "Name": 'CCC',
            "errorName": 'errorCCC',
            "maskName": 'maskCCC',
            "description": 'Canopy chlorophyll content',
            "variable": 1,
            "outmin": (ee.Image(ee.Array([[0]]))),
            "outmax": (ee.Image(ee.Array([[1000]])))
        } 
    },
    'CWC': {
        "COPERNICUS/S2_SR": {
            "Name": 'CWC',
            "errorName": 'errorCWC',
            "maskName": 'maskCWC',
            "description": 'Canopy water content',
            "variable": 1,
            "outmin": (ee.Image(ee.Array([[0]]))),
            "outmax": (ee.Image(ee.Array([[100]])))
        } 
    },
    'DASF': {
        "COPERNICUS/S2_SR": {
            "Name": 'DASF',
            "errorName": 'errorDASF',
            "maskName": 'maskDASF',
            "description": 'Directional area scattering factor',
            "variable": 1,
            "outmin": (ee.Image(ee.Array([[0]]))),
            "outmax": (ee.Image(ee.Array([[1]])))
        } 
    }
}'''




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
        "outmin": (ee.Image(ee.Array([[0]]))),
        "outmax": (ee.Image(ee.Array([[1]])))        
    },
    'fAPAR': {
        "Name":      'fAPAR',
        "errorName": 'errorfAPAR',
        "maskName":   'maskfAPAR',
        "description": 'Fraction of absorbed photosynthetically active radiation',
        "variable": 2,
        "outmin": (ee.Image(ee.Array([[0]]))),
        "outmax": (ee.Image(ee.Array([[1]])))        
    },
    'fCOVER': {
        "Name": 'fCOVER',
        "errorName": 'errorfCOVER',
        "maskName": 'maskfCOVER',
        "description": 'Fraction of canopy cover',
        "variable": 3,
        "outmin": (ee.Image(ee.Array([[0]]))),
        "outmax": (ee.Image(ee.Array([[1]]))) 
    },
    'LAI': {
        "Name":        'LAI',
        "errorName":   'errorLAI',
        "maskName":    'maskLAI',
        "description": 'Leaf area index',
        "variable": 1,
        "outmin": (ee.Image(ee.Array([[0]]))),
        "outmax": (ee.Image(ee.Array([[1]])))
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
# Description: Returns a single band image with name "networkid" corresponding given input partition image 
#              remapped to networkIDs
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [162])
# 
#############################################################################################################
def makeIndexLayer(inPartition, inLegend, inNetwork_Ind):

    partition   = ee.Image(inPartition)               # partition image
    legend      = ee.FeatureCollection(inLegend)      # legend to convert partition numbers to networks
    Network_Ind = ee.FeatureCollection(inNetwork_Ind) # legend to convert networks to networkIDs
    
    #get lists of valid partitions
    legend_list = legend.toList(legend.size())
    landcover   = legend_list.map(lambda feature: ee.Feature(feature).getNumber('Value'))

    # get corresponding networkIDs
    networkIDs = legend_list.map(lambda feature: ee.Feature(feature).get('SL2P Network')) \
                            .map(lambda propertyValue: ee.Feature(ee.FeatureCollection(Network_Ind).first()).toDictionary().getNumber(propertyValue))
    
    return partition.remap(landcover, networkIDs, 0).rename('networkID')
    

    
#############################################################################################################
# Description: Read coefficients of a network from csv EE asset
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [163])
# 
#############################################################################################################
def getCoefs(netData,ind) :
    return((ee.Feature(netData)).getNumber(ee.String('tabledata').cat(ee.Number(ind).int().format())))



#############################################################################################################
# Description: Parse one row of CSV file for a network into a global variable
#
# Note:  We assume a two-hidden-layer network with tansig functions but allow for variable nodes per layer
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [164])
#
#############################################################################################################
def makeNets(inFeature, inM):
    
    feature = ee.List(inFeature)
    M = ee.Number(inM)
    
    # get the requested network and initialize the created network
    netData = ee.Feature(feature.get(M.subtract(1)))
    net = {}
    
    # input slope
    num = ee.Number(6)
    start = num.add(1)
    end = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["inpSlope"] = ee.List.sequence(start,end).map(lambda ind: getCoefs(netData,ind))
    
    # input offset
    num = end.add(1)
    start = num.add(1)
    end = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["inpOffset"] = ee.List.sequence(start,end).map(lambda ind: getCoefs(netData,ind))

    # hidden layer 1 weight
    num = end.add(1)
    start = num.add(1)
    end = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["h1wt"] = ee.List.sequence(start,end).map(lambda ind: getCoefs(netData,ind))

    # hidden layer 1 bias
    num = end.add(1)
    start = num.add(1)
    end = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["h1bi"] = ee.List.sequence(start,end).map(lambda ind: getCoefs(netData,ind))

    # hidden layer 2 weight
    num = end.add(1)
    start = num.add(1)
    end = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["h2wt"] = ee.List.sequence(start,end).map(lambda ind: getCoefs(netData,ind))
  
    # hidden layer 2 bias
    num = end.add(1)
    start = num.add(1)
    end = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["h2bi"] = ee.List.sequence(start,end).map(lambda ind: getCoefs(netData,ind))

    # output slope
    num = end.add(1)
    start = num.add(1)
    end = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["outSlope"] = ee.List.sequence(start,end).map(lambda ind: getCoefs(netData,ind))
  
    # output offset
    num = end.add(1)
    start = num.add(1)
    end = num.add(netData.getNumber(ee.String('tabledata').cat(num.format())))
    net["outBias"] = ee.List.sequence(start,end).map(lambda ind: getCoefs(netData,ind))
    
    return(ee.Dictionary(net))




#############################################################################################################
# Description: Parse CSV file with list of networks for a selected variable. This will parse one network for
#              each landclass partition
#
# Note:        This function is not called by any other fuction so far
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [165])
#
#############################################################################################################
def makeNetVars(asset, numNets, variableNum):
    asset       = ee.FeatureCollection(asset)
    numNets     = ee.Number(numNets)
    variableNum = ee.Number(variableNum)  

    #get selected network 
    list_features = asset.flatten()
    filtered_features = ee.FeatureCollection(asset.filter(ee.Filter.eq('tabledata3', variableNum))).toList(numNets)
    
    return ee.List.sequence(1,numNets).map(lambda netNum: makeNets(filtered_features,netNum))
    
    

#############################################################################################################
# Description: Returns a ee.Dictionary object that contain two keys (Image and Network). The Image key 
#              corresponds an image masked so the networkID band equals the netIndex and the corresponding
#              network
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [166])
#
#############################################################################################################
def selectNet(inImage, inNetList, inBandNames, inBandScales, inNetIndex):
    '''Returns a ee.Dictionary object that contains two keys (Image and Network). 

       Args: 
         inImage(ee.Image): A given ee.Image object 
    '''
    image      = ee.Image(inImage)
    netList    = ee.List(inNetList)
    bandNames  = ee.List(inBandNames)
    bandScales = ee.Array(inBandScales)
    netIndex   = ee.Number(inNetIndex).int()
    
    #return ee.Image(image.updateMask(image.select('networkID').eq(netIndex)).select(bandNames))
    sclImg = ee.Image(bandScales).arrayProject([0]).arrayFlatten([bandNames])
    inImg  = ee.Image(image.updateMask(image.select('networkID').eq(netIndex)).select(bandNames))
    inImg  = inImg.multiply(sclImg)

    inNet = ee.List(netList.get(netIndex))

    return ee.Dictionary().set("Image", inImg).set("Network", inNet)


            
            
#############################################################################################################
# Description: Applies two layer neural network within input and output scaling
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [167])
#                    2021-May-27  Reviewed and added comments
#############################################################################################################
def applyNet(inOutputName, inNetDict):
    '''Applies two layer neural network within input and output scaling.

       Args: 
         inOutputName(string): 
         inNetDict(ee.Dictionary): This directionary contains two keys ('Image' and 'Network'). The associated 
                                   value of the second key ('Network') is the ANN to be applied to the image,
                                   which is the associated value of the first key('image'). '''

    outputName = ee.String(inOutputName)
    netDict    = ee.Dictionary(inNetDict)  #A given ee.Dictionary object containing two keys
    #print('\n\n<applyNet> network dictionary = ', netDict.getInfo())

    #========================================================================================================
    # Obtain the image and network objects separately from the given ee.Dictionay object, which is returned
    # from "selectNet" function
    #========================================================================================================
    img = ee.Image(netDict.get('Image'))
    net = ee.Dictionary(netDict.get('Network'))    

    inSlope = net.toArray(ee.List(['inpSlope', 'inpOffset']), 0).transpose()
    #print('<applyNet> inpSlope = ', inSlope.getInfo())

    # Input scaling    
    inGain  = ee.Image(net.toArray(ee.List(['inpSlope']), 0).transpose()).arrayProject([0]).arrayFlatten([img.bandNames()])
    inBias  = ee.Image(net.toArray(ee.List(['inpOffset']),0).transpose()).arrayProject([0]).arrayFlatten([img.bandNames()])
    l1inp2D = img.multiply(inGain).add(inBias)
    
    # Hidden layers    
    # "l12D" is a 2D iamge/matrix with 4 bands ('h1w1','h1w2','h1w3','h1w4','h1w5')
    l12D = ee.Image(net.toArray(ee.List(['h1wt']), 0).reshape([ee.List(net.get('h1bi')).length(), ee.List(net.get('inpOffset')).length()])) \
              .matrixMultiply(l1inp2D.toArray().toArray(1)) \
              .add(ee.Image(net.toArray(ee.List(['h1bi']),0).transpose())) \
              .arrayProject([0]).arrayFlatten([['h1w1','h1w2','h1w3','h1w4','h1w5']])
    
    # apply tansig 2/(1+exp(-2*n))-1. "l2inp2D" is a 2D image with 5 bands ('h1w1','h1w2','h1w3','h1w4','h1w5')
    l2inp2D = ee.Image(2).divide(ee.Image(1).add((ee.Image(-2).multiply(l12D)).exp())).subtract(ee.Image(1))

    # purlin hidden layers. "l22D" is a 2D image with only one band ('h2bi')
    l22D = l2inp2D.multiply(ee.Image(net.toArray(ee.List(['h2wt']),0).transpose()) \
                              .arrayProject([0]).arrayFlatten([['h2w1','h2w2','h2w3','h2w4','h2w5']])) \
                  .reduce('sum') \
                  .add(ee.Image(net.toArray(ee.List(['h2bi']),0))) \
                  .arrayProject([0]).arrayFlatten([['h2bi']])
    
    # Output scaling 
    outGain    = ee.Image(ee.Number(net.get('outSlope')))
    outBias    = ee.Image(ee.Number(net.get('outBias')))    
    outputBand = l22D.subtract(outBias).divide(outGain)     
    
    # Return network output
    return outputBand.rename(outputName)





#############################################################################################################
# Description: Returns image with single band named networkid corresponding given input partition image 
#              remapped to networkIDs. Applies a set of shallow networks to an image based on a provided 
#              partition (classification) map.
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [168])
#
#############################################################################################################
def wrapperNNets(inNetwork, inPartition, inProdOptions, inCollOptions, suffixName, inImage) :
    '''Applies a set of shallow networks to an image based on a provided partition (classification) map

       Args: 
         inNetwork(ee.List): The list of networks;
         inPartition(ee.image): The given partition/classification map;
         inProdOptions(ee.Dictionary): The dictionary containing options for desired product;
         inCollOptions(ee.Dictionary): the dictionary containing options for image collection;
         suffixName(string): The suffix name of output;
         inImage(ee.Image): The given (mosaic) image for vegetation parameter extraction.'''

    #========================================================================================================
    # typecast function parameters
    #========================================================================================================
    network     = ee.List(inNetwork)
    partition   = ee.Image(inPartition)
    ProdOptions = ee.Dictionary(inProdOptions)
    CollOptions = ee.Dictionary(inCollOptions)
    image       = ee.Image(inImage)
    
    #print('<wrapperNNets> product options = ', ProdOptions.getInfo())

    #========================================================================================================
    # determine networks based on collection
    #========================================================================================================
    netList = ee.List(network.get(ee.Number(ProdOptions.get('variable')).subtract(1))); 
    
    #========================================================================================================
    # parse land cover into network index and add to input image
    #========================================================================================================
    imageInput = image.addBands(makeIndexLayer(partition, CollOptions.get('legend'), CollOptions.get('Network_Ind')))

    # define list of input names
    '''return ee.ImageCollection(ee.List.sequence(0, netList.size().subtract(1)) \
                  .map(lambda netIndex: selectNet(imageInput, netList, CollOptions["inputBands"], netIndex)) \
                  .map(lambda netDict: applyNet(suffixName + ProdOptions['Name'], netDict))) \
                  .max() \
                  .addBands(partition) \
                  .addBands(imageInput.select('networkID'))
    '''
    #========================================================================================================
    # define list of input names
    #========================================================================================================
    netIndex = 0
    outName  = ee.String(suffixName).cat(ProdOptions.getString('Name'))
    netDict  = ee.Dictionary(selectNet(imageInput, netList, CollOptions.get('inputBands'), CollOptions.get('inputScaling'), netIndex))
    estimate = ee.Image(applyNet(outName, netDict))   

    return estimate.addBands(partition).addBands(imageInput.select('networkID'))
   


#############################################################################################################
# Description: Apply Sentinel-2 land mask
#
# Revision history:  2021-Oct-18  Copied from Richard's Python notebook (In [159])
#
#############################################################################################################
def s2MaskLand(image) :
    return image.updateMask((image.select('SCL').eq(4)).Or(image.select('SCL').eq(5)))



#############################################################################################################
# Description: Returns image with selected bands scaled
#
# Revision history:  2021-Oct-18  Copied from Richard's Python notebook (In [160])
#
#############################################################################################################
def scaleBands(bandList, scaleList, image) :
    '''Returns image with selected bands scaled

       Args: 
         bandList(ee.List): The list of bands;
         scaleList(ee.List): The list of scaling factors;
         image(ee.Image): A single image in a image collection.'''

    bandList  = ee.List(bandList)
    scaleList = ee.List(scaleList)
    return image.addBands(srcImg = image.select(bandList).multiply(ee.Image.constant(scaleList)).rename(bandList),overwrite = True)    




#############################################################################################################
# Description: Determine if inputs fall in domain of algorithm. Need to be updated to allow for the domain
#              to vary with partition
#
# Revision history:  2021-Oct-18  Copied from Richard's Python notebook (In [161])
#
#############################################################################################################
def invalidInput(sl2pDomain, bandList, image) :
  '''Determine if inputs fall in domain of algorithm.

     Args: 
       sl2pDomain(ee.FeatureCollection): A feature collection storing value domain;
       bandList(ee.List): The list of bands;
       image(ee.Image): A single image in a image collection.'''

  sl2pDomain = ee.FeatureCollection(sl2pDomain).aggregate_array("DomainCode").sort()
  bandList   = ee.List(bandList).slice(3)
  image      = ee.Image(image)

  # code image bands into a single band and compare to valid codes to make QC band
  image = image.addBands(image.select(bandList)
                              .multiply(ee.Image.constant(ee.Number(10)))
                              .ceil()
                              .mod(ee.Number(10))
                              .uint8()
                              .multiply(ee.Image.constant(ee.List.sequence(0,bandList.length().subtract(1)).map(lambda value: ee.Number(10).pow(ee.Number(value)))))
                              .reduce("sum")  
                              .remap(sl2pDomain, ee.List.repeat(0, sl2pDomain.length()), 1)
                              .rename("QC"))
  return image




##########################################################################################################
# Description: Creates a mosaic image specially for vegetation parameter extraction with LEAF tool.
#
# Note:        The major difference between a mosaic for LEAF tool and general-purpose mosaic is the 
#              attachment of three imaging geometrical angle bands. 
#  
# Revision history:  2021-May-19  Lixin Sun  Initial creation
#
##########################################################################################################
def LEAF_Mosaic(Param_dict, inMonth, mapBounds):
  '''Craete a mosaic image specially for vegetation parameter extraction with LEAF tool.
  Args:
     Param_dict(dictionary): A dictionary containing some required parameters;    
     inMonth(int or string): A specified month;
     mapBounds(ee.Geometry): A given spatial region of a mosaic image.'''

  #=======================================================================================================
  # Determine time and spatial ranges based the given parameters
  #=======================================================================================================
  month = int(inMonth)  
  year  = int(Param_dict['year'])  

  start, stop = eoImgSet.time_range_strs(year, month)

  #=======================================================================================================
  # Form an image colection object based on the given filtering criteria
  #=======================================================================================================
  ssr_code = int(Param_dict['sensor'])  
  #ssr_code = eoImg.SensorName2Code(ssr_name)
  img_coll = eoImgSet.getCollection(ssr_code, eoImg.sur_ref, mapBounds, start, stop)
  
  #=======================================================================================================
  # Pre-process every imagery and flag invalid inputs
  # The code in [219] of original Python code  COLL_OPTIONS
  #=======================================================================================================
  #CollName = eoImg.GEE_catalog_name(Param_dict['sensor'], eoImg.sur_ref)
  #img_coll = img_coll.map(lambda image: invalidInput(COLL_OPTIONS[CollName]["sl2pDomain"], COLL_OPTIONS[CollName]["inputBands"], image))  
                     #.map(lambda image: s2MaskLand(image)) \
                     #.map(lambda image: scaleBands(netOptions["inputBands"],netOptions["inputScaling"],image))

  #=======================================================================================================
  # Attach Date, Score and geometry angle bands to each image in the filtered image collection
  #=======================================================================================================
  #night_lights = eoMosaic.Global_night_lights(str(year))
  midDate = ee.Date(ee.Date(start).millis().add(ee.Date(stop).millis()).divide(ee.Number(2.0)))

  mosaic = eoMosaic.coll_mosaic(img_coll, ssr_code, eoImg.sur_ref, midDate, True)
  #print("<LEAF_Mosaic> band names in mosaic image = ", mosaic.bandNames().getInfo())

  #=======================================================================================================
  # Attach a QC band to mosaic image
  #=======================================================================================================
  CollName = eoImg.GEE_catalog_name(Param_dict['sensor'], eoImg.sur_ref)
  #print("<LEAF_Mosaic> collection name = ", CollName)

  mosaic   = invalidInput(COLL_OPTIONS[CollName]["sl2pDomain"], COLL_OPTIONS[CollName]["inputBands"], mosaic)    
  
  return mosaic
  '''med_mosaic   = img_coll.median()
  image1       = img_coll.first()  
  data_unit    = eoImg.DataUnit(image1) 
  rescale_f    = eoImg.get_rescale(ssr_code, data_unit)
  blue_name    = eoImg.get_BandName(eoImg.BLU_band, ssr_code)
  rescale_img  = ee.Image(ee.Number(rescale_f));  #Create a rescaling image
  
  blue_refer  = med_mosaic.select([blue_name]).multiply(rescale_img).toFloat()
  scored_coll = img_coll.map(lambda image: eoImg.attach_Date(image)) \
                        .map(lambda image: eoMosaic.attach_Score(night_lights, blue_refer, midDate, ssr_code, data_unit, image)) \
                        .map(lambda image: eoImg.add_Geometry(ssr_code, image))
  
  #==========================================================================================
  # Create a mosaic based on spectral score and then water mask for masking out water pixels
  #==========================================================================================
  mosaicImg  = scored_coll.qualityMosaic(eoImg.pix_score)

  water_mosaic = eoWTMap.coll_WaterMosaic(scored_coll)
  water_mask   = eoWTMap.coll_water_mapping(img_coll)
  water_mask = water_mask.where(partition.gte(ee.Image(18)), ee.Image(1))  

  return eoMosaic.improve_water_mosaic(mosaicImg, ssr_code, water_mosaic, water_mask)
  #return mosaicImg.updateMask(water_mask.not())  #Note that mosaic image cannot be clipped here
  return mosaicImg
  '''





#############################################################################################################
# Description: Exports one set of LEAF products
#
# Revision history:  2021-Oct-18  Lixin Sun  Initial creation 
#
#############################################################################################################
def export_LEAF_Products(PROD_name, month, Param_dict, mapBounds, estimateImage, errorImage, task_list):
  '''Produces one LEAF product for a specified month of a year

  Args:
    PROD_name(string): A specified product name string (e.g., 'LAI' or 'fCOVER');
    month(int or string): A targeted month (either an integer or a string). If month value is outside of
                          1 and 12, then a peak season product will be created.
    Param_dict(dictionary): A dictionary storing other required running parameters;
    mapBounds(ee.Geometry): The spatial boundary used in LEAF production;
    estimateImage(ee.Image): A LEAF parameter map image;
    errorImage(ee.Image): The uncertainty map associated with the LEAF parameter map; 
    task_list([]): A list for storing the links to exporting tasks.'''  

  #==========================================================================================================
  # Create the names of export folder anf files 
  #==========================================================================================================
  year_str     = str(Param_dict['year'])
  tile_str     = str(Param_dict['tile_name'])
  scale_str    = str(Param_dict['spatial_scale'])
  given_folder = str(Param_dict['out_folder'])

  form_folder  = tile_str + '_' + year_str

  exportFolder = form_folder if len(given_folder) < 2 else given_folder  
  month_name   = eoImg.get_MonthName(month)

  if month < 1 or month > 12:
    estimate_filePrefix  = form_folder + '_' + str(PROD_name) + '_' + scale_str + 'm'
    uncertain_filePrefix = form_folder + '_' + 'error' + str(PROD_name) + '_' + scale_str + 'm'
  else:  
    estimate_filePrefix  = form_folder + '_' + month_name + '_' + str(PROD_name) + '_' + scale_str + 'm'
    uncertain_filePrefix = form_folder + '_' + month_name + '_' + 'error' + str(PROD_name) + '_' + scale_str + 'm'

  #==========================================================================================================
  # Export LEAF products to a Google Drive directory 
  #==========================================================================================================
  out_location = str(Param_dict['location']).lower()

  if out_location.find('drive') > -1:
    task1 = ee.batch.Export.image.toDrive(
        image          = estimateImage,
        folder         = exportFolder, 
        description    = estimate_filePrefix,   
        fileNamePrefix = estimate_filePrefix,
        scale          = Param_dict['spatial_scale'], 
        crs            = 'EPSG:3979', 
        maxPixels      = 1e11, 
        region         = mapBounds)  

    task1.start() 
    task_list.append(task1)

    task2 = ee.batch.Export.image.toDrive(
        image          = errorImage,
        folder         = exportFolder, 
        description    = uncertain_filePrefix, 
        fileNamePrefix = uncertain_filePrefix,
        scale          = Param_dict['spatial_scale'], 
        crs            = 'EPSG:3979', 
        maxPixels      = 1e11, 
        region         = mapBounds)   
  
    task2.start()  
    task_list.append(task2)
  elif out_location.find('storage') > -1:
    print('<export_LEAF_Products> Exporting to Cloud Storage......')  
    out_bucket = str(Param_dict['bucket'])
    task1 = ee.batch.Export.image.toCloudStorage(
        image          = estimateImage,      
        bucket         = out_bucket,   
        description    = estimate_filePrefix,   
        fileNamePrefix = exportFolder + '/' + estimate_filePrefix,        
        scale          = Param_dict['spatial_scale'], 
        crs            = 'EPSG:3979', 
        maxPixels      = 1e11, 
        region         = mapBounds)  

    task1.start() 
    task_list.append(task1)

    task2 = ee.batch.Export.image.toCloudStorage(
        image          = errorImage,
        bucket         = out_bucket, 
        description    = uncertain_filePrefix, 
        fileNamePrefix = exportFolder + '/' + uncertain_filePrefix,
        scale          = Param_dict['spatial_scale'], 
        crs            = 'EPSG:3979', 
        maxPixels      = 1e11, 
        region         = mapBounds)   
  
    task2.start()  
    task_list.append(task2)  



#############################################################################################################
# Description: Exports Three ancillary maps associated with LEAF products
#
# Revision history:  2021-Oct-18  Lixin Sun  Initial creation 
#
#############################################################################################################
def export_LEAF_ancillaries(mosaic, month, Param_dict, mapBounds, task_list):
  '''Produces one LEAF product for a specified month of a year

  Args:
    mosaic(ee.Image): A given mosaic image, which includes "Date" and "QC" bands;
    month(int or string): A targeted month (either an integer or a string). If month value is outside of
                          1 and 12, then a peak season product will be created.
    Param_dict(dictionary): A dictionary storing other required running parameters;
    mapBounds(ee.Geometry): The spatial boundary used in LEAF production;
    task_list([]): A list for storing the links to exporting tasks.'''  

  #==========================================================================================================
  # Create the names of exporting folder and files 
  #==========================================================================================================
  year_str     = str(Param_dict['year'])
  tile_str     = str(Param_dict['tile_name'])
  scale_str    = str(Param_dict['spatial_scale'])
  given_folder = str(Param_dict['out_folder'])

  form_folder  = tile_str + '_' + year_str

  exportFolder = form_folder if len(given_folder) < 2 else given_folder  

  if month >= 1 or month <= 12:
    filePrefix = form_folder + '_' + eoImg.get_MonthName(month)   #str(month)

  QC_filePrefix   = filePrefix + '_QC_'        + scale_str + 'm'
  Date_filePrefix = filePrefix + '_Date_'      + scale_str + 'm'
  Part_filePrefix = filePrefix + '_Partition_' + scale_str + 'm'
  
  #==========================================================================================================
  # Generate partition map (The partition map for Sentinel-2 and Landsat imagery should be the same)
  #==========================================================================================================
  CollName = 'COPERNICUS/S2_SR'
  partition = (COLL_OPTIONS[CollName]["partition"]).filterBounds(mapBounds).mosaic().rename('partition')

  #==========================================================================================================
  # Export ancillary maps associated with LEAF products 
  #==========================================================================================================
  myScale  = Param_dict['spatial_scale']
  myCRS    = 'EPSG:3979'
  QC_img   = mosaic.select(['QC'])
  date_img = mosaic.select(['date'])

  task0 = ee.batch.Export.image.toDrive(
      image          = partition,
      folder         = exportFolder, 
      description    = Part_filePrefix,   
      fileNamePrefix = Part_filePrefix,
      scale          = myScale, 
      crs            = myCRS, 
      maxPixels      = 1e11, 
      region         = mapBounds)  

  task0.start() 
  task_list.append(task0)

  task1 = ee.batch.Export.image.toDrive(
      image          = QC_img,
      folder         = exportFolder, 
      description    = QC_filePrefix,   
      fileNamePrefix = QC_filePrefix,
      scale          = myScale, 
      crs            = myCRS, 
      maxPixels      = 1e11, 
      region         = mapBounds)  

  task1.start() 
  task_list.append(task1)

  task2 = ee.batch.Export.image.toDrive(
      image          = date_img,
      folder         = exportFolder, 
      description    = Date_filePrefix, 
      fileNamePrefix = Date_filePrefix,
      scale          = myScale, 
      crs            = myCRS, 
      maxPixels      = 1e11, 
      region         = mapBounds)   
  
  task2.start()  
  task_list.append(task2)  





#############################################################################################################
# Description: Produces one vegetation parameter map corresponding to a month of a year
#
# Revision history:  2021-May-20  Lixin Sun  Initial creation 
#                    2021_Oct-11  Lixin Sun  Moved mosaic creation outside this function. This ensure the
#                                            same mosaic image can be used for generating different products.
#                    2021-Oct-15  Lixin Sun  Modified so that peak season ("month" argument is outside of 
#                                            1 and 12) product can also be generated. 
#############################################################################################################
def one_LEAF_Product(mosaic, PROD_name, month, Param_dict, mapBounds, output, task_list):
  '''Produces one LEAF product for a specified month of a year

    Args:
       mosaic (eeImage): A given mosaic image from which a specified product will be generated;
       PROD_name(string): A specified product name string (e.g., 'LAI' or 'fCOVER');
       month(int or string): A targeted month (either an integer or a string). If month value is outside of
                             1 and 12, then a peak season product will be created.
       Param_dict(dictionary): A dictionary storing other required running parameters;
       mapBounds(ee.Geometry): The spatial ragion of a LEAF product map;
       output (Bool): The flag indication if to export results;
       task_list([]): A list for storing the links to exporting tasks.'''  

  #==========================================================================================================
  # Get GEE Data Catalog name corresponding to a given sensor type code
  #==========================================================================================================
  CollName = eoImg.GEE_catalog_name(Param_dict['sensor'], eoImg.sur_ref)  

  #==========================================================================================================
  # Create vegetation parameter map based on the mosaic image, classification map and hyperparameters
  #==========================================================================================================
  partition = (COLL_OPTIONS[CollName]["partition"]).filterBounds(mapBounds).mosaic().rename('partition')
  numNets   = ee.Number(ee.Feature((COLL_OPTIONS[CollName]["Network_Ind"]).first()).propertyNames().remove('Feature Index').remove('system:index').remove('lon').size())

  SL2P_net = ee.List.sequence(1, ee.Number(COLL_OPTIONS[CollName]["numVariables"]), 1) \
                    .map(lambda netNum: makeNetVars(COLL_OPTIONS[CollName]["Collection_SL2P"], numNets, netNum))
    
  errorsSL2P_net = ee.List.sequence(1, ee.Number(COLL_OPTIONS[CollName]["numVariables"]), 1) \
                     .map(lambda netNum: makeNetVars(COLL_OPTIONS[CollName]["Collection_SL2Perrors"], numNets, netNum))

  print('<one_LEAF_Product> PROD_name and CollName = ', PROD_name, CollName)
  CollOptions     = COLL_OPTIONS[CollName]  #Dictionay related to a selected collection type
  ProdOptions     = PROD_OPTIONS[PROD_name] #Dictionay related to a selected production and collection type  

  estimateSL2P    = wrapperNNets(SL2P_net,       partition, ProdOptions, CollOptions, "estimate", mosaic)
  uncertaintySL2P = wrapperNNets(errorsSL2P_net, partition, ProdOptions, CollOptions, "error",    mosaic)
  
  print('<one_LEAF_Product> estimate cube band names = ', estimateSL2P.bandNames().getInfo())
  print('<one_LEAF_Product> error cube band names = ', uncertaintySL2P.bandNames().getInfo())

  #==========================================================================================================
  # Select the product bands and then rescale them
  #==========================================================================================================
  estimateImage = estimateSL2P.select([0])
  errorImage    = uncertaintySL2P.select([0])
  networkID     = estimateSL2P.select(['networkID']).toUint8()

  if PROD_name == 'Albedo' or PROD_name == 'fAPAR' or PROD_name == 'fCOVER':
    scaling_factor = ee.Image(200);  #Could be 255, but 200 is easy to remember
  elif PROD_name == 'LAI':
    scaling_factor = ee.Image(20);   #Modified on Jan. 28, 2021
  
  estimateImage = estimateImage.where(estimateImage.lt(ee.Image(0.0)), ee.Image(0.0))        
  estimateImage = estimateImage.multiply(scaling_factor).toUint8()
  errorImage    = errorImage.multiply(scaling_factor).toUint8()
  
  #==========================================================================================================
  # Set the estimates and uncertainties of water pixels to zero
  #==========================================================================================================
  estimateImage = estimateImage.where(partition.eq(ee.Image(18)), ee.Image(0))
  errorImage    = errorImage.where(partition.eq(ee.Image(18)), ee.Image(0))

  if output == True:
    export_LEAF_Products(PROD_name, month, Param_dict, mapBounds, estimateImage, errorImage, task_list)





#############################################################################################################
# Description: The start/main function for operationally producing vegetation parameter maps with LEAF Tool
#
# Revision history:  2021-May-20  Lixin Sun  Initial creation 
#
#############################################################################################################
def LEAF_tool_main(Param_dict):
  '''Produces one or more vegetation parameter maps for a specific region using the images acquired within 
     one or multiple months

     Args:
       Param_dict(Dictionary): A dictionary storing the parameters required for running LEAF Toolbox.'''
  #==========================================================================================================
  # Get spatial region geometry. Generate one spatial region and then pass it to other function. This way 
  # ensures all the processes use the same spatial region.
  #==========================================================================================================
  TileName = Param_dict['tile_name']
  if eoTG.is_valid_tile_name(TileName) == True:
    mapBounds = eoTG.PolygonDict.get(TileName)      
  else:
    mapBounds = eoTG.custom_RegionDict.get(TileName)
    
  #mapBounds = eoTG.PolygonDict.get(Param_dict['tile_name'])  
  #mapBounds = eoTG.SmallRegion  

  mapBounds = eoTG.expandMosaicPolygon(mapBounds, 0.02)
  print('<LEAF_tool_main> map boundary = ', mapBounds.getInfo())  

  #==========================================================================================================
  # Two Loops through months and product names
  # Note that, for the same month, one mosaic can be reused for generating different products. 
  #==========================================================================================================
  task_list = []

  for month in Param_dict['months']:
    mosaic = LEAF_Mosaic(Param_dict, month, mapBounds)    
    export_LEAF_ancillaries(mosaic, month, Param_dict, mapBounds, task_list)

    for prod in Param_dict['prod_names']:      
      one_LEAF_Product(mosaic, prod, month, Param_dict, mapBounds, True, task_list)

  return task_list