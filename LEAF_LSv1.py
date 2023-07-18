import ee 

import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import export_text
pd.options.mode.chained_assignment = None  # default='warn'




###################################################################################################
# Description: This function returns a ee.Feature object that was generated with 'inKey' and its
#              corresponding value in the given dictionary (inDict).
# 
# Revision history:  2023-Jan-19  Lixin Sun  Initial creation 
#
###################################################################################################
def DictItem2Feature(inKey, inDict):
  val = ee.Dictionary(inDict).get(inKey)
  return ee.Feature(ee.Geometry.Point([0,0]), {'keys': inKey, 'value': val})




###################################################################################################
# Description: This function returns filtered unique sub-tree numbers
# 
# Revision history:  2022-???-??  Richard Fernandes  Initially created in JavaScript 
#                    2023-Jan-05  Lixin Sun  Converted from Richard's JavaScript code
#                    2023-Jan-19  Lixin Sun  Modified so that some child code corresponding small
#                                            number of pixels will be filtered out.          
###################################################################################################
def uniqueValues(Image, Region, Thresh):
  '''
     Args:
        Image(ee.Image): A given image containing only one band named as 'childNames' 
        Region(ee.Geometry): A goemetry region corresponding to the given image;
        Thresh(float): A threshold on the number of pixels corresponding to a child code.'''
  image  = ee.Image(Image)
  region = ee.Geometry(Region)

  #================================================================================================
  # Create a histogram that counts the frequency for each child number 
  #================================================================================================
  reduction = image.reduceRegion(reducer = ee.Reducer.frequencyHistogram(), 
                                 geometry = region,
                                 bestEffort = True,
                                 scale = 30,    
                                 tileScale = 4) 

  histogram = ee.Dictionary(reduction.get(reduction.keys().get(0)))

  #================================================================================================
  # Convert the histogram dictionary to a feature collection
  #================================================================================================
  dict_keys    = ee.List(histogram.keys())  
  histogram_FC = ee.FeatureCollection(dict_keys.map(lambda key: DictItem2Feature(key, histogram)))
  
  #================================================================================================
  # Filter the feature collection
  #================================================================================================
  short_FC = histogram_FC.filter(ee.Filter.gt('value', Thresh))

  #================================================================================================
  # Return the key values in the filtered feature collection
  #================================================================================================
  values = ee.FeatureCollection(short_FC).aggregate_array('keys').map(lambda key: ee.Number.parse(key)) 
  #print('\n\n<uniqueValues> final values = ', values.getInfo())

  return values




###################################################################################################
# Description: This function creates an image where each band is the numerical value from a list
#              of strings
#
# Revision history:  2022-???-??  Richard Fernandes  Initially created in JavaScript 
#
###################################################################################################
def stringListtoImage(stringList):
  '''Creates an image where each band is the numerical value from a list of strings
     Args: 
       stringList(ee.List): a list of number strings.'''

  # convert strigs to number and zip it to a dictionry
  numList   = ee.List(stringList).map(lambda x: ee.Number.parse(x))
  indexList = ee.List.sequence(1, numList.size()).map(lambda x: ee.Number(x).format('%d'))

  # create an image collection and flatten in correct order
  return ee.Dictionary.fromLists(indexList, numList).toImage(indexList)




###################################################################################################
# Description: This function 
#
# Revision history:  2022-???-??  Richard Fernandes  Initially created in JavaScript 
#                    2023-Mar-08  Lixin Sun  Changed the second set of scaling factors from 
#                                            ('10000,10000,1,1,1') to ('10000,10000,10000,10000,10000')
#
###################################################################################################
def ParentPredict(Image, ParentFC):
  '''Applies a RF and returns response.
     Args:
       image(ee.Image): A given ee.Image object. Subregions have been defined by caller;
       methodFC(ee.FeatureCollection): A single feature collection containing RF models.'''

  image    = ee.Image(Image)         # Note that subregions have been defined
  parentFC = ee.FeatureCollection(ParentFC)

  #================================================================================================
  # select inputs scale the image and rename to RF regressors
  #================================================================================================
  params     = parentFC.first()    # Get the first feature in the given feature collection  
  tree_str   = ee.String(parentFC.first().get('tree')).replace("#", "\n", "g")
  classifier = ee.Classifier.decisionTree(tree_str)  

  out_img = image.select(ee.String(params.get('regressorsGENames')).split(',')) \
                        .multiply(stringListtoImage(ee.String(params.get('regressorsGEScaling')).split(','))) \
                        .add(stringListtoImage(ee.String(params.get('regressorsGEOffset')).split(','))) \
                        .multiply(stringListtoImage(ee.String('10000,10000,10000,10000,10000').split(','))) \
                        .rename(ee.String(params.get('regressors')).split(',')) \
                        .round() \
                        .classify(classifier)  # Conduct DT-based classification 
  
  return out_img





###################################################################################################
# Description: This function 
#
# Revision history:  2022-???-??  Richard Fernandes  Initially created in JavaScript 
#                    2023-Mar-08  Lixin Sun  Changed the second set of scaling factors from 
#                                            ('10000,10000,1,1,1') to ('10000,10000,10000,10000,10000')
#
###################################################################################################
def ChildPredict(Image, childFC):
  '''Applies a RF and returns response.
     Args:
       image(ee.Image): A given ee.Image object. Subregions have been defined by caller;
       methodFC(ee.FeatureCollection): A single feature collection containing RF models.'''

  image   = ee.Image(Image)         # Note that subregions have been defined
  childFC = ee.FeatureCollection(childFC)

  #================================================================================================
  # select inputs scale the image and rename to RF regressors
  #================================================================================================
  params     = childFC.first()    # Get the first feature in the given feature collection    
  #classifier = childFC.get('RF')  #.setOutputMode('REGRESSION')
  
  image = image.select(ee.String(params.get('regressorsGENames')).split(',')) \
                        .multiply(stringListtoImage(ee.String(params.get('regressorsGEScaling')).split(','))) \
                        .add(stringListtoImage(ee.String(params.get('regressorsGEOffset')).split(','))) \
                        .multiply(stringListtoImage(ee.String('10000,10000,10000,10000,10000').split(','))) \
                        .rename(ee.String(params.get('regressors')).split(',')) \
                        .round() 
                        #.classify(classifier)  # Conduct DT-based classification 
  
  #================================================================================================
  # Create a list of Decision Tree classifiers from the tree text strings in "childFC" 
  #================================================================================================
  tree_strings   = childFC.aggregate_array("tree").map(lambda str: ee.String(str).replace("#", "\n", "g"))

  DT_classifiers = tree_strings.map(lambda tree: ee.Classifier.decisionTree(tree))
  result_imgs = DT_classifiers.map(lambda classifier: ee.Image(image.classify(classifier)).float())

  return ee.ImageCollection(result_imgs).reduce(ee.Reducer.mean())





###################################################################################################
# Description: This function applies an identified child RF to the regions of a given image.
#
# Revision history:  2022-???-??  Richard Fernandes  Initially created in JavaScript 
#                    2023-Mar-09  Lixin Sun  Changed scaling factor from 1000 to 2 and the data
#                                            type of the returned image from Int16 to Uint8. 
#             
###################################################################################################
def applyChildRF(Image, MethodFC, ChildName):
  '''Applies an identified child feature collection to subregions of a given image.

  Args:
    Image(ee.Image): A targeted image/mosaic;
    MethodFC(ee.List): A list of method feature collection;
    ChildName(Integer): An integer number representing a child FC.'''
  image     = ee.Image(Image)
  methodFC  = ee.List(MethodFC)   # A list of the ee.FeatureCollection objects of all children 
  childName = ee.Number(ChildName)
  
  #Apply a pixel mask to the given image/mosaic
  maskedImg = image.updateMask(image.select('childNames').eq(childName))  

  # Select ONE feature collection corresponding to a specified child 
  # The feature collection a number of trees (Random Forest) for one child 
  uesd_child = methodFC.filter(ee.Filter.stringContains('system:id', childName.format("%d"))).get(0)
  
  return ChildPredict(maskedImg, uesd_child).rename('estimate')    #scaling factor = 20




###################################################################################################
# Description: This function lists all the RFs in GEE assets that have string length bigger than 
#              a specified number.
#
# Revision history:  # Revision history:  2023-Mar-27  Lixin Sun  Initial creation
#             
###################################################################################################
def investigateMethod(MethodName, DirectoryName, lenThresh=3000000):
  '''Constructs method/algorithm based on the data stored on GEE assets.

     Args:
       MethodName(string): A method name string;
       DirectoryName): The name string for a GEE assets directiory storing random Forest trees.'''
  #================================================================================================
  # Create a list of GEE asset names 
  # Note: the return of "ee.data.listAssets" function is a Python Dictionary with only one key 
  # called "assets", which corresponds another Python list containing dictionary objects.
  #================================================================================================
  methodName    = str(MethodName)
  directoryName = str(DirectoryName)

  raw_asset_list = ee.data.listAssets({'parent': directoryName})['assets']
  #print('<constructMethod> numb of keys = ',raw_asset_list)
  #================================================================================================
  # Create a list of ee.FeatureCollection objects from a GEE assets list of directories
  #================================================================================================
  client_asset_list = []
  for asset in raw_asset_list:
    client_asset_list.append(ee.FeatureCollection(asset['name']))

  assetList = ee.List(client_asset_list)
  #print('<constructMethod> one asset :', ee.FeatureCollection(assetList.get(100)).get('system:id'))
    
  #================================================================================================
  # Attache sub-trees to each PARENT FeatureCollection object
  #================================================================================================
  def getSysID(oneFC):   
    return ee.String(ee.FeatureCollection(oneFC).get('system:id'))

  
  def getTreeSize(oneFC):   
    sys_ID = ee.String(ee.FeatureCollection(oneFC).get('system:id'))
    all_sizes = ee.FeatureCollection(oneFC).aggregate_array("tree").map(lambda str: ee.String(str).length())

    child_size = all_sizes.reduce(ee.Reducer.sum())

    return [sys_ID, child_size]

  def filter_small_tree(aRF_size):
    ee_list = ee.List(aRF_size)
    return ee.Algorithms.If(ee.Number(ee_list.get(1)).gt(lenThresh), aRF_size, ee.String(''))

  #SysID_list    = assetList.map(lambda oneFC: getSysID(oneFC))
  TreeSize_list = assetList.map(lambda oneFC: getTreeSize(oneFC))
  
  large_RFs = TreeSize_list.map(lambda aRF: filter_small_tree(aRF)).distinct()

  #asset_tree_info = ee.Dictionary.fromLists(SysID_list, TreeSize_list)
  for indx in range(1, large_RFs.size().getInfo()):
    print(large_RFs.get(indx).getInfo())
  



###################################################################################################
# Description: This function deletes all the GEE assets under a folder.
#
# Revision history:  2023-Mar-27  Lixin Sun  Initial creation
#             
###################################################################################################
def deleteGEEAsset(DirectoryName):
  '''Constructs method/algorithm based on the data stored on GEE assets.

     Args:
       MethodName(string): A method name string;
       DirectoryName): The name string for a GEE assets directiory storing random Forest trees.'''
  #================================================================================================
  # Create a list of GEE asset names 
  # Note: the return of "ee.data.listAssets" function is a Python Dictionary with only one key 
  # called "assets", which corresponds another Python list containing dictionary objects.
  #================================================================================================
  directoryName  = str(DirectoryName)
  raw_asset_list = ee.List(ee.data.listAssets({'parent': directoryName})['assets'])
  print('<deleteGEEAsset> all assets = ',raw_asset_list)
  
  list_length = raw_asset_list.length().getInfo()
  for indx in range(0, list_length):
    asset_id = ee.Dictionary(raw_asset_list.get(indx)).get('id')
    #print(asset_id.getInfo())
    ee.data.deleteAsset(asset_id.getInfo())
  




###################################################################################################
# Description: This function constructs method/algorithm based on the data stored on GEE assets 
#
# Revision history:  2022-???-??  Richard Fernandes  Initially created in JavaScript 
#
###################################################################################################
def constructMethod(MethodName, DirectoryName):
  '''Constructs method/algorithm based on the data stored on GEE assets.

     Args:
       MethodName(string): A method name string;
       DirectoryName): The name string for a GEE assets directiory storing random Forest trees.'''
  #================================================================================================
  # Create a list of GEE asset names 
  # Note: the return of "ee.data.listAssets" function is a Python Dictionary with only one key 
  # called "assets", which corresponds another Python list containing dictionary objects.
  #================================================================================================
  methodName     = str(MethodName)
  directoryName  = str(DirectoryName)

  raw_asset_list = ee.data.listAssets({'parent': directoryName})['assets']
  #print('<constructMethod> numb of keys = ',raw_asset_list)
  #================================================================================================
  # Create a list of ee.FeatureCollection objects from a GEE assets list of directories
  #================================================================================================
  client_asset_list = []
  for asset in raw_asset_list:
    client_asset_list.append(ee.FeatureCollection(asset['name']))

  assetList = ee.List(client_asset_list)
  #print('<constructMethod> one asset :', ee.FeatureCollection(assetList.get(1)).propertyNames().getInfo())
  
  #================================================================================================
  # Create a LIST of all PARENT FeatureCollection objects 
  #================================================================================================  
  parentList = assetList.filter(ee.Filter.stringContains('system:id', methodName)) \
                        .filter(ee.Filter.stringContains('system:id','parent')) 
  #print('\n\n\n<constructMethod> All parent trees:', ee.List(parentList).get(0).getInfo())
  
  #================================================================================================
  # Attache sub-trees to each PARENT FeatureCollection object
  #================================================================================================
  def AddChilds(parentFC):   
    '''Attach all child trees to a parent FC, which contains only one feature''' 
    parent_id    = ee.String(ee.FeatureCollection(parentFC).get('system:id')).slice(0,-8)

    all_children = assetList.filter(ee.Filter.stringContains('system:id', parent_id)) \
                            .filter(ee.Filter.stringContains('system:id','child')) 
    
    return ee.FeatureCollection(parentFC).set('childFCList', all_children)

  AllMethodList = parentList.map(lambda parentFC: AddChilds(parentFC))
  #print('\n\n<constructMethod> All parents and children trees:', AllMethodList.get(0).getInfo())
  
  # CL - add property "biomeNumber" to each element in "AllMethodList" by parsing the ID
  AllMethodList = AllMethodList.map(lambda method: ee.FeatureCollection(method).set('biomeNumber', \
                          ee.Number.parse(ee.String(ee.FeatureCollection(method).get('system:id')).slice(-9,-8))))

  return AllMethodList





###################################################################################################
# Description: This function divides a given List into a number of sublists and return them as the
#              elements of an exterior list. This function was developed to deal with the issue
#              related to too many unique subtree values.
#
# Revision history:  2023-Feb-24  Lixin Sun  Initial creation
#
###################################################################################################
def divide_unique_values(unique_subtree_values, Interval):
  '''Divides a given List into a number of sublists and return them as the elements of an exterior list.

     Args:
       unique_subtree_values(ee.List): A list of subtree values;
       Interval(Int or ee.Number): A interval of the division.'''

  inList        = ee.List(unique_subtree_values)
  ListSize      = inList.size()
  start_indices = ee.List.sequence(0, ListSize, Interval)

  return start_indices.map(lambda start: inList.slice(start, ee.Number(start).add(Interval)))



###################################################################################################
# Description: This function creates estimations for a number of subtree values that is normally
#              less than 30 
#
# Revision history:  2023-Feb-24  Lixin Sun  Initial creation
#
###################################################################################################
def estimateSubResponse(subList, child_FC_list, BiomeID, Image):
  '''Divides a given List into a number of sublists and return them as the elements of an exterior list.

     Args:
       subList(ee.List): A list of integers;
       child_FC_list():
       BiomeID(Integer, ee.Number): A specified biome ID
       Image(ee.Image): A given image/mosaic.'''

  image   = ee.Image(Image)
  biomeID = ee.Number(BiomeID)

  estimated_imgs = ee.List(subList).map(lambda chld_name: applyChildRF(image, child_FC_list, chld_name))
  #print('\n\n<estimateResponse> number of estimated layers :', ee.ImageCollection(estimated_imgs).size().getInfo())

  #================================================================================================
  # Merge all the estimated images into one 
  #================================================================================================
  # Remove mask from each estimated image
  estimated_imgs = estimated_imgs.map(lambda image: ee.Image(image).unmask())
  #print('\n\n<estimateResponse> numb of images:', estimated_imgs.size().getInfo())

  out_img = ee.ImageCollection(estimated_imgs).max()

  return out_img
  #================================================================================================
  # Apply the mask of the identified biome and then return the resultant image
  #================================================================================================
  #return out_img.updateMask(image.select('biome').eq(biomeID))   #.clip(region)




###################################################################################################
# Description: This function filters out the child names that do not have corresponding RF trees
#
# Revision history:  2023-Feb-24  Lixin Sun  Initial creation
#
###################################################################################################
def filter_childNames(MethodFC, childNames):
  '''
    MethodFC(ee.List): all feature collection corresponding to one biome
    childName(integer): The ID of a child
  '''
  methodFC    = ee.List(MethodFC)
  child_names = ee.List(childNames)
    
  def check_one_child(methodFC, oneName):
    name    = ee.Number(oneName)
    uesd_RF = ee.List(methodFC.filter(ee.Filter.stringContains('system:id', name.format("%d"))))
    
    return ee.Algorithms.If(uesd_RF.size().gt(0), name, -1)
    
  valid_names = child_names.map(lambda aName: check_one_child(methodFC, aName))
    
  return valid_names.filter(ee.Filter.gt('item', 0))





###################################################################################################
# Description: This function estimates a BioParameter map for ONE biome type based on an 
#              image/mosaic by applying a pre-created RF model.
#
# Revision history:  2022-???-??  Richard Fernandes  Initially created in JavaScript 
#
###################################################################################################
def BiomeEstimate(Method, BiomeID, Image, Region):
  '''Estimates a BioParameter map for a given image/mosaic by applying a pre-created RF model.

     Args:
       Method(ee.List): A list of RF models;
       BiomeID(ee.Number): An integer representing a specified biome ID;
       Image(ee.Image): A given image/mosaic, based on which a bioparameter map will be estimated;
       Region(ee.Geometry): A ee.Geometry object defining the region of the image/mosaic.'''
  
  method  = ee.List(Method)
  image   = ee.Image(Image)
  biomeID = ee.Number(BiomeID)
  region  = ee.Geometry(Region)

  #================================================================================================
  # Cassidy Li - match biomeID to method property "biomeNumber"
  # Select a RF model based on a given "BiomeID", which can also be regarded as a parent ID
  #================================================================================================
  biome_method = ee.FeatureCollection(method.filter(ee.Filter.eq('biomeNumber', biomeID)).get(0))
  #print('\n\n\n<estimateResponse> number of used_methods = ', biome_method.size().getInfo())

  #================================================================================================
  # Extract all child RF models associated with a specified biome
  #================================================================================================
  child_FC_list = biome_method.get('childFCList')

  #================================================================================================
  # Attach a child name band to a given image/mosaic based on the predictions of a parent RF 
  #================================================================================================
  parent_biomap = ParentPredict(image, biome_method)
  image = image.addBands(parent_biomap.multiply(1000).round().rename('childNames')) 

  parent_biomap = parent_biomap.updateMask(image.select('biome').eq(biomeID))  

  #================================================================================================
  # Determine a set of unique values representing different child RF models
  #================================================================================================
  unique_subtree_values = uniqueValues(image.select('childNames'), region, 0)  
  #print('unique_subtree values before filtering = ', unique_subtree_values.getInfo())

  # Filter out the child numbers that do not have corresponding child RF
  valid_child_values = filter_childNames(child_FC_list, unique_subtree_values)  
  #print('valid_subtree values = ', valid_child_values.getInfo())
  #return parent_biomap.float().rename('estimate') 

  #for child in valid_child_values:
  #  print("<BiomeEstimate> child code:", child)
  #  applyChildRF(image, child_FC_list, child)

  #================================================================================================
  # Estimate a set of images by applying the child RFs corresponding to all unique child values 
  #================================================================================================  
  estimated_imgs = valid_child_values.map(lambda oneName: applyChildRF(image, child_FC_list, oneName))

  #================================================================================================
  # Merge the estimated images into one image 
  #================================================================================================
  # Remove mask from each estimated image
  estimated_imgs = estimated_imgs.map(lambda image: ee.Image(image).unmask())
  out_img = ee.ImageCollection(estimated_imgs).max()

  #================================================================================================
  # Apply the mask of the identified biome and then return the resultant image
  #================================================================================================
  return out_img.updateMask(image.select('biome').eq(biomeID))






#############################################################################################################
# Code the input feature domain by using a linear hash for each row of the input data frame
# the hash algorithm converts each input row into an integer from 0 to 9 by applying the provided scale and 
# offset and then rounding is then produces a hash entry for each row by packing the integers consequitively
# to form a uint64 code.
# This implies a limit of at most 18 columns for the input data frame.
# returns a list corresonding to hash table of unique coded input rows
#############################################################################################################
def makeDomain(df, domainIndex, domainScaling, domainOffset):
  '''
  '''
  df = np.array(df) 

  if df.shape[1] < 19 :
    domainIndex = np.array(domainIndex)
    domainScaling = np.array(domainScaling)
    domainOffset = np.array(domainOffset)
  else:
    raise ValueError("More than 18 dimensions in domain")
  
  return np.uint64(np.unique(np.sum(np.clip(np.around(df* domainScaling + domainOffset,0),0,9) * np.power(10,np.cumsum(domainIndex)-domainIndex[0]),1),0)).tolist()




#############################################################################################################
# parse a sckitlearn decision tree into a R text tree suitable for use in GEE
# for compactness ancillary items like node sample size and residuals are forced to = 1
# this is a blind guess by Richard but seems to work
#############################################################################################################
def make_tree(rf, regressors, decimals=3, maxDepth=10):
  '''
  rf(): A trained random forest
  '''
  # first get the output in sckitlearn text format in a dataframe
  r = export_text(decision_tree=rf,feature_names=regressors,show_weights=True,decimals=decimals,max_depth=maxDepth)
  r = r.splitlines()
  rdf = pd.DataFrame(r,columns = ['rule'])
    
  #identify rules and not leaf values
  isrule = ~rdf['rule'].str.contains('value')
  rulesdf = rdf.loc[isrule]
    
  #determine level in tree and the associated starting based node number
  rdf['level'] = rdf['rule'].str.count(r'(\|)').values.tolist()
  rdf.loc[isrule,'base'] = ((rdf.level).mul(0).add(2)).pow(rdf.level)

  # get the actual tested condition
  rdf.loc[isrule,'condition'] =  rdf.loc[isrule,'rule'].str.extract(r'(x.+)').values.tolist()
    
  # identify leaf nodes and fill in the response value
  rdf.loc[~isrule,'leaf'] = '*'
  rdf['leaf'] = rdf['leaf'].fillna(method='bfill',limit=1)
  rdf.loc[~isrule,'response'] = rdf.loc[~isrule,'rule'].str.extract(r'([+-]?([0-9]*[.])?[0-9]+)')[0].values.tolist()
  rdf['response'] = rdf['response'].fillna(method='bfill')
    
  #discard non rules
  rdf.loc[rdf['leaf'].isna(),'leaf'] = ' '
  rdf = rdf.dropna()

  #dtermine if this is a left or right branch
  rdf['branch'] = rdf['rule'].str.contains(r'(?:\>)').astype('int')
  rdf['node'] = rdf.base + rdf.branch
  rdf.loc[rdf.level==1,'node']=rdf.loc[rdf.level==1,'branch'] + 2
  rdfindex = rdf.index
    
  #asign a node number, this is non trivial and critical for use later
  #read https://www.r-bloggers.com/2022/10/understanding-leaf-node-numbers-when-using-rpart-and-rpart-rules/
  for row in range(2,rdf.shape[0]):
    # find the nearest row above
    df = rdf[0:row]
    if ( (rdf[row:row+1].level.values)[0] > 1 ):
      parentdf = df.loc[df.level == (rdf[row:row+1].level.values-1)[0]].iloc[-1]
      rdf.at[rdfindex[row],'parentbase'] = parentdf.base  
      rdf.at[rdfindex[row],'parentnode'] = parentdf.node  
      rdf.at[rdfindex[row],'node'] = rdf.iloc[row].node + 2 * (  parentdf.node - parentdf.base ) 
    
  # glue together each rule in a big string, add the root node and return as a list
  rdf['phrase'] = rdf.apply(lambda x:  ' ' *(2 * x.level) + str(int(x.node)) + ') ' + x.condition + ' 0 0 ' + str(x.response) + ' ' +x.leaf + '\n', axis=1)
  return ( '1) root 1 1 1 (1)\n'+''.join(rdf['phrase'].values.tolist()))



#############################################################################################################
# Description: This function exports trees to GEE assets as FeatureCollections 
# Note:        This function was taken from the GEEMAP libraries and modified as needed here
#############################################################################################################
def export_trees_to_fc_CCRS(trees,response,regressors,regressorsGEECollectionName,regressorsGEENames,responseGEEScaling,responseGEEOffset,regressorsGEEScaling2, \
                            regressorsGEEScaling,regressorsGEEOffset,domain,domainScaling,domainOffset,asset_id,description="geemap_rf_export"):

  """Function that creates a feature collection with a property tree which contains the string representation of decision trees and exports to ee asset for later use
        together with CCRS tree properties
    args:
        trees (list[str]): list of string representation of the decision trees
        response (str): name of response variable
        regressors (list[str]): list pf strings of names of regressors variables in the created trees
        regressorsGEECollectionName (str) : name of GEE input collection
        regressorsGEENames (list[str]): list of names of the regressors variables in the GEE input collection
      	responseGEEScaling (list[float]): list of scaling values to apply to GEE output image
        responseGEEOffset (list[float]): list of  offset values to apply to GEE output image
        regressorsGEEScaling2 (list[float]): list of scaling values to apply to GEE input collection after initial scale ad offset is applied
        regressorsGEEScaling (list[float]): list of scaling values to apply to GEE input collection
        regressorsGEEOffset (list[float]): list of  offset values to apply to GEE input collection
        domain (list[uint64]): list of domain code values
        domainScaling (list[float]) : list of scaling values to create domain
        domainOffset ( list[float]): list of offset values to create domain
        asset_id (str): ee asset id path to export the feature collection to

    kwargs:
        description (str): optional description to provide export information. default = "geemap_rf_export"
  """
  # create a null geometry point. This is needed to properly export the feature collection
  null_island = ee.Geometry.Point([0, 0])

  # create a list of feature over null island
  # set the tree property as the tree string
  # encode return values (\n) as #, use to parse later
    
  features = [
        ee.Feature(null_island, {"tree": tree.replace("\n", "#"),\
                                 "response": ','.join(response),\
                                 "regressors": ','.join(regressors),\
                                 "regressorsGEECollectionName":regressorsGEECollectionName,\
                                 "regressorsGENames": ','.join(regressorsGEENames),\
                                 "responseGEScaling": ','.join(str(x) for x in responseGEEScaling),\
                                 "responseGEOffset": ','.join(str(x) for x in responseGEEOffset),\
                                 "regressorsGEScaling2": ','.join(str(x) for x in regressorsGEEScaling2),\
                                 "regressorsGEScaling": ','.join(str(x) for x in regressorsGEEScaling),\
                                 "regressorsGEOffset": ','.join(str(x) for x in regressorsGEEOffset),\
                                 # "domain": ','.join(str(x) for x in domain),\
                                 "domainScaling": ','.join(str(x) for x in domainScaling),\
                                 "domainOffset": ','.join(str(x) for x in domainOffset)} ) for tree in trees]
    
  # cast as feature collection
  fc = ee.FeatureCollection(features)

  # get export task and start
  task = ee.batch.Export.table.toAsset(collection=fc, description=description, assetId=asset_id)
  
  task.start()



#############################################################################################################
# This function currently is not called by any other function
#############################################################################################################
def strings_to_classifier(trees=None,outputMode='REGRESSION'):
  """Function that takes string representation of decision trees and creates a ee.Classifier that can be used with ee objects

    args:
        trees (list[str]): list of string representation of the decision trees
        outputMode [str] : classifier output mode
    returns:
        classifier (ee.Classifier): ee classifier object representing an ensemble decision tree
  """

  # convert strings to ee.String objects
  ee_strings = [ee.String(tree) for tree in trees]

  # pass list of ee.Strings to an ensemble decision tree classifier (i.e. RandomForest)
  classifier = ee.Classifier.decisionTreeEnsemble(ee_strings).setOutputMode(outputMode)

  return classifier


#############################################################################################################
# This function currently is not called by any other function
# Get list of all intercomaprison feature collections
#############################################################################################################
def get_asset_list(parent):
  parent_asset = ee.data.getAsset(parent)
  parent_id = parent_asset['name']
  parent_type = parent_asset['type']
  asset_list = []
  child_assets = ee.data.listAssets({'parent': parent_id})['assets']

  for child_asset in child_assets:
    child_id = child_asset['name']
    child_type = child_asset['type']
    if child_type in ['FOLDER','IMAGE_COLLECTION']:
      # Recursively call the function to get child assets
      asset_list.extend(get_asset_list(child_id))
    else:
      asset_list.append(child_id)

  return asset_list



#############################################################################################################
# construct hierarchal random forests for FTL method
# hierarchicalRF(calbiomeDictLAIFTL,calbiomeDictLAINAIVE, regressors, regressorsGEENames, response, \
#                                   domainScaling, domainOffset, 
#                                   maxDepthParent=10, maxDepthChild=15, minSamplesSplit=2,\
#                                   maxleafnodesParent=999, minSamplesLeafParent=200, \
#                                   maxleafnodesChild= 999, minSamplesLeafChild=50, \
#                                   maxFeatures=4, nTrees = 50)
#############################################################################################################
def hierarchicalRF(dataDictParent, dataDictChild,regressorsNames,regressorsGEENames, response, \
                   domainScaling, domainOffset, \
                   maxDepthParent     =20,    maxDepthChild =20, minSamplesSplit=11, \
                   maxleafnodesParent = 100,  minSamplesLeafParent = 10, \
                   maxleafnodesChild  = 999,  minSamplesLeafChild  = 10, \
                   maxFeatures = "auto", nTrees = 100):
  '''
  dataDictParent(Dictionary): A dictionary containing data sets for training parent RFs;
  dataDictChild(Dictionary): A dictionary containing data sets for training child RFs;
  regressorsNames(List): A list of logical names of input parameters(e.g., ['red','NIR','cosSZA','cosVZA','cosSA']);
  regressorsGEENames(List): A list of names really used in GEE for input parameters(e.g., ['SR_B4', 'SR_B5','cosSZA','cosVZA','cosSA']);
  response(List): A list of biophysical parameter names (e.g., ['LAI', 'fAPAR]');
  domainScaling(List): A list of domain scalings;
  domainOffset(List): A list of domain offsets;
  '''  
  #==========================================================================================================
  # make generic names for regressors for use in GEE
  # e.g., convert whatever regressor names to ['x1', 'x2', ..., 'xn']
  #==========================================================================================================
  regressors = []
  for item in np.arange(1,len(regressorsNames)+1,1):
    regressors.append('x' + str(item))

  #==========================================================================================================
  # Calibrate hierarchal randforest preeidctors for each biome
  #==========================================================================================================
  for biome in dataDictParent.keys(): 
    print('biome:',biome)

    # subset only the regressors and response columns
    dfBiome  = dataDictChild [biome]['DF'][sum([regressorsNames, response],[])].astype('int')   
    dfParent = dataDictParent[biome]['DF'][sum([regressorsNames, response],[])].astype('int')

    dfBiome.columns  = sum([regressors,response],[])
    dfParent.columns = sum([regressors,response],[])
    print('Total size of the data frame for child RF = ', dfBiome.shape)
    print('Parent size  of the data frame for parent RF = ',dfParent.shape)
    
    # Merge the two data frames into one 
    DFs     = [dfBiome, dfParent]
    
    # populate a parent RF dictionary that holds a single tree RF used to partition data into child RFs
    parentRFDict = {}
    parentRFDict.update({'regressors': regressors})
    parentRFDict.update({'regressorsGEE': regressorsGEENames})
    parentRFDict.update({'response': response})
    parentRFDict.update({'domain':makeDomain(dfBiome[regressors], domainIndex, domainScaling,domainOffset)})
    parentRFDict.update({'RF': RandomForestRegressor(n_estimators=1, \
                                                     min_samples_leaf = minSamplesLeafParent, \
                                                     min_samples_split=minSamplesSplit, \
                                                     bootstrap=False, \
                                                     random_state=0, \
                                                     verbose=0, \
                                                     max_depth=maxDepthParent, \
                                                     max_leaf_nodes=maxleafnodesParent, \
                                                     max_features=maxFeatures, \
                                                     n_jobs=40) \
                              .fit(dfParent[regressors], np.array(dfParent[response]).ravel())})
    
    # label input data using the prediction from the parent RF as this will be unique
    dfBiome['estimate']=np.around(np.array(parentRFDict['RF'].predict(dfBiome[regressors])),decimals=3)

    # populate dictionary of children RFs, each childRF is itself a dictionary similar to the parentRF but now using more than one tree
    # each child is labelled using the prediction value from the parentRF corresponding to its partition
    childrenRFDict = {}
    print('number children:',np.unique(np.around(np.array(parentRFDict['RF'].predict(dfBiome[regressors])),decimals=3)).size)
    for partition in np.unique(np.around(np.array(parentRFDict['RF'].predict(dfBiome[regressors])), decimals=3)):
      dfpartitionBiome = dfBiome.loc[dfBiome['estimate'] == partition]
      childRFDict = {}
      childRFDict.update({'size': dfpartitionBiome[response].shape[0]})
      childRFDict.update({'regressors': regressors})
      childRFDict.update({'regressorsGEE': regressorsGEENames})
      childRFDict.update({'response': response})
      childRFDict.update({'domain':makeDomain(dfpartitionBiome[regressors], domainIndex, domainScaling,domainOffset)})
      childRFDict.update({'RF': RandomForestRegressor(n_estimators=nTrees, \
                                                      min_samples_leaf=minSamplesLeafChild, \
                                                      bootstrap=True, \
                                                      random_state=0, \
                                                      verbose=0, \
                                                      max_depth=maxDepthChild, \
                                                      max_leaf_nodes=maxleafnodesChild, \
                                                      max_features=maxFeatures, \
                                                      n_jobs=40) \
                              .fit(dfpartitionBiome[regressors], np.array(dfpartitionBiome[response]).ravel())})
      
      childrenRFDict.update({partition: childRFDict})

      # assign the childrenRFDict to the parent
      parentRFDict.update({'childrenRFDict':childrenRFDict })      

      #assign the parentRF dict to the calibration data dictionary for trhis biome
      dataDictParent[biome].update({method+response[0]+'parentRFDict':parentRFDict})   

    return dataDictParent




# apply algorithm to data 
def predictClassifier(dataDict, methodDict, method, regressorsNames, response):
  '''
  dataDict(Dictionary): A Dictionary for storing all training data with biome numbers as keys;
  methodDict(Dictionary): A dictionary for storing all methods
  method:
  regressorsNames(String): a string containing the names of all input variables () 
  response(list): a list containing the names of all predicted parameters, e.g., ['LAI'].'''  

  #==========================================================================================================
  # make generic names for regressors for use in GEE
  # e.g., convert whatever regressor names to ['x1', 'x2', ..., 'xn']
  #==========================================================================================================
  regressors = []
  for item in np.arange(1,len(regressorsNames)+1,1):
    regressors.append('x' + str(item))

  #==========================================================================================================
  # Calibrate hierarchal randforest preeidctors for each biome
  #==========================================================================================================
  for biome in dataDict.keys():  # since biome number as keys
    print('biome:', biome)

    if (biome in [1,2,4,6,7]):
      # subset only the regressors 
      dfBiome = dataDict[biome]['DF'][sum([regressorsNames],[])].astype('int')
      dfBiome.columns = regressors   # Using ['x1', 'x2', ... , 'xn']

      #Apply the parent classifier
      parentRF = methodDict[biome][method+response[0]+'parentRFDict']['RF']
      dfBiome['childNames'] = np.around(parentRF.predict(dfBiome), decimals=3)
      dataDict[biome]['DF'][method + response[0]+'childNames'] = dfBiome['childNames']

      for partition in np.unique(dfBiome['childNames'] ):
        dfBiome.loc[dfBiome['childNames']==partition,method + response[0]] = methodDict[biome][method+response[0]+'parentRFDict']['childrenRFDict'][partition]['RF'].predict(dfBiome.loc[dfBiome['childNames']==partition][regressors])  
        dataDict[biome]['DF'][method + response[0]] = dfBiome[method + response[0]]
           
  return dataDict




