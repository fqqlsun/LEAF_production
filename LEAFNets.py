import ee
#ee.Initialize()

import Image as Img
import ImgMask as IM
import ImgSet as IS
import eoTileGrids as eoTG
import eoParams as eoPM
import Mosaic
import eoAuxData as eoAD
import LEAF_LSv1 as LFLS



#############################################################################################################
# Description: Functions is for reading parameters for creating the ANNs applicable to Sentinel-2 data 
# 
# Revision history:  2021-May-17  Lixin Sun  Copied from the Richard's Python code
#                    2022-Jan-17  Lixin Sun  Added more feature collections for diverse land covers. 
#                    2022_Sep-08  Lixin Sun  Further reduce the number of land cover types for SL2P
#  
#############################################################################################################
'''
def s2_createFeatureCollection_estimates(version):
    #print("\n<s2_createFeatureCollection_estimates> function is called......")
    if version == 0:
      return ee.FeatureCollection ('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1')  
      #return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_dbf_big_NNT1_Single_0_1') 
    else:
      #print("\n<s2_createFeatureCollection_estimates> SL2P version1 is being used......")
      return  ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1') \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_dbf_big_clumped_NNT1_Single_0_1_v2')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_enf_big_clumped_NNT1_Single_0_1_v2')) \
       .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_mix_big_clumped_NNT1_Single_0_1_v2'))   


def s2_createFeatureCollection_errors(version):
    if version == 0:
      return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error')
    else:
      return   ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1_error') \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_dbf_big_clumped_NNT1_Single_0_1_v2_errors')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_enf_big_clumped_NNT1_Single_0_1_v2_errors')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_mix_big_clumped_NNT1_Single_0_1_v2_errors'))


def s2_createFeatureCollection_domains(version):
    if version == 0:
      return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')
     #return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_DOMAIN')
    else:
      return   ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN') \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN')) \
        .merge(ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/S2_SL2P_WEISS_ORIGINAL_DOMAIN'))
'''

def s2_createFeatureCollection_estimates(version):
    #print("\n<s2_createFeatureCollection_estimates> function is called......")
    if version == 0:
      return ee.FeatureCollection ('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_weiss_or_prosail_NNT3_Single_0_1')  
      #return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/s2_sl2p_ROF_sobol_prosail_dbf_big_NNT1_Single_0_1') 
    else:
      #print("\n<s2_createFeatureCollection_estimates> SL2P version1 is being used......")
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


def s2_createFeatureCollection_errors(version):
    if version == 0:
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


def s2_createFeatureCollection_domains(version):
    if version == 0:
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


def s2_createFeatureCollection_range():
    return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')
    
def s2_createFeatureCollection_Network_Ind():
  return ee.FeatureCollection('users/rfernand387/Parameter_file_prosail_ccrs_big_clumped2')

def s2_createFeatureCollection_legend():
    #return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/Legend_sl2p')
    return ee.FeatureCollection('users/rfernand387/Legend_prosail_ccrs_big_clumped')

'''
def createImageCollection_partition():  
  return ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V/Global") \
           .map(lambda image: image.select("discrete_classification") \
           .remap([0,20,30,40,50,60,70,80,90,100,111,112,113,114,115,116,121,122,123,124,125,126,200],[0,8,10,15,17,16,19,18,14,13,1,3,1,5,6,6,2,4,2,5,6,6,18],0).uint8().rename("partition")) \
           .merge(ee.ImageCollection('users/rfernand387/NA_NALCMS_2015_tiles') \
           .map(lambda image: image.select("b1").rename("partition")))
'''



#############################################################################################################
# Description: Functions for reading ANN coefficients that are applicable to Sentinel-2 data without using
#              three red-edge bands. The vegetation parameters extracted from this kind of ANN are more
#              comparable to that extracted from Landsat data.  
# 
# Revision history:  2023-Aug-30  Lixin Sun  Initial creation
#
#############################################################################################################
def s2_no_edge_createFeatureCollection_estimates():
    return   ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1') \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_enf_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_NNT1_Single_0_1')) 

def s2_no_edge_createFeatureCollection_errors():
    return   ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes') \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_enf_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_NNT1_Single_0_1_incertitudes')) 


def s2_no_edge_createFeatureCollection_domains():
    return   ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_domain') \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_enf_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_domain')) 


'''
def s2_no_edge_createFeatureCollection_estimates():
    return   ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1') \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_enf_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_NNT1_Single_0_1')) 

def s2_no_edge_createFeatureCollection_errors():
    return   ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes') \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_enf_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_NNT1_Single_0_1_incertitudes')) 


def s2_no_edge_createFeatureCollection_domains():
    return   ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_domain') \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_enf_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_weiss_or_prosail_domain')) \
      .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/s2likel8_sl2p_ccrs_sobol_4sail2_dbf_domain')) 
'''

def s2_no_edge_createFeatureCollection_range():
    return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/weiss_or_prosail3_NNT3_Single_0_1_RANGE')
    
def s2_no_edge_createFeatureCollection_Network_Ind():
    #return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/Parameter_file_sl2p')
    return ee.FeatureCollection('users/rfernand387/Parameter_file_prosail_ccrs_big_clumped2')

def s2_no_edge_createFeatureCollection_legend():
    #return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/Legend_sl2p')
    return ee.FeatureCollection('users/rfernand387/Legend_prosail_ccrs_big_clumped')



#############################################################################################################
# Description: Functions for reading ANN coefficients that are applicable to Landsat-8 data 
# 
# Revision history:  2021-May-17  Lixin Sun  Copied from the Richard's Python code in Jupyter Notebook
#                    2023-Sep-25  Lixin Sun  Further reduce the land cover IDs from [0,1,2,3,4,5,6,7,8,9,10,11]
#                                            to [0,0,1,2,0,0,0,1,0,0,0,3];
#
#############################################################################################################
'projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_mix_big_clumpedv3_NNT1_Single_0_1'
def l8_createFeatureCollection_estimates(version):
    if version == 0:
      return  ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1')
    else: 
      return  ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1') \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_dbf_big_clumpedv3_NNT1_Single_0_1')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_enf_big_clumpedv2_NNT1_Single_0_1')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_dbf_big_clumpedv3_NNT1_Single_0_1')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_mix_big_clumpedv3_NNT1_Single_0_1')) 
                                   
def l8_createFeatureCollection_errors(version):
    if version == 0:
      return  ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')
    else:
      return  ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes') \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_dbf_big_clumpedv3_NNT1_Single_0_1_incertitudes')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_enf_big_clumpedv2_NNT1_Single_0_1_incertitudes')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_dbf_big_clumpedv3_NNT1_Single_0_1_incertitudes')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_NNT1_Single_0_1_incertitudes')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_mix_big_clumpedv3_NNT1_Single_0_1_incertitudes')) 

def l8_createFeatureCollection_domains(version):
    if version == 0:
      return  ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_domain')
    else:
      return  ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_domain') \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_domain')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_dbf_big_clumpedv3_domain')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_enf_big_clumpedv2_domain')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_domain')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_domain')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_domain')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_dbf_big_clumpedv3_domain')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_domain')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_domain')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_weiss_or_prosail_domain')) \
       .merge(ee.FeatureCollection('projects/ee-modis250/assets/SL2P/l8_sl2p_ROF_sobol_prosail_mix_big_clumpedv3_domain')) 

def l8_createFeatureCollection_range(version):
    return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/LANDSAT_LC08_C01_T1_SR_RANGE')
    
def l8_createFeatureCollection_Network_Ind():
    #return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/Parameter_file_sl2p')
    return ee.FeatureCollection('users/rfernand387/Parameter_file_prosail_ccrs_big_clumped2')

def l8_createFeatureCollection_legend():
    #return ee.FeatureCollection('users/rfernand387/LANDSAT_LC08_C01_T1_SR/Legend_sl2p')
    return ee.FeatureCollection('users/rfernand387/Legend_prosail_ccrs_big_clumped')


'''    
def s2_createFeatureCollection_Network_Ind():
  return ee.FeatureCollection('users/rfernand387/Parameter_file_prosail_ccrs_big_clumped2')

def s2_createFeatureCollection_legend():
    #return ee.FeatureCollection('users/rfernand387/COPERNICUS_S2_SR/Legend_sl2p')
    return ee.FeatureCollection('users/rfernand387/Legend_prosail_ccrs_big_clumped')
'''


#def l8_createImageCollection_partition():
#    return ee.ImageCollection('users/rfernand387/NA_NALCMS_2015_tiles') \
#             .map(lambda image: image.select("b1").rename("partition")) \
#             .merge(ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V/Global") \
#             .map(lambda image: image.select("discrete_classification") \
#             .remap([0,20,30,40,50,60,70,80,90,100,111,112,113,114,115,116,121,122,123,124,125,126,200],
#                    [0,8, 10,15,17,16,19,18,14,13, 1,  3,  1,  5,  6,  6,  2,  4,  2,  5,  6,  6,  18],0).uint8().rename("partition")))




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
      "inputBands":   ['cosVZA','cosSZA','cosRAA','B3',   'B4', 'B5',      'B6',      'B7',     'B8A','B11',    'B12'], 
                                                  #green, red, red_edge1, red_edge2, red_edge3, NIR,  SWIR1 and SWIR2
    },

    'L8_SR': {
      "name": 'L8',
      "description": 'LANDSAT 8',      
      "Watercover": 'CLOUD_COVER',      
      "VIS_OPTIONS": 'VIS_OPTIONS',
      "Collection_SL2P":       ee.FeatureCollection(l8_createFeatureCollection_estimates(VERSION_NB)),
      "Collection_SL2Perrors": ee.FeatureCollection(l8_createFeatureCollection_errors(VERSION_NB)),
      "sl2pDomain":            ee.FeatureCollection(l8_createFeatureCollection_domains(VERSION_NB)),
      "Network_Ind":           ee.FeatureCollection(l8_createFeatureCollection_Network_Ind()),
      "legend":                ee.FeatureCollection(l8_createFeatureCollection_legend()),
      "numVariables": 7,
      "inputBands":   ['cosVZA','cosSZA','cosRAA', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'],
                                                   #green,  red,     NIR,     SWIR1 and SWIR2
    },
    
    'HLS_SR': {
      "name": 'HLS',
      "description": 'HLS',      
      "Watercover": 'CLOUD_COVERAGE',      
      "VIS_OPTIONS": 'VIS_OPTIONS',
      "Collection_SL2P":       ee.FeatureCollection(l8_createFeatureCollection_estimates(VERSION_NB)),
      "Collection_SL2Perrors": ee.FeatureCollection(l8_createFeatureCollection_errors(VERSION_NB)),
      "sl2pDomain":            ee.FeatureCollection(l8_createFeatureCollection_domains(VERSION_NB)),
      "Network_Ind":           ee.FeatureCollection(l8_createFeatureCollection_Network_Ind()),
      "legend":                ee.FeatureCollection(l8_createFeatureCollection_legend()),
      "numVariables": 7,
      "inputBands":   ['cosVZA','cosSZA','cosRAA', 'B3', 'B4', 'B5', 'B6', 'B7'],
                                                 #green, red,  NIR,  SWIR1 and SWIR2
    },

    'S2_SR6': {  #For using Sentinel-2 data with only 6 Landsat equivalent bands
      "name": 'S2',
      "description": 'Sentinel 2A',      
      "Watercover": 'WATER_PERCENTAGE',
      "VIS_OPTIONS": 'VIS_OPTIONS',
      "Collection_SL2P":       ee.FeatureCollection(s2_no_edge_createFeatureCollection_estimates()),      
      "Collection_SL2Perrors": ee.FeatureCollection(s2_no_edge_createFeatureCollection_errors()),  
      "sl2pDomain":            ee.FeatureCollection(s2_no_edge_createFeatureCollection_domains()),
      "Network_Ind":           ee.FeatureCollection(s2_no_edge_createFeatureCollection_Network_Ind()),
      "legend":                ee.FeatureCollection(s2_no_edge_createFeatureCollection_legend()),
      "numVariables": 7,
      "inputBands":   ['cosVZA','cosSZA','cosRAA', 'B3', 'B4', 'B8A','B11', 'B12'], 
                                                  #green, red, NIR, SWIR1 and SWIR2
    }
}



PROD_OPTIONS = {
    "Surface_Reflectance": {
        "Name": 'Surface_Reflectance',
        "description": 'Surface_Reflectance',
        "inp":      [ 'B4', 'B5', 'B6', 'B7', 'B8A','B9','B11','B12']        
    },
    "ALBEDO": {
        "Name": 'Albedo',
        "errorName": 'errorAlbedo',
        "maskName": 'maskAlbedo',
        "description": 'Black sky albedo',
        "variable": 6,           
        "outmin": 0,  #(ee.Image(ee.Array([[0]]))),
        "outmax": 1,  #(ee.Image(ee.Array([[1]])))
        "scale_factor": 200,
        "compact_factor": 1},
    'FAPAR': {
        "Name":      'fAPAR',
        "errorName": 'errorfAPAR',
        "maskName":   'maskfAPAR',
        "description": 'Fraction of absorbed photosynthetically active radiation',
        "variable": 2,
        "outmin": 0 ,  #(ee.Image(ee.Array([[0]]))),
        "outmax": 1,  #(ee.Image(ee.Array([[1]])))
        "scale_factor": 200,
        "compact_factor": 256},
    'FCOVER': {
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
# Description: Returns a single band image named "networkID" to map the networks to be applied according to
#              a land cover map. 
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [162])
#                    2022-Jan-27  Updated to ensure this function works for both LEAF V0 (one network for
#                                 all land cover classes) and V1 (diverse networks for diffrent land covers).
#############################################################################################################
def makeIndexLayer(inPartition, numb_classes, legend, network_IDs):
    '''Returns a single band image named "networkID" to map teh networks to be applied according to
       a land cover map. 

       Args: 
         inPartition(ee.image): a land cover classification map;
         nbClsNets(ee.Number): the number of networks corresponding to one biophysical parameter;
         inLegend(ee.FeatureCollection): a feature collection containing class legends;
         inNetwork_Id(ee.FeatureCollection): a feature collection containing networkIDs. '''
    partition  = ee.Image(inPartition)             # land cover classification map with CCRS' legend
    classes    = ee.Number(numb_classes)           # the number of networks for one biophysical parameter (one or multiple)
    legend     = ee.FeatureCollection(legend)      # legend to convert class ID numbers to networks
    Network_Id = ee.FeatureCollection(network_IDs) # legend to convert networks to networkIDs
    
    #print('\n\n<makeIndexLayer> legend collection = ', legend.getInfo())
    #print('<makeIndexLayer> network ID collection = ', Network_Id.getInfo())
    #========================================================================================================
    # get a list of all valid class IDs
    #========================================================================================================
    legend_list = legend.toList(legend.size())
    CCRS_LC_IDs = legend_list.map(lambda feature: ee.Feature(feature).getNumber('Value'))
    
    print('\n\n<makeIndexLayer> CCRS land cover IDs = ', CCRS_LC_IDs.getInfo())

    #========================================================================================================
    # get network indices corresponding to the class IDs
    #========================================================================================================
    print('<makeIndexLayer> numb of valid classes = ', classes.getInfo())
    if classes.getInfo() == 1:  # the case of LEAF V0
      nbClsIDs   = CCRS_LC_IDs.size().getInfo()
      networkIDs = ee.List([0]*nbClsIDs)
      print('<makeIndexLayer> LEAF V0 network IDs = ', networkIDs.getInfo())
    else:  # the case of LEAF V1
      networkIDs = legend_list.map(lambda feature: ee.Feature(feature).get('SL2P Network')) \
                              .map(lambda propertyValue: ee.Feature(Network_Id.first()).toDictionary().getNumber(propertyValue))
      print('<makeIndexLayer> LEAF V1 network IDs = ', networkIDs.getInfo())     

    #========================================================================================================
    # return a mapped network index map and name it as 'networkID'
    # [1, 3, 4, 17, 7, 8, 5, 11, 9, 15, 13, 2, 14, 10, 12, 18, 16, 19, 6]  ==>  19 CCRS class IDs
    # [3, 2, 2, 0,  8, 7, 2, 7,  4, 1,  5,  3, 4,  6,  10, 0,  9,  0,  11] ==>  12 network IDs
    #  2 and 7 network IDs corresponding broadleaf and shrubland 
    #========================================================================================================
    init_net_ID_map = partition.remap(CCRS_LC_IDs, networkIDs, 0)
    return init_net_ID_map.rename('networkID')

    #init_net_IDs = [0,1,2,3,4,5,6,7,8,9,10,11]
    #real_net_IDs = [0,0,1,2,0,0,0,1,0,0,0,3]

    #return init_net_ID_map.remap(init_net_IDs, real_net_IDs, 0).rename('networkID')
    
    


    
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
         feature_list(ee.List): A list of network ee.Features for one parameter of all classes;
         class_ID(ee.Number): A land cover class number/ID. '''
    
    #========================================================================================================
    # typecast function parameters 
    #========================================================================================================
    features = ee.List(feature_list)  # a list of network ee.Features for one parameterof all classes
    cls_ID   = ee.Number(class_ID)     
    
    #========================================================================================================
    # Extract one LEAF network ee.Feature from the "feature_list" based on a given class_ID
    #========================================================================================================
    class_net = ee.Feature(features.get(cls_ID.subtract(1)))

    #========================================================================================================
    #========================================================================================================
    # Break down a feature (class_net, a 1D vector) into eight vectors and associate them with eight keys.  
    #========================================================================================================
    out_net = {}
    
    # input slope (11 values for S2 and 8 for LS)
    num    = ee.Number(6)    # 6
    offset = class_net.getNumber(ee.String('tabledata').cat(num.format()))  #The value corresponding to 'tabledata6'
    start  = num.add(1)      # 7
    end    = num.add(offset) # 6 + offset'
    out_net["inpSlope"] = ee.List.sequence(start, end).map(lambda indx: getCoefs(class_net, indx))
    
    # input offset (11 values for S2 and 8 for LS)
    num    = end.add(1)
    offset = class_net.getNumber(ee.String('tabledata').cat(num.format()))
    start  = num.add(1)
    end    = num.add(offset)
    out_net["inpOffset"] = ee.List.sequence(start, end).map(lambda indx: getCoefs(class_net, indx))

    # hidden layer 1 weight (55 values = 11 x 5) 
    num    = end.add(1)
    offset = class_net.getNumber(ee.String('tabledata').cat(num.format()))
    start  = num.add(1)
    end    = num.add(offset)
    out_net["h1wt"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(class_net,indx))

    # hidden layer 1 bias (5 values)
    num    = end.add(1)
    offset = class_net.getNumber(ee.String('tabledata').cat(num.format()))
    start  = num.add(1)
    end    = num.add(offset)
    out_net["h1bi"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(class_net,indx))

    # hidden layer 2 weight (5 values)
    num    = end.add(1)
    offset = class_net.getNumber(ee.String('tabledata').cat(num.format()))
    start  = num.add(1)
    end    = num.add(offset)
    out_net["h2wt"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(class_net,indx))
  
    # hidden layer 2 bias (1 value)
    num    = end.add(1)
    offset = class_net.getNumber(ee.String('tabledata').cat(num.format()))
    start  = num.add(1)
    end    = num.add(offset)
    out_net["h2bi"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(class_net,indx))

    # output slope (1 value)
    num    = end.add(1)
    offset = class_net.getNumber(ee.String('tabledata').cat(num.format()))
    start  = num.add(1)
    end    = num.add(offset)
    out_net["outSlope"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(class_net,indx))
  
    # output offset (1 value)
    num    = end.add(1)
    offset = class_net.getNumber(ee.String('tabledata').cat(num.format()))
    start  = num.add(1)
    end    = num.add(offset)
    out_net["outBias"] = ee.List.sequence(start,end).map(lambda indx: getCoefs(class_net, indx))
    
    #print('<FNet_to_DNet> The output network in dictionary format:', out_net)
    return ee.Dictionary(out_net)




#############################################################################################################
# Description: Returns a list of LEAF networks (with ee.Dictionary objects as elements) for calculating 
#              one biophysical parameter map across different land cover types. 
#              
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [165])
#
#############################################################################################################
def make_DNet_arr(all_nets, numClasses, ParamID):
    '''Returns a list of LEAF networks (with ee.Dictionary objects as elements) for calculating one
       biophysical parameter map across different land cover types. 

       Args:
         all_nets(ee.FeatureCollection): a collection of LEAF networks (with ee.Feature as elements) for
                                         all biophysical parameters and land cover types; 
         numClasses(ee.Number): the total number of land cover types (1 or 11);
         ParamID(ee.Number): the ID number of a vegetation parameter (e.g., 1 for 'LAI'). '''
    #========================================================================================================
    # typecast function parameters 
    #========================================================================================================
    all_nets   = ee.FeatureCollection(all_nets)  #A network matrix for different bio-parameters and land covers; 
    numClasses = ee.Number(numClasses)           #The total number of land cover types
    ParamID    = ee.Number(ParamID)              #The ID number of a vegetation parameter
    
    #========================================================================================================
    # Extract a list of network features for one biophysical parameter and different land cover types
    # The value associated with 'tabledata3' key is the biophysical parameter ID (e.g., 1 means LAI). 
    # All the features with 'tabledata3' equal to the same values are the networks for calculating the same
    # biophysical parameter across different land cover types.   
    #========================================================================================================
    filtered_features = ee.FeatureCollection(all_nets.filter(ee.Filter.eq('tabledata3', ParamID))).toList(numClasses)
    #print('<make_DNet_arr> Filtered network feature list:', filtered_features.getInfo())

    # Return a list of network (in ee.Dictionary format) for different land cover types
    # "FNet_to_DNet" function converts a given LEAF network from ee.Feature format to ee.Dictionary format.
    #return FNet_to_DNet(filtered_features, 1)
    return ee.List.sequence(1, numClasses).map(lambda ClsID: FNet_to_DNet(filtered_features, ClsID))
    



#############################################################################################################
# Description: Applies a specified (defined by 'inNetIndex') two-layer neural network to a subset of land
#              covers and returns a single band image containing results.
#
# Note:        This function applys gain and offset to convert the image values to reflectance values 
#              ranging from between 0 and 1, instead of from 0 to 100
#
# Revision history:  2021-May-17              Copied from Richard's Python notebook (In [167])
#                    2021-May-27  Lixin Sun   Reviewed and added comments
#                    2022-Jan-27  Lixin Sun   Merged 'selectNet' function to 'applyNet'. The reason of 
#                                             doing this is to apply a spatial mask to resultant image
#                                             (see 'return' statment). 
#                    2022-Mar-28  Lixin Sun   Updated to use "apply_gain_offset" for image value conversion.
#                    2022-Jun-17  Lixin Sun   Moved pixel gain/offset application to outside of this function.
#                                             So the reflectance value range in the given mosaic image must
#                                             be from 0 to 1.  
#############################################################################################################
def applyNet(Image, NetList, BandNames, NetIndex, OutName):
    '''Applies a specified (defined by 'inNetIndex') two-layer neural network to a subset of land covers.

       Args: 
         Image(ee.Image): a ee.Image object with network index band (named 'networkID') attached;
         NetList(ee.List):  a list of networks for one parameter and various land cover types;
         BandNames(ee.List):  a list of band names to be used in parameter extraction;              
         NetIndex(ee.Number): an index number to a land cover;
         OutName(string): the name string of output band. '''
    
    in_image   = ee.Image(Image)           # a mosaic image with a "networkID" band image attached 
    netList    = ee.List(NetList)          # a list of all available LEAF networks
    bandNames  = ee.List(BandNames)        # [cosCZA,cosVZA,cosRAA,B3,B4,B5,B6,B7,B8,B11 and B12] for Sentinel2
    netIndex   = ee.Number(NetIndex).int() # the index number of a specified LEAF network   
    outputName = ee.String(OutName)        # the name of the band containing output results

    #========================================================================================================
    # Mask out areas with "networkID" not equal to a identified networkID
    #========================================================================================================
    mask     = in_image.select('networkID').eq(netIndex)    # a mask to mask out unselected land cover types  
    used_img = in_image.select(bandNames).updateMask(mask)  # Update the mask for a number of selected bands
    
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
# Description: Applies a set of ANNs to an image based on a given land cover map and returns an image
#              (ee.Image object) containing three bands, a biophysical parameter map, a land cover map and 
#              a network index map. 
#
# Note:        (1) The SR value range of the given mosaic image (inImage) must be within 0 and 1.
#              (2) Note the dictionaries used in this function are all ee.Dictionary objects, so the items 
#                  cannot be accessed through subscription (e.g., dictionary.['key']).
#
# Revision history:  2021-May-17  Copied from Richard's Python notebook (In [168])
#                    2023-Nov-27  Lixin Sun  Added return of network ID map
#
#############################################################################################################
def wrapperNNets(networks, partition, prod_options, coll_options, suffix_name, inImage) :
    '''Applies a set of shallow networks to an image based on a given land cover map.

       Args: 
         networks(ee.List): a 2D matrix of networks (ee.Dictionary objects);
         partition(ee.Image): a land cover partition/classification map;
         prod_options(ee.Dictionary): a dictionary containing the info related to a selected parameter type;
         coll_options(ee.Dictionary): a dictionary containing the info related to a selected satellite type;
         suffix_name(string): a suffix name of output;
         inImage(ee.Image): a mosaic image for vegetation parameter extraction. '''
    #========================================================================================================
    # typecast function parameters  
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
    # Attach a network ID band to the given image cube
    #========================================================================================================
    net_indx_map = makeIndexLayer(partition, nbClsNets, CollOptions.get('legend'), CollOptions.get('Network_Ind'))
    used_image   = image.addBands(net_indx_map)  #The name of the added band is "networkID"

    #========================================================================================================
    # Apply each network in 'netList' to its corresponding land cover separately and then merge the results
    # to one image by calling 'max()' function.
    #========================================================================================================
    outName    = ee.String(suffix_name).cat(ProdOptions.getString('Name'))
    band_names = CollOptions.get('inputBands')

    #estimate = applyNet(used_image, netList, band_names, 2, outName)
    
    estimate = ee.ImageCollection(ee.List.sequence(0, nbClsNets.subtract(1)) \
             .map(lambda netIndex: applyNet(used_image, netList, band_names, netIndex, outName))) \
             .max()    
             #.addBands(partition).addBands(net_indx_map)
    
    return estimate, net_indx_map






#############################################################################################################
# Description: This function creates a pixel mask that masks out cloud/shadow, snow/ice and water. This mask
#              will be used to set a flag at the 3rd bit in a QC image. 
#
# The value mapping from a classification map to biome map is as follows:
# [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19], [0,7,7,5,6,6,7,2,2,1,1,2,1,1,2,3,1,1,0,0]
#
# Revision history:  2022-Jun-22  Lixin Sun  Initial creation 
#                    2022-Nov-16  Lixin Sun  Added water mask from a given classification map.
#
#############################################################################################################
def LEAF_valid_mask(Image, Year, SsrData, MaxRef, ClassMap):
  '''Exports three ancillary maps associated with one set of LEAF products

  Args:
    Image(ee.Image): a given mosaic image;
    Year(int): A integer representing target year;
    SsrData(Dictionary): a Dictionary containing metadata associated with a sensor and data unit;
    MaxRef(int): the maximum reflectance value in the given Image;
    ClassMap(ee.Image): a given classification map.'''

  #==========================================================================================================
  # Invoke the functions to generate various masks. 
  # Note the value range in "Image" is [0, 1] since it is used for LEAF calculation 
  #==========================================================================================================
  snow_mask   = IM.Img_SnowMask (Image, Year, SsrData, MaxRef)
  #water_mask  = IM.Img_WaterMask(Image, SsrData, MaxRef)
  valid_mask  = IM.Img_ValidMask(Image, Year, SsrData, MaxRef)  
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
def SL2P_separate_params(inParams, inMosaic, Region, SsrData, ClassImg, task_list = None):
  '''Produces a full set of LEAF products for a specific region and time period and export them in separate files.

    Args:
       inParams(Dictionary): A dictionary containing all required parameters;
       inMosaic(ee.Image): A given mosaic image from which products will be generated;  
       Region(ee.Geometry): A ROI;     
       SsrData(Dictionary): A Dictionary containing metadata associated with a sensor and data unit;
       ClassImg(ee.Image): A given classification image;
       task_list([]): a list for storing the links to exporting tasks.'''
  
  mosaic = ee.Image(inMosaic)
  #==========================================================================================================
  # Obtain the names of a GEE Data Catalog ('COPERNICUS/S2_SR_HARMONIZED' or 'LANDSAT/LC08/C01/T1_SR') and
  # a biophysical parameter (one of 'LAI', 'fCOVER', 'fAPAR' and 'Albedo').
  #==========================================================================================================
  coll_dict   = COLL_OPTIONS[SsrData['NAME']] # ee.Dictionay object related to a selected collection type
 
  sl2p_Domain = coll_dict["sl2pDomain"].aggregate_array("DomainCode").sort()
  bandList    = ee.List(coll_dict["inputBands"])
  LEAF_image  = mosaic.select(bandList.slice(3))  #Select only required spectral bands
  nBands      = bandList.slice(3).length()
  
  #print("\n\n<SL2P_separate_params> Selected band names in given mosaic:", LEAF_image.bandNames().getInfo())
  #==========================================================================================================
  # Create a QC image to mark the pixels where spectral values are out of the input range for calculating
  # biophysical parameters
  #==========================================================================================================
  QC_img = LEAF_image.multiply(ee.Image.constant(ee.Number(10))).ceil().mod(ee.Number(10))\
                     .multiply(ee.Image.constant(ee.List.sequence(0, nBands.subtract(1)).map(lambda value: ee.Number(10).pow(ee.Number(value))))) \
                     .reduce("sum").remap(sl2p_Domain, ee.List.repeat(0, sl2p_Domain.length()), 1).uint8()

  #==========================================================================================================
  # Mask out water bodies from the mosaic image
  #==========================================================================================================  
  water_mask = ClassImg.neq(ee.Image(0)).And(ClassImg.neq(ee.Image(18)))
  mosaic     = mosaic.updateMask(water_mask)

  #print("<SL2P_separate_params> The bands in LEAF mosaic_image", mosaic.bandNames().getInfo())
  #==========================================================================================================
  # Determine the number of land cover classes based on the number of networks and parameter types.
  #==========================================================================================================
  coll_nets  = coll_dict["Collection_SL2P"]             # Get all the networks for parameter estimation
  #print("\n<SL2P_separate_params>", coll_nets.getInfo())

  total_nets = coll_nets.size()                         # the total number of networks (ee.Feature objects)  
  numbParams = int(coll_dict["numVariables"])           # the total number of biophysical parameters (normally 7)
  numClasses = total_nets.divide(ee.Number(numbParams)) # the number of land cover classes
  print("\n<one_SL2P_param> total numb of nets:", total_nets.getInfo())
  print("\n<one_SL2P_param> nParams and nClasses:", numbParams, numClasses.getInfo())

  #==========================================================================================================
  # Create a list of networks in ee.Dictionary format for all biophysical parameters.
  # In case of multiple classes are applied, each element in above list is another list of networks for 
  # diverse land cove types.  
  #==========================================================================================================
  #make_DNet_arr(coll_nets, numClasses, 1)
  DNet_arr = ee.List.sequence(1, numbParams).map(lambda paramID: make_DNet_arr(coll_nets, numClasses, paramID))

  #==========================================================================================================
  # Define a function that can estimate a biophysical parameter and its corresponding QC image
  #==========================================================================================================   
  def estimate_param_QC(ProdName, QC_img):
    prod_dict = PROD_OPTIONS[str(ProdName).upper()]
    estim_img, NetID_map = wrapperNNets(DNet_arr, ClassImg, prod_dict, coll_dict, "estimate", mosaic)

    # Identify the pixels exceeding the output range 
    out_min    = ee.Image(prod_dict['outmin'])
    out_max    = ee.Image(prod_dict['outmax'])
    range_mask = estim_img.lt(out_min).Or(estim_img.gt(out_max)).multiply(ee.Image(2))
    QC_img     = QC_img.bitwiseOr(range_mask)

    scaling_factor = ee.Image(prod_dict['scale_factor'])
    estim_img      = estim_img.where(estim_img.lt(0), ee.Image(0)).multiply(scaling_factor)

    return estim_img.uint8(), QC_img.uint8()  #, NetID_map

  #==========================================================================================================
  # Estimate FOUR biophysical parameter maps and QC map, and then export them separately
  #==========================================================================================================
  if task_list != None:
    for prod_name in inParams['prod_names']: 
      veg_param_map, QC_img = estimate_param_QC(prod_name, QC_img)
      Img.export_one_map(inParams, Region, veg_param_map, prod_name, task_list)  
  
    #==========================================================================================================
    # Set flags/marks in the 3rd bit of "QC_img" for all kinds of invalid pixels (cloud, shadow, snow, ice, 
    # water, saturated or out of range) 
    #==========================================================================================================  
    Year = inParams['year']
    invalid_mask = LEAF_valid_mask(inMosaic, Year, SsrData, 1, ClassImg).multiply(ee.Image(4)).uint8()
    QC_map       = QC_img.unmask().bitwiseOr(invalid_mask)

    Img.export_one_map(inParams, Region, QC_map, 'QC', task_list)
    






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

  sl2p_Domain = coll_dict["sl2pDomain"].aggregate_array("DomainCode").sort()
  bandList    = ee.List(coll_dict["inputBands"])
  LEAF_image  = inMosaic.select(bandList.slice(3))  #Only select required spectral bands
  nBands      = bandList.slice(3).length()

  QC_img = LEAF_image.multiply(ee.Image.constant(10)).ceil().mod(ee.Number(10))\
                     .multiply(ee.Image.constant(ee.List.sequence(0, nBands.subtract(1)).map(lambda value: ee.Number(10).pow(ee.Number(value))))) \
                     .reduce("sum").remap(sl2p_Domain, ee.List.repeat(0, sl2p_Domain.length()), 1).uint8()

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
# Description: This function answers if a "InquireStr" is included in "ProductList" list that contains 
#              optional products (e.g., 'lai', 'fapar', 'fcover', 'albedo', 'date', 'partition' or 'RGB') 
#              from LEAF production tool.
#
# Revision history:  2022-Oct-27  Lixin Sun  Initial creation 
#
#############################################################################################################
def Is_export_required(InquireStr, ProductList):
  '''This function answers if a "InquireStr" is included in "ProductList" list.

     Args:
       InquireStr(string): A string that is inquired.
       ProductList(string): A list of prodcut strings to be exported by LEAF production tool.'''  
  low_inquire = InquireStr.lower()

  for prod in ProductList:
    prod_low = prod.lower()
    if prod_low.find(low_inquire) != -1:
      return True

  return False




#############################################################################################################
# Description: Produces LEAF products for a customized spatial region and time window or a specified scene
# 
# Note: There are the following three situations where this function will be called:
#       (1) A ee.Geometry.Polygon object is provided as the value corresponding to "custom_region" key
#       (2) A user-specified scene ID is provided as the value corresponding to "scene_ID" key
#       (3) A time window is provided as the values corresponding to "start_date" and "end_date" keys
#
# Revision history:  2023-Nov-26  Lixin Sun  Initial creation 
#
#############################################################################################################
def apply_SL2P(inParams, task_list, ExportMosaic=False):
  '''Produces LEAF products for one or multiple tiles in CANADA

    Args:
      inParams(Dictionary): A dictionary containing all execution input parameters;
      task_list([]): a list for storing the exporting tasks;
      outputMosaic(Boolean): A flag indicating if to export used mosaic image.'''  
  
  print('<apply_SL2P> All parameters:', inParams) 

  #==========================================================================================================
  # Obtain some required parameters
  #==========================================================================================================
  SsrData     = Img.SSR_META_DICT[inParams['sensor']]
  year        = int(inParams['year'])
  SceneID     = inParams['scene_ID']       # An optional ID of a single scene/granule 
  ProductList = inParams['prod_names']     # A list of products to be generated
  region_name = str(inParams['current_region'])

  start, stop = eoPM.get_time_window(inParams, False)
  region      = eoPM.get_spatial_region(inParams)
  
  if 'tile' in region_name:
    region = eoTG.expandSquare(region, 0.02)   

  #==========================================================================================================
  # Obtain a global Land cover classification map and export it as needed 
  #==========================================================================================================
  ClassImg = eoAD.get_GlobLC(year, False).uint8().clip(region)
  if Is_export_required('parti', ProductList):
    Img.export_one_map(inParams, region, ClassImg, 'Partition', task_list)

  #==========================================================================================================
  # If scene_ID is provided, ontain its footprint as ROI
  #==========================================================================================================
  if len(SceneID) > 5: 
    # Obtain the specified single scene and its footprint
    ssr_code, tile_str, refer_date_str, valid_ID = Img.parse_ImgID(SceneID)  # parse the given image ID string
    
    if valid_ID == True and SsrData['SSR_CODE'] == ssr_code:
      image  = ee.Image(SsrData['GEE_NAME'] + '/' + SceneID) 
      image  = Img.apply_gain_offset(image, SsrData, 1, 10)  # convert SR to range between 0 and 1
      image  = Img.attach_AngleBands(image, SsrData)         # attach three imaging angle bands
      region = ee.Image(image).geometry()
      
      SL2P_separate_params(inParams, image, region, SsrData, ClassImg, task_list)

  else: 
    ScoreWs = inParams['score_weights'] if 'score_weights' in inParams else None
    mosaic = Mosaic.LEAF_Mosaic(SsrData, region, start, stop, True, ScoreWs)   
    print("\n<apply_SL2P> The band names in mosiac image = ", mosaic.bandNames().getInfo())

    SL2P_separate_params(inParams, mosaic, region, SsrData, ClassImg, task_list)
     
    if ExportMosaic:      
      Mosaic.export_mosaic(inParams, mosaic, SsrData, region, True, task_list)

    elif 'tile' in region_name:
      date_map = mosaic.select([Img.pix_date])
      Img.export_one_map(inParams, region, date_map, 'Date', task_list)        
    
    




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
def LEAF_production(inParams, ExportMosaic=False):
  '''Produces monthly biophysical parameter maps for a number of tiles and months.

    Args:
      inParamDict(Dictionary): A Python dictionary storing all input parameters for one execution;
      ExportMosaic(Boolean): A flag indicating if to export the used mosaic image.'''

  #==========================================================================================================
  # Standardize the given execution parameters
  #==========================================================================================================
  params = eoPM.get_LEAF_params(inParams)
  
  #==========================================================================================================
  # Produce vegetation parameter porducts for eath region and each time window
  #==========================================================================================================
  task_list = []
  region_names = params['regions'].keys()
  nTimes = len(params['start_dates'])

  # Produce vegetation parameter products for each spatial region
  for reg_name in region_names:
    eoPM.set_spatial_region(params, reg_name)

    # Produce vegetation parameter porducts for each time window
    for TIndex in range(nTimes):
      eoPM.set_current_time(params, TIndex)

      # Produce and export products in a specified way (a compact image or separate images)      
      print('\n<LEAF_production> Generate and export separate biophysical maps for {}th time period and {} region......'.format(TIndex, reg_name))        
      apply_SL2P(params, task_list, ExportMosaic)

      # out_style = str(params['export_style']).lower()
      # if out_style.find('comp') > -1:
      #   print('\n<LEAF_production> Generate and export biophysical maps in one file .......')
      #   #out_params = compact_params(mosaic, SsrData, ClassImg)

      #   # Export the 64-bits image to either GD or GCS
      #   #export_compact_params(fun_Param_dict, region, out_params, task_list)

      # else: 
      #   # Produce and export vegetation parameetr maps for a time period and a region
      #   print('\n<LEAF_production> Generate and export separate biophysical maps for {}th time period and {} region......'.format(TIndex, reg_name))        
      #   apply_SL2P(params, task_list, ExportMosaic)    
     
  return task_list




# def LEAF_production_old(inParams):
#   '''Produces monthly biophysical parameter maps for a number of tiles and months.

#      Args:
#        ExeParamDict(Python Dictionary): A Python dictionary storing all input parameters for one execution.'''

#   #==========================================================================================================
#   # Standardize the given execution parameters
#   #==========================================================================================================
#   params = eoPM.get_LEAF_params(inParams)

#   #==========================================================================================================
#   # Deal with three scenarios: customized spatial region, customized compositing period and regular tile 
#   #==========================================================================================================
#   task_list = []

#   if eoPM.is_custom_region(params) or eoPM.is_custom_window(params):   
#     # There is a customized spatial region specified in Parameter dictionary 
#     print('\n<LEAF_production> Calling custom_composite function......')
#     custom_LEAF_production(params, task_list)

#   else: 
#     # There is neither customized region nor customized compositing period defined in Parameter dictionary 
#     print('\n<LEAF_production> Calling tile_composite function......')
#     tile_LEAF_production(params, task_list)  
    
#   return task_list





# Ottawa_region = ee.Geometry.Polygon([[-75.96625073107825,45.260057944138275], [-75.73210461291418,45.260057944138275],
#                                      [-75.73210461291418,45.39136958969806],  [-75.96625073107825,45.39136958969806], 
#                                      [-75.96625073107825,45.260057944138275]])

# params =  {
#      'sensor': 'S2_SR',           # A sensor type string (e.g., 'S2_SR' or 'L8_SR')
#      'unit': 2,                   # A data unit code (1 or 2 for TOA or surface reflectance)   
#      'year': 2024,                # An integer representing image acquisition year
#      'nbYears': 1,                # positive int for annual product, or negative int for monthly product
#      'months': [8],               # A list of integers represening one or multiple monthes     
#      'tile_names': ['tile45_911'],    # A list of (sub-)tile names (defined using CCRS' tile griding system) 
#      'prod_names': ['LAI', 'fCOVER', 'fAPAR', 'Albedo'],       #['mosaic', 'LAI', 'fCOVER',  'fAPAR', 'Albedo']
#      'out_location': 'drive',        # Exporting location ('drive', 'storage' or 'asset') 
#      'resolution': 20,            # Exporting spatial resolution
#      'GCS_bucket': 's2_mosaic_2020',  # An unique bucket name on Google Cloud Storage
#      'out_folder': 'tile45_2024_for_Sean_new',   # the folder name for exporting
#      'export_style': 'comp',
     
#      #'start_dates': ['2022-07-01'],
#      #'end_dates': ['2022-07-15'],
# }

# LEAF_production(params, True)
