import ee 




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
        Percent(float): A threshold on the number of pixels corresponding to a child code.'''
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
# Description: This function takes a feature collection resulting from `export_trees_to_fc` and
#              creates a ee.Classifier that can be used with ee objects
#
# Note:        This function will be called by "constructMethod" function 
#   
###################################################################################################
def fc_to_classifier(FC):
  """Takes a feature collection resulting from `export_trees_to_fc` and 
     creates a ee.Classifier that can be used with ee objects

  args:
     fc (ee.FeatureCollection): feature collection that has trees property for each feature that represents the decision tree

  returns:
     classifier (ee.Classifier): ee classifier object representing an ensemble decision tree"""
  # expects that '#' is ecoded to be a 'return/enter'
  tree_strings = FC.aggregate_array("tree").map(lambda str: ee.String(str).replace("#", "\n", "g"))

  # pass list of ee.Strings to an ensemble decision tree classifier (i.e. RandomForest)
  return ee.Classifier.decisionTreeEnsemble(tree_strings)




###################################################################################################
# Description: This function creates an image where each band is the numerical value from a list
#              of strings
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
# Description: This function applies ONE ee.FeatureCollection object to subregions of a given
#              image (Image) and returns response
###################################################################################################
def predictRF(Image, MethodFC):
  '''Applies a RF and returns response.
     Args:
       image(ee.Image): A given ee.Image object. Subregions have been defined by caller;
       methodFC(ee.FeatureCollection): A single feature collection containing RF models.'''

  image    = ee.Image(Image)         # Note that subregions have been defined
  methodFC = ee.FeatureCollection(MethodFC) 

  #================================================================================================
  # select inputs scale the image and rename to RF regressors
  #================================================================================================
  params = methodFC.first()  # Get the first feature in the given feature collection

  out_img = image.select(ee.String(params.get('regressorsGENames')).split(',')) \
                        .multiply(stringListtoImage(ee.String(params.get('regressorsGEScaling')).split(','))) \
                        .add(stringListtoImage(ee.String(params.get('regressorsGEOffset')).split(','))) \
                        .multiply(stringListtoImage(ee.String('10000,10000,10000,10000,10000').split(','))) \
                        .rename(ee.String(params.get('regressors')).split(',')) \
                        .round() \
                        .classify(methodFC.get('RF'))  # Conduct RF-based classification 

  return out_img




###################################################################################################
# Description: This function applies an identified child feature collection to regions of a given
#              image.
###################################################################################################
def applyChildRF(Image, MethodFC, ChildName):
  '''Applies an identified child feature collection to subregions of a given image.

  Args:
    Image(ee.Image): A targeted image/mosaic;
    MethodFC(ee.List): A list of method feature collection;
    ChildName(Integer): An integer number representing a child FC.'''
  image     = ee.Image(Image)
  methodFC  = ee.List(MethodFC)
  childName = ee.Number(ChildName)
  
  #Apply a mask to the given image/mosaic
  maskedImg = image.updateMask(image.select('childNames').eq(childName))  

  #Select a feature collection model 
  uesd_RF   = methodFC.filter(ee.Filter.stringContains('system:id', childName.format("%d"))).get(0)
  
  return predictRF(maskedImg, uesd_RF).multiply(2).toUint8().rename('estimate') #scaling factor = 20




###################################################################################################
# Description: This function constructs method/algorithm based on the data stored on GEE assets 
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
  #print('<constructMethod> one asset :', ee.FeatureCollection(assetList.get(100)).get('system:id'))
  
  #================================================================================================
  # Create a LIST of all PARENT FeatureCollection objects 
  #================================================================================================
  def set_RF(parentFC):
    return ee.FeatureCollection(parentFC).set('RF', fc_to_classifier(ee.FeatureCollection(parentFC)))  

  parentList = assetList.filter(ee.Filter.stringContains('system:id', methodName)) \
                        .filter(ee.Filter.stringContains('system:id','parent')) \
                        .map(lambda parentFC: set_RF(parentFC))
  #print('\n\n\n<constructMethod> All parent trees:', ee.List(parentList).get(0).getInfo())
  
  #================================================================================================
  # Attache sub-trees to each PARENT FeatureCollection object
  #================================================================================================
  def AddChildRF(parentFC):   
    '''Attach all child trees to a parent FC''' 
    parent_id    = ee.String(ee.FeatureCollection(parentFC).get('system:id')).slice(0,-8)

    all_children = assetList.filter(ee.Filter.stringContains('system:id', parent_id)) \
                            .filter(ee.Filter.stringContains('system:id','child')) \
                            .map(lambda childFC: set_RF(childFC))

    return ee.FeatureCollection(parentFC).set('childFCList', all_children)

  AllMethodList = parentList.map(lambda parentFC: AddChildRF(parentFC))
  #print('\n\n<constructMethod> All parents and children trees:', AllMethodList.get(0).getInfo())
  
  # CL - add property "biomeNumber" to each element in "AllMethodList" by parsing the ID
  AllMethodList = AllMethodList.map(lambda method: ee.FeatureCollection(method).set('biomeNumber', \
                          ee.Number.parse(ee.String(ee.FeatureCollection(method).get('system:id')).slice(-9,-8))))

  return AllMethodList





###################################################################################################
# Description: This function divides a given List into a number of sublists and return them as the
#              elements of an exterior list. This function was dveloped to deal with the issue
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
  #print('\n\n\n<estimateResponse> number of used_methods = ', used_method.size().getInfo())

  #================================================================================================
  # Extract all child RF models associated with a specified biome
  #================================================================================================
  child_FC_list = biome_method.get('childFCList')

  #================================================================================================
  # Attach a child name band to the given image/mosaic based on the predictions of a parent RF 
  #================================================================================================
  image = image.addBands(predictRF(image, biome_method).multiply(1000).round().rename('childNames')) 

  #return image.select('childNames').updateMask(image.select('biome').eq(biomeID))
  #================================================================================================
  # Determine a set of unique values representing different child RF models
  #================================================================================================
  unique_subtree_values = uniqueValues(image.select('childNames'), region, 0)  
  #print('unique_subtree values = ', unique_subtree_values.getInfo())

  # Filter out the child numbers that do not have corresponding child RF
  valid_child_values = filter_childNames(child_FC_list, unique_subtree_values)  

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

