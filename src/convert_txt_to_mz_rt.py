"""

CONVERT LOCAL COORDINATES TO M/Z RT INTENSITY MODULE

-convert mzml inference boxes into specific m/z and rt values
-return dataframe which can then be exported as a .CSV file

"""
from os import listdir
import os
from os.path import isfile, join
import params
from mzml_reader import extract_mzvals, extract_timevals, extract_intensities
import pandas as pd
import numpy as np
import math
from numpy import loadtxt
from collections import OrderedDict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
from pathlib import Path

"""
Helper function
Finds nearest value in array to the value parameter
"""
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

"""
Get array of all .txt inference data including center, box length/width, confidence for each block image
"""
def getinferencearrs():
    onlyfiles = listdir(params.txt_inference_path)
    arr_of_inferences = []
    for file in onlyfiles:
        with open(params.txt_inference_path + "\\" + file) as my_file:
            txt = my_file.read().splitlines()
            splitarr = []
            for arr in txt:
                splitarr.append(arr.split())
            arr_of_inferences.append(splitarr)
    return arr_of_inferences

"""
Get array of all block numbers with peaks detected inside
"""
def getinferencefilenames():
   templist =  listdir(params.txt_inference_path)
   final_list = []
   for txtfile in templist:
       idxofdot = 0
       for i in range(len(txtfile)):
           if(txtfile[i] == "."):
               idxofdot = i
       final_list.append(txtfile[9:idxofdot])
   #breakpoint()
   return final_list

"""
Main conversion function
Converts local coordinates predicted by yolov5 into m/z and rt of most intense value in the area of m/z, rt pixel values
"""
def convert(mz_rt_img, intensity_img, filenamelist, inferencearr, window_mz, window_rt):
    mzrtvalarr = []
    finalarr = []
    for i in range(len(filenamelist)):
        #Go through each block, and since that block # - 1 equals the index of the image containing each pixel with m/z and rt in the mz_rt_img array, we can navigate to the cached data
        idxofimg = int(filenamelist[i])-1
        img = mz_rt_img[idxofimg]
        for inference in inferencearr[i]:
            # Iterate through each inference box in each image (since one image can have multiple objects detected)
            # Convert local proportion of image values into pixel values, then since for example, 640/window_mz*2 pixels represent each actual visible "box" value of m/z and rt and intensity
            # After you have the number of pixels into the image the center is, we convert that by diving how many pixels each box is and we have the # box that the peak is in
            #breakpoint()
            centerx =  - round(float(inference[1]) * (2*window_mz))
            centery = round(float(inference[2]) * (2*window_rt))
            width= round(float(inference[3]) * (2*window_mz))
            height = round(float(inference[4]) * (2*window_rt))
            #breakpoint()
            # Get all boxes in the range of the bounding box and find the intensity for each value, saving the maximum intensity index in the image (horiz = mzval index, vertical = timeval index)
            maxintensitycoords = [0,0]
            maxintensity = 0
            for timeval in range(centery - math.floor(height/2), centery + math.floor(height/2)):
                for mzval in range(centerx - math.floor(width/2), centerx + math.floor(width/2)):
                    if (intensity_img[idxofimg][timeval][mzval] > maxintensity):
                        maxintensity = intensity_img[idxofimg][timeval][mzval]
                        mzrtval = img[timeval][mzval]
            #breakpoint()
            # Calculate index in the mz_rt_img arr of the mz, rt value so we can get the exact mz and rt time value of the peak
            #poscenterinimg = 60 * maxintensitycoords[0] +
            #imgcenter = img[60 * centery + centerx]
            mzrtval[0] = round(mzrtval[0], 8)
            mzrtval[1] = round(mzrtval[1], 8)
            mzrtvalarr.append(mzrtval)

            #correct mzrange around 0.015 or 0.013
            mzleft = img[centery][centerx][1] - 0.0075
            mzright = img[centery][centerx][1] + 0.0075

            #max time 0.5 min, min anything below 0.5min
            rtleft = img[centery - math.floor(height/2)][centerx][0]
            rtright = img[centery + math.floor(height/2) - 1][centerx][0]

            #Convert intensity from log10 back to original to save in dataframe
            finalintensity = maxintensity

            #Create dataframe
            finalarr.append([filenamelist[i], mzrtval[1], mzrtval[0], mzleft, mzright, rtleft, rtright, finalintensity, round(float(inference[5]) * 100, 3)])

    return pd.DataFrame(np.array(finalarr), columns=['Block Number', 'M/Z', 'Retention Time', 'M/Z Left Range', 'M/Z Right Range', "Retention Time Left Range", "Retention Time Right Range", "Intensity", "Model Confidence"])