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
from mzml_reader import extract_mzvals, extract_timevals, extract_intensities
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('pdf')
import params
import math
import os
import gc
plt.rcParams["figure.figsize"] = (0.6 ,1.4)
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
def get_image_for_blocks(profile_file_mzML, window_mz=70, window_rt=65, timetoignoreL = 2, timetoignoreR = 20):

    #Run scan to get times for each scan number, mz list of raw, not rounded values, and intensities of m/z values
    scan_t = extract_timevals(profile_file_mzML)
    mz_list = extract_mzvals(profile_file_mzML, 0, len(scan_t))
    intensity_list = extract_intensities(profile_file_mzML, 0, len(scan_t))

    cnt = 0 # initialize block count
    arr_of_mz_rt = [] # initialize array of [m/z, rt] corresponding to each pixel in each image produced
    intensitiesarr = [] # initialize array of intensities corresponding to each pixel in each image produced

    # Cleaning up scan_t data
    if (len(scan_t) > 2 and scan_t[1] - scan_t[0] > 0.1):  ## if gap >0.1: second..
        scan_t = [i / 60.0 for i in scan_t]

    #Add a check to remove rt before and after for noise
    timetoignoreleft = scan_t.index(find_nearest(scan_t, timetoignoreL))
    timetoignoreright = scan_t.index(find_nearest(scan_t, timetoignoreR))

    # Initialize for loops to create blocks
    for time in range(timetoignoreleft + window_rt, timetoignoreright, window_rt * 2):
        # Find index and length of longest mzarr in time range so no mz values are left out.
        # All mzarrs start and end at the same values but some arrays contain more values in between, so we need to include those

       # allmzintime = []
        #for i in range(time-window_rt, time+window_rt):
            #for j in range(0, len(mz_list[i])):
                #allmzintime.append(mz_list[i][j])
        #allmzintime = sorted(set(allmzintime))
        #newallmzintime = []
        #tempmz = []

        #for i in np.arange(allmzintime[0], allmzintime[len(allmzintime) - 1], 0.005):
            #tempmz.append(i)

        #for j in range(len(tempmz)):
            #newallmzintime.append(find_nearest(allmzintime), tempmz[j])


        #for i in range(0, len(allmzintime), 35):
            #newallmzintime.append(allmzintime[i])

        allmzintime = []
        allintensityintime = []
        for i in range(pos_rt1, pos_rt2):
            for j in range(len(mz_list[i])):
                allmzintime.append(mz_list[i][j])
                allintensityintime.append(intensity_list[i][j])

        tempmz = []

        for i in np.arange(allmzintime[0], allmzintime[len(allmzintime) - 1], 0.0005):
            tempmz.append(i)

        tempmz[len(tempmz) - 1] = tempmz[len(tempmz) - 1] + 0.1
        binnedvals = list(pd.cut(np.array(allmzintime), tempmz, right=False, labels=False))

        newbinnedmz = []
        newbinnedintensity = []
        templistmz = []
        templistintensity = []

        for i in range(1, len(binnedvals)):

            if (binnedvals[i] == binnedvals[i - 1]):
                templistmz.append(allmzintime[i])
                templistintensity.append(allintensityintime[i])
            elif len(templistmz) > 0:
                newbinnedmz.append(allmzintime[i])
                newbinnedintensity.append(allintensityintime[i])
            else:
                newbinnedintensity.append(max(templistintensity))
                newbinnedmz.append(templistmz[templistintensity.index(max(templistintensity))])
                templistmz = []
                templistintensity = []

        newallmzintime = newbinnedmz


        # Iterate through m/z values in time range to create blocks
        for pos_mz in range(window_mz, len(newallmzintime), window_mz*2):
            if(pos_mz > (len(newallmzintime) - window_mz)):
                pos_mz = len(newallmzintime) - window_mz

            cnt += 1
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

            mzvalarrsplit = []
            for mzmz in range(pos_mz - window_mz, pos_mz + window_mz):
                mzvalarrsplit.append(newallmzintime[mzmz])

            # Creating the image from calculated ranges
            area = []
            arrofmzrttemp = []
            # Looping through all times in range
            for t in range(pos_rt1, pos_rt2):
                htgrids = intensity_list[t]
                grids_part = []
                for m in range(len(mzvalarrsplit)):
                # Going through every m/z value (50 total) in mzvalarrsplit and getting the intensity of that mzvalue in each different time value, saving it to an array
                    # If cannot locate mzvalue in that mzarr at time "t" append intensity of 0
                    pos_mz_bin = mz_list[t].index(find_nearest(mz_list[t], mzvalarrsplit[m]))

                    #Resolve case of multiple m/z values in the bin
                    if(pos_mz_bin > mz_list[t].index(find_nearest(pow(10, grids_part[len(grids_part) - 1])))):
                        bin_len_multiple = mz_list[t].index(find_nearest(pow(10, grids_part[len(grids_part) - 1])))
                        highest_intensity_bin = htgrids[bin_len_multiple + 1]
                        for i in range(mz_list[t].index(find_nearest(pow(10, grids_part[len(grids_part) - 1]) - pos_mz_bin )), pos_mz_bin):
                            if(ht_grids[i] > highest_intensity_bin):
                                highest_intensity_bin = ht_grids[bin_len_multiple + i]
                        grids_part.append(highest_intensity_bin)

                    elif (htgrids[pos_mz_bin] > 0):
                        grids_part.append(np.log10(htgrids[pos_mz_bin]))

                    else:
                        grids_part.append(htgrids[pos_mz_bin])
                    arrofmzrttemp.append([scan_t[t], mz_list[t][pos_mz_bin]])

                area.append(grids_part)
            arr_of_mz_rt.append(arrofmzrttemp)
            intensitiesarr.append(area)

            # Render array as an image and save it to local drive path
            plt.imshow(area, cmap='Greys', aspect='auto')
            plt.gca().set_axis_off()
            plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
            plt.margins(0, 0)
            plt.savefig(r'.\mzml-img-blocks-new-test-3\ ' + "Block # " + str(cnt) + '.png')
            plt.close('all')

        pickle.dump([cnt, arr_of_mz_rt, intensitiesarr], open(params.results_path + "\\saveADAP-Test-3.p", "wb"))
    return arr_of_mz_rt, intensitiesarr





