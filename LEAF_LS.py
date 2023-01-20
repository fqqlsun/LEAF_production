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
def uniqueValues(Image, Region):
  '''
     Args:
        Image(ee.Image): A given image containing only one band named as 'childNames' 
        Region(ee.Geometry): a goemetry region corresponding to the given image.'''
  image  = ee.Image(Image)
  region = ee.Geometry(Region)
  percentage = 0.0001

  #================================================================================================
  # Create a histogram that counts the frequency for each child number 
  #================================================================================================
  reduction = image.reduceRegion(reducer = ee.Reducer.frequencyHistogram(), 
                                 geometry = region,
                                 bestEffort = True,
                                 scale = 30,    
                                 tileScale = 4) 

  histogram   = ee.Dictionary(reduction.get(reduction.keys().get(0)))

  #================================================================================================
  # Determine a threshold that will be used to filter out the child numbers corresponding to a 
  # small number of pixels 
  #================================================================================================
  dict_values = ee.List(histogram.values()).map(lambda val: ee.Number(val).round())
  thresh = ee.Number(dict_values.reduce(ee.Reducer.sum())).multiply(percentage)  

  #================================================================================================
  # Convert the histogram dictionary to a feature collection
  #================================================================================================
  dict_keys    = ee.List(histogram.keys())  
  histogram_FC = ee.FeatureCollection(dict_keys.map(lambda key: DictItem2Feature(key, histogram)))
  
  #================================================================================================
  # Filter the feature collection
  #================================================================================================
  short_FC = histogram_FC.filter(ee.Filter.gt('value', thresh))

  #================================================================================================
  # Return the key values in the filtered feature collection
  #================================================================================================
  values = ee.FeatureCollection(short_FC).aggregate_array('keys').map(lambda key: ee.Number.parse(key)) 
  print('\n\n<uniqueValues> final values = ', values.getInfo())

  return values




###################################################################################################
# Description: This function takes a feature collection resulting from `export_trees_to_fc` and
#              creates a ee.Classifier that can be used with ee objects
#
# Note:        This function will be called by "constructMethod" function 
#   
###################################################################################################
def fc_to_classifier(fc):
  """Takes a feature collection resulting from `export_trees_to_fc` and 
     creates a ee.Classifier that can be used with ee objects

  args:
     fc (ee.FeatureCollection): feature collection that has trees property for each feature that represents the decision tree

  returns:
     classifier (ee.Classifier): ee classifier object representing an ensemble decision tree"""
  # expects that '#' is ecoded to be a 'return/enter'
  tree_strings = fc.aggregate_array("tree").map(lambda str: ee.String(str).replace("#", "\n", "g"))

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

  image    = ee.Image(Image)                # Note that subregions have been defined
  methodFC = ee.FeatureCollection(MethodFC) 

  #================================================================================================
  # select inputs scale the image and rename to RF regressors
  #================================================================================================
  params = methodFC.first()  # Get the first feature in the given feature collection
  #print('\n\n<predictRF> regressorsGENames:', ee.String(params.get('regressorsGENames')).split(',').getInfo())
  #print('<predictRF> regressorsGEScaling:', ee.String(params.get('regressorsGEScaling')).split(',').getInfo())
  #print('<predictRF> regressorsGEOffset:', ee.String(params.get('regressorsGEOffset')).split(',').getInfo())
  #print('<predictRF> regressors:', ee.String(params.get('regressors')).split(',').getInfo())

  out_img = image.select(ee.String(params.get('regressorsGENames')).split(',')) \
                        .multiply(stringListtoImage(ee.String(params.get('regressorsGEScaling')).split(','))) \
                        .add(stringListtoImage(ee.String(params.get('regressorsGEOffset')).split(','))) \
                        .multiply(stringListtoImage(ee.String('10000,10000,1,1,1').split(','))) \
                        .rename(ee.String(params.get('regressors')).split(',')) \
                        .round() \
                        .classify(methodFC.get('RF'))  # Conduct RF-based classification 

  #print('<predictRF> bands in out image = ', out_img.bandNames().getInfo())
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
  
  #Apply a mask t othe given image/mosaic
  maskedImg = image.updateMask(image.select('childNames').eq(childName))  

  #Select a feature collection model 
  uesd_RF   = methodFC.filter(ee.Filter.stringContains('system:id', childName.format("%d"))).get(0)

  return predictRF(maskedImg, uesd_RF).multiply(1000).toInt16().rename('estimate')




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

  #================================================================================================
  # Create a list of ee.FeatureCollection objects from a GEE assets list of directories
  #================================================================================================
  client_asset_list = []
  for asset in raw_asset_list:
    client_asset_list.append(ee.FeatureCollection(asset['name']))

  assetList = ee.List(client_asset_list)
  #print('All assets:', assetList)
  
  #================================================================================================
  # Define two subroutines 
  #================================================================================================
  def set_RF(parentFC):
    return ee.FeatureCollection(parentFC).set('RF', fc_to_classifier(ee.FeatureCollection(parentFC)))

  def childRF(parentFC):    
    return ee.FeatureCollection(parentFC).set('childFCList', assetList.filter(ee.Filter.stringContains('system:id',ee.String(ee.FeatureCollection(parentFC).get('system:id')).slice(0,-8))) \
                                                                      .filter(ee.Filter.stringContains('system:id','child')) \
                                                                      .map(lambda childFC: set_RF(childFC)))

  #================================================================================================
  # Create a LIST of PARENT FeatureCollection objects 
  #================================================================================================
  parentList = assetList.filter(ee.Filter.stringContains('system:id', methodName)) \
                        .filter(ee.Filter.stringContains('system:id','parent')) \
                        .map(lambda parentFC: set_RF(parentFC))
  #print('\n\n<constructMethod> All parents:', parentList.getInfo())

  #================================================================================================
  # Attache sub-trees to each PARENT FeatureCollection object
  #================================================================================================
  methodList = parentList.map(lambda parentFC: childRF(parentFC))
  #print('All parents and children:', methodList.get(5).getInfo())

  return methodList




###################################################################################################
# Description: This function applies RF models to an image 
###################################################################################################
def estimateResponse(Method, Image, Region):
  '''
  '''
  method = ee.FeatureCollection(Method)
  image  = ee.Image(Image)
  
  #================================================================================================
  # Attach a band indicating children Numbers based on the parent RF Tree to the given image/mosaic
  #================================================================================================
  image = image.addBands(predictRF(image, method).multiply(1000).round().rename('childNames')) 

  #================================================================================================
  # Collect a list of unique values that represent different child decision trees
  #================================================================================================
  unique_subtree_values = uniqueValues(image.select('childNames'), Region)  
  #unique_subtree_values = ee.List([1149, 1282, 2056, 2818, 10298])

  #================================================================================================
  # Make images of response for each unique childnumbers
  #================================================================================================
  child_FC_list = method.get('childFCList')  # Get a list of feature collections under a given "method"
  #print('\n\n<estimateResponse> method child list: ', child_FC_list.getInfo())

  estimated_imgs = unique_subtree_values.map(lambda chld_name: applyChildRF(image, child_FC_list, chld_name))

  # Remove mask from every image
  estimated_imgs = estimated_imgs.map(lambda image: ee.Image(image).unmask().clip(Region))
  print('\n\n<estimateResponse> numb of images:', estimated_imgs.size().getInfo())

  return ee.ImageCollection(estimated_imgs).max()
