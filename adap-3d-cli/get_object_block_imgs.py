"""object blocking module

-Conducts mzml file scan for all times, mz, and intensity values corresponding to scans
-Generates images
-Saves image to hard-drive

"""

import numpy as np
import pandas as pd
from mzml_reader import extract_mzvals, extract_timevals, extract_intensities
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import os

#Helper function for when attribute values are too rounded in order to locate them in an array
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def get_image_for_blocks(profile_file_mzML, window_mz=60, window_rt=300, timetoignoreL = 2, timetoignoreR = 20, debugimageversion = False):
    ## Scanning the raw mzML file into array data ##
    inputfile = profile_file_mzML
    scan_t = extract_timevals(inputfile)
    mz_list = extract_mzvals(inputfile, 0, len(scan_t))
    intensity_list = extract_intensities(inputfile, 0, len(scan_t))
    cnt = 0
    arr_of_mz_rt = []

    ## Cleaning up data ##
    if (len(scan_t) > 2 and scan_t[1] - scan_t[0] > 0.1):  ## if gap >0.1: second..
        scan_t = [i / 60.0 for i in scan_t]

    #Add a check to remove rt before and after for noise
    timetoignoreleft = scan_t.index(find_nearest(scan_t, timetoignoreL))
    timetoignoreright = scan_t.index(find_nearest(scan_t, timetoignoreR))
    for time in range(timetoignoreleft+window_rt, timetoignoreright-window_rt, window_rt*2):
        for mz in range(window_mz, len(mz_list[time])-window_mz, window_mz*2):
            cnt += 1
            mz0 = mz_list[time][mz]
            rt0 = scan_t[time]

            pos_rt = time
            pos_rt1 = pos_rt - window_rt
            pos_rt2 = pos_rt + window_rt
            if pos_rt2 >= len(scan_t):
                pos_rt1 = len(scan_t) - window_rt * 2
                pos_rt2 = len(scan_t)
            elif pos_rt1 < 0:
                pos_rt1 = 0
                pos_rt2 = 2 * window_rt

            #pos_mzorig = mz_list[pos_rt].index(find_nearest(mz_list[pos_rt], mz0))
            pos_mzorig = mz
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
            arrofmzrttemp = []
            for t in range(pos_rt1, pos_rt2):
                htgrids = intensity_list[t]
                grids_part = []
                for m in range(len(mzvalarrsplit)):
                    pos_mz = mz_list[t].index(find_nearest(mz_list[t], mzvalarrsplit[m]))
                    grids_part.append(htgrids[pos_mz])
                    arrofmzrttemp.append([scan_t[t], mz_list[t][m]])
                area.append(grids_part)
            arr_of_mz_rt.append(arrofmzrttemp)


            ## Taking log of each intensity in the image and saving the attribute to the corresponding peak object ##
            for l in range(0,len(area)):
                for m in range(0,len(area[0])):
                    if(area[l][m] > 0):
                        area[l][m] = np.log10(area[l][m])

            ## Create figure and axes objects. Adjust values and create the image ##
            plt.imshow(area, cmap='Greys', aspect='auto')
            plt.gca().set_axis_off()
            plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
            plt.margins(0, 0)
            plt.savefig(r'.\mzml-img-blocks\ ' + "Block # " + str(cnt) + '.png')
            plt.close('all')

    return arr_of_mz_rt





