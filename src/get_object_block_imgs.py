"""

MZML FILE IMAGE BLOCKING MODULE

-Conducts mzml file scan for all times, mz, and intensity values corresponding to scans
-Generates images
-Saves image to hard-drive
-Returns two useful arrays (mz, rt array and intensity array) for converting local coordinates to m/z and rt values

"""

import numpy as np
import pandas as pd
import pickle
from PIL import Image
from mzml_reader import extract_mzvals, extract_timevals, extract_intensities
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('tkagg')
import params
import math
import os
import collections
import gc
plt.rcParams["figure.figsize"] = (0.96 , 1.6)
gc.collect()
"""
Helper function to locate time edge values
"""
def find_nearest(array,value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return array[idx-1]
    else:
        return array[idx]

"""
1: Extract block images including every possible M/Z value in the time range
2: Return array containing two arrays:
    a) corresponding m/z and rt values for each pixel in each image
    b) intensity value of each m/z value (pixel corresponding, same shape)
"""
def get_image_for_blocks(profile_file_mzML, window_mz=70, window_rt=65, timetoignoreL = 2, timetoignoreR = 20, min_intensity_threshold = 1000):

    #Run scan to get times for each scan number, mz list of raw, not rounded values, and intensities of m/z values
    scan_t = extract_timevals(profile_file_mzML)
    mz_list = extract_mzvals(profile_file_mzML, 0, len(scan_t))
    intensity_list = extract_intensities(profile_file_mzML, 0, len(scan_t))
    cnt = 0 # initialize block count
    arr_of_mz_rt = [] # initialize array of [m/z, rt] corresponding to each pixel in each image produced
    intensitiesarr = [] # initialize array of intensities corresponding to each pixel in each image produced
    blocknums = []

    # Cleaning up scan_t data
    if (len(scan_t) > 2 and scan_t[1] - scan_t[0] > 0.1):  ## if gap >0.1: second..
        scan_t = [i / 60.0 for i in scan_t]

    #Add a check to remove rt before and after for noise
    timetoignoreleft = scan_t.index(find_nearest(scan_t, timetoignoreL))
    timetoignoreright = scan_t.index(find_nearest(scan_t, timetoignoreR))

    # Initialize for loops to create blocks
    for time in range(timetoignoreleft + window_rt, timetoignoreright, window_rt * 2):
        # Create indexes of time of entire mzarr
        pos_rt = time

        # Adjust index boundaries to create a 50x130 image that doesn't overlap since we want all mz values based from the largest mzarr to include all the possible values we can
        # (may not be in the center of the image)
        pos_rt1 = pos_rt - window_rt
        pos_rt2 = pos_rt + window_rt

        if pos_rt2 >= len(scan_t):
            pos_rt1 = len(scan_t) - window_rt * 2
            pos_rt2 = len(scan_t)
        elif pos_rt1 < 0:
            pos_rt1 = 0
            pos_rt2 = 2 * window_rt
        # Find index and length of longest mzarr in time range so no mz values are left out.
        allmzintime = dict()

        for i in range(pos_rt1, pos_rt2):
            for j in range(len(mz_list[i])):
                allmzintime[mz_list[i][j]] = intensity_list[i][j]
        orderedmzintime = dict(collections.OrderedDict(sorted(allmzintime.items())))
        sortedmz = list(orderedmzintime.keys())
        tempmz = []
        binval = mz_list[pos_rt][1] - mz_list[pos_rt][0]
        for i in np.arange(sortedmz[0], sortedmz[len(sortedmz) - 1], 1.44 * binval):
            tempmz.append(i)

        tempmz[len(tempmz)-1] = tempmz[len(tempmz) - 1] + 0.001
        binnedvals = list(pd.cut(np.array(sortedmz), tempmz, right = False, labels = False))

        newbinnedmz = []
        newbinnedintensity = []

        tempmz1 = []
        tempintensity1 = []

        for i in range(1, len(binnedvals) - 1):

            if (binnedvals[i - 1] != binnedvals[i] and binnedvals[i + 1] != binnedvals[i]):
                newbinnedintensity.append(orderedmzintime[sortedmz[i]])
                newbinnedmz.append(sortedmz[i])
                tempmz1 = []
                tempintensity1 = []
            elif (binnedvals[i] != binnedvals[i - 1] and binnedvals[i] == binnedvals[i + 1] or (
                    binnedvals[i] == binnedvals[i - 1] and binnedvals[i] == binnedvals[i + 1])):
                tempmz1.append(sortedmz[i])
                tempintensity1.append(orderedmzintime[sortedmz[i]])
            elif (binnedvals[i] == binnedvals[i - 1] and binnedvals[i] != binnedvals[i + 1]):
                tempmz1.append(sortedmz[i])
                tempintensity1.append(orderedmzintime[sortedmz[i]])
                newbinnedintensity.append(max(tempintensity1))
                newbinnedmz.append(tempmz1[tempintensity1.index(max(tempintensity1))])
                tempmz1 = []
                tempintensity1 = []

        newallmzintime = newbinnedmz


        # Iterate through m/z values in time range to create blocks
        for pos_mz in range(window_mz, len(newallmzintime), window_mz*2):

            if(pos_mz > (len(newallmzintime) - window_mz)):
                pos_mz = len(newallmzintime) - window_mz - 1

            mzvalarrsplit = []
            intensitysplit = []
            for mzmz in range(pos_mz - window_mz, pos_mz + window_mz):
                mzvalarrsplit.append(newallmzintime[mzmz])
                intensitysplit.append(allmzintime[newallmzintime[mzmz]])
            # Creating the image from calculated ranges
            area = []
            arr_of_mz_rttemp = []
            # Looping through all times in range

            for t in range(pos_rt1, pos_rt2):
                intensitygrid = intensity_list[t]
                mzgrid = mz_list[t]
                mzleft = mzgrid.index(find_nearest(mzgrid, newallmzintime[pos_mz - window_mz]))
                mzright = mzgrid.index(find_nearest(mzgrid, newallmzintime[pos_mz + window_mz]))
                tempvalarrsplit = mzvalarrsplit
                tempvalarrsplit.append(tempvalarrsplit[len(tempvalarrsplit) - 1] + 0.05)
                tempvalarrsplit[0] = tempvalarrsplit[0] - 0.1
                binnedvals2 = list(pd.cut(np.array(mzgrid[mzleft: mzright + 1]), tempvalarrsplit, right=False, labels=False))
                finalbins = []
                finalbinsmzrt = []

                for i in range(window_mz * 2):
                    temparr = []
                    for j in range(len(binnedvals2)):
                        if (binnedvals2[j] == i):
                            temparr.append(intensitygrid[mzleft + j])
                    if (len(temparr) == 0):
                        if ((j > 1 and j < len(binnedvals2) - 1) and temparr[j - 1] != 0 and temparr[j + 1] != 0):
                            finalbins.append((temparr[j - 1] + temparr[j + 1]) / 2)
                            finalbinsmzrt.append([mzgrid[mzleft + j], scan_t[t]])
                        else:
                            finalbins.append(0)
                            finalbinsmzrt.append([0, scan_t[t]])
                    else:
                        finalbins.append(max(temparr))
                        finalbinsmzrt.append([mzgrid[mzleft + j], scan_t[t]])


                area.append(finalbins)
                arr_of_mz_rttemp.append(finalbinsmzrt)

            if (np.amax(area) > min_intensity_threshold):
                intensitiesarr.append(area)
                arr_of_mz_rt.append(arr_of_mz_rttemp)
                blocknums.append(cnt)

                # Render array as an image and save it to local drive path

                plt.imshow(area, cmap='Greys', aspect='auto', interpolation = None)
                plt.gca().set_axis_off()
                plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
                plt.margins(0, 0)
                plt.savefig(r'.\Blocks\ ' + "Block # " + str(cnt) + '.png')
                plt.close('all')

                cnt += 1
                #breakpoint()

        #pickle.dump([cnt, arr_of_mz_rt, intensitiesarr], open(params.results_path + "\\saveADAP-Test-3.p", "wb"))

    return blocknums, intensitiesarr, arr_of_mz_rt




