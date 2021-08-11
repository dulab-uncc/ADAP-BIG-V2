""" conversion module

-convert mzml inference boxes into specific m/z and rt values

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

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

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

def getinferencefilenames():
   templist =  listdir(params.txt_inference_path)
   final_list = []
   for txtfile in templist:
       idxofdot = 0
       for i in range(len(txtfile)):
           if(txtfile[i] == "."):
               idxofdot = i
       final_list.append(txtfile[9:idxofdot])
   return final_list

def convert(mz_rt_img, intensity_img, filenamelist, inferencearr, window_mz, window_rt):
    mzrtvalarr = []
    finalarr = []
    for i in range(len(filenamelist)):
        idxofimg = int(filenamelist[i])-1
        img = mz_rt_img[idxofimg]
        for inference in inferencearr[i]:
            centerx = round(float(inference[1]) * 640 / (640/(window_mz*2)))
            centery = round(float(inference[2]) * 480 / (480/(window_rt*2)))
            width= round(float(inference[3]) * 640 / (640/(window_mz*2)))
            height = round(float(inference[4]) * 480 / (480/(window_rt*2)))

            maxintensitycoords = [0,0]
            maxintensity = 0
            for timeval in range(centery - math.floor(height/2), centery + math.floor(height/2)):
                for mzval in range(centerx - math.floor(width/2), centerx + math.floor(width/2)):
                    if (intensity_img[idxofimg][timeval][mzval] > maxintensity):
                        maxintensity = intensity_img[idxofimg][timeval][mzval]
                        maxintensitycoords = [timeval, mzval]

            poscenterinimg = 50 * maxintensitycoords[0] + maxintensitycoords[1]
            mzrtval = img[poscenterinimg]
            mzrtvalarr.append(mzrtval)
            mzleft = img[centerx - math.floor(width/2)][1]
            mzright = img[centerx + math.floor(width/2)][1]
            rtleft = img[50 * (centery - math.floor(height/2) - 1)][0]
            rtright = img[50 * (centery + math.floor(height/2) - 1)][0]

            finalintensity = pow(10, maxintensity)
            finalarr.append([mzrtval[1], mzrtval[0], mzleft, mzright, rtleft, rtright, finalintensity, round(float(inference[5]) * 100, 3)])
            #savetestimg(mzrtval[1], mzrtval[0], params.window_rt, params.window_mz)
            #breakpoint()

    return pd.DataFrame(np.array(finalarr), columns=['M/Z', 'Retention Time', 'M/Z Left Range', 'M/Z Right Range', "Retention Time Left Range", "Retention Time Right Range", "Intensity", "Model Confidence"])

def savetestimg(mz, rt, window_rt, window_mz):
    scan_t = extract_timevals(params.profile_mzml_path)
    mz_list = extract_mzvals(params.profile_mzml_path, 0, len(scan_t))
    intensity_list = extract_intensities(params.profile_mzml_path, 0, len(scan_t))

    if (len(scan_t) > 2 and scan_t[1] - scan_t[0] > 0.1):  ## if gap >0.1: second..
        scan_t = [i / 60.0 for i in scan_t]

    if not os.path.isdir(r'../mzml-img-detection-debug'):
        os.system('mkdir .\mzml-img-detection-debug')
    time = scan_t.index(find_nearest(scan_t, rt))
    mzvalue = mz_list[time].index(find_nearest(mz_list[time], mz))

    pos_rt = time
    pos_rt1 = pos_rt - window_rt
    pos_rt2 = pos_rt + window_rt
    if pos_rt2 >= len(scan_t):
        pos_rt1 = len(scan_t) - window_rt * 2
        pos_rt2 = len(scan_t)
    elif pos_rt1 < 0:
        pos_rt1 = 0
        pos_rt2 = 2 * window_rt

    pos_mzorig = mzvalue
    pos_mz1orig = pos_mzorig - window_mz
    pos_mz2orig = pos_mzorig + window_mz

    if pos_mz2orig >= len(mz_list):
        pos_mz1orig = len(mz_list) - window_mz * 2
        pos_mz2orig = len(mz_list)
    elif pos_mz1orig < 0:
        pos_mz1orig = 0
        pos_mz2orig = 2 * window_mz

    mzvalarrsplit = []
    for mzmz in range(window_mz, -1, -1):
        mzvalarrsplit.append(round(mz_list[int(pos_rt)][int(pos_mzorig - mzmz)], 6))
    for mzmz in range(1, window_mz):
        mzvalarrsplit.append(round(mz_list[int(pos_rt)][int(pos_mzorig + mzmz)], 6))

    ## Creating the image from calculated ranges ##
    area = []
    for t in range(pos_rt1, pos_rt2):
        htgrids = intensity_list[t]
        grids_part = []
        for m in range(len(mzvalarrsplit)):
            pos_mz = mz_list[t].index(find_nearest(mz_list[t], mzvalarrsplit[m]))
            grids_part.append(htgrids[pos_mz])
        area.append(grids_part)


    ## Taking log of each intensity in the image and saving the attribute to the corresponding peak object ##
    for l in range(0, len(area)):
        for m in range(0, len(area[0])):
            if (area[l][m] > 0):
                area[l][m] = np.log10(area[l][m])

    ## Create figure and axes objects. Adjust values and create the image ##
    plt.imshow(area, cmap='Greys', aspect='auto')
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.savefig(r'.\mzml-img-detection-debug\debugimg2.png')
    plt.close('all')