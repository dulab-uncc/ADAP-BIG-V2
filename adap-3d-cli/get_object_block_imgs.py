"""

MZML FILE IMAGE BLOCKING MODULE

-Conducts mzml file scan for all times, mz, and intensity values corresponding to scans
-Generates images
-Saves image to hard-drive
-Returns two useful arrays (mz, rt array and intensity array) for converting local coordinates to m/z and rt values

"""

import numpy as np
import pandas as pd
from mzml_reader import extract_mzvals, extract_timevals, extract_intensities
import matplotlib.pyplot as plt
import matplotlib
import params
import math
matplotlib.use("Agg")
import os

"""
Helper function to locate time edge values
"""
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx] #return value nearest to passed in value (in specified array)

"""
1: Extract block images including every possible M/Z value in the time range
2: Return array containing two arrays:
    a) corresponding m/z and rt values for each pixel in each image
    b) intensity value of each m/z value (pixel corresponding, same shape)
"""
def get_image_for_blocks(profile_file_mzML, window_mz=60, window_rt=300, timetoignoreL = 2, timetoignoreR = 20):

    #Run scan to get times for each scan number, mz list of raw, not rounded values, and intensities of m/z values
    scan_t = extract_timevals(profile_file_mzML)
    mz_list_raw = extract_mzvals(profile_file_mzML, 0, len(scan_t))
    intensity_list = extract_intensities(profile_file_mzML, 0, len(scan_t))

    cnt = 0 # initialize block count
    arr_of_mz_rt = [] # initialize array of [m/z, rt] corresponding to each pixel in each image produced
    intensitiesarr = [] # initialize array of intensities corresponding to each pixel in each image produced
    mz_list = [] # initialize array of m/z values rounded

    # Round all m/z values to nearest 4th, can alter
    for mzarr in mz_list_raw:
        templist = []
        for val in mzarr:
            templist.append(round(val, 4))
        mz_list.append(templist)

    # Cleaning up scan_t data
    if (len(scan_t) > 2 and scan_t[1] - scan_t[0] > 0.1):  ## if gap >0.1: second..
        scan_t = [i / 60.0 for i in scan_t]

    #Add a check to remove rt before and after for noise
    timetoignoreleft = scan_t.index(find_nearest(scan_t, timetoignoreL))
    timetoignoreright = scan_t.index(find_nearest(scan_t, timetoignoreR))

    # Initialize for loops to create blocks
    for time in range(timetoignoreleft+window_rt, timetoignoreright-window_rt, window_rt*2):

        # Find index and length of longest mzarr in time range so no mz values are left out.
        # All mzarrs start and end at the same values but some arrays contain more values in between, so we need to include those
        idxoflargestmzarr = 0
        maxlen = 0
        for i in range(time-window_rt, time+window_rt):
            if(len(mz_list[i]) > maxlen):
                maxlen = len(mz_list[i])
                idxoflargestmzarr = i

        # Iterate through m/z values in time range to create blocks
        for mz in range(window_mz, maxlen-window_mz, window_mz*2):

            cnt += 1
            # Create indexes of time of entire mzarr
            pos_rt = idxoflargestmzarr

            # Adjust index boundaries to create a 50x130 image that doesn't overlap since we want all mz values based from the largest mzarr to include all the possible values we can
            # (may not be in the center of the image)
            pos_rt1 = pos_rt - (window_rt + (idxoflargestmzarr - time))
            pos_rt2 = pos_rt + (window_rt - (idxoflargestmzarr - time))
            if pos_rt2 >= len(scan_t):
                pos_rt1 = len(scan_t) - window_rt * 2
                pos_rt2 = len(scan_t)
            elif pos_rt1 < 0:
                pos_rt1 = 0
                pos_rt2 = 2 * window_rt

            # Set index of mz value in the longestmzarr and make windows
            pos_mzorig = mz
            pos_mz1orig = pos_mzorig - window_mz
            pos_mz2orig = pos_mzorig + window_mz
            mzvalarrsplit = []

            # Go through every m/z value in the longest mzarr that is within 50 values and saving them to an array to be used in image creation
            # Because the m/z values are not always in the same index position, we will use .index and find_neares()
            for mzmz in range(window_mz, -1, -1):
                mzvalarrsplit.append(round(mz_list[int(pos_rt)][int(pos_mzorig - mzmz)], 6))
            for mzmz in range(1, window_mz):
                mzvalarrsplit.append(round(mz_list[int(pos_rt)][int(pos_mzorig + mzmz)], 6))

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
                    try:
                        pos_mz = mz_list[t].index(mzvalarrsplit[m])
                        grids_part.append(htgrids[pos_mz])
                        arrofmzrttemp.append([scan_t[t], mzvalarrsplit[m]])
                    except ValueError:
                        grids_part.append(0)
                        arrofmzrttemp.append([0, 0])
                area.append(grids_part)
            arr_of_mz_rt.append(arrofmzrttemp)
            intensitiesarr.append(area)

            # Taking log of each intensity in the image
            for l in range(0,len(area)):
                for m in range(0,len(area[0])):
                    if(area[l][m] > 0):
                        area[l][m] = np.log10(area[l][m])

            # Render array as an image and save it to local drive path
            plt.imshow(area, cmap='Greys', aspect='auto')
            plt.gca().set_axis_off()
            plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
            plt.margins(0, 0)
            plt.savefig(r'.\mzml-img-blocks-new\ ' + "Block # " + str(cnt) + '.png')
            plt.close('all')

    return arr_of_mz_rt, intensitiesarr





