import sys
import numpy as np
import bisect as bs
import pandas as pd
import MZML_READER as read
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import logging
import os

#Helper function for when attribute values are too rounded in order to locate them in an array
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def get_image_for_blocks(profile_file_mzML, RESULTS_PATH, window_mz=60, window_rt=300):
    dataFramePrevEvaluation = pd.read_csv(r"C:\Users\jerry\Desktop\DCSM.csv")
    predictionsArrTime = dataFramePrevEvaluation['retention_time']
    predictionsArrMz = dataFramePrevEvaluation['mz']
    inputfile = profile_file_mzML
    if not os.path.isdir(RESULTS_PATH + '\Signal_Images\DCSM_IMGS'):
        os.system('mkdir .\Results\Signal_Images\DCSM_IMGS')
    if not os.path.isdir(RESULTS_PATH + '\Signal_Images\CONFIRMED_PEAKS'):
        os.system('mkdir .\Results\Signal_Images\CONFIRMED_PEAKS')

    ## Scanning the raw mzML file into array data ##
    scan_t = read.extract_timevals(inputfile)
    mz_list = read.extract_mzvals(inputfile, 0, len(scan_t))
    intensity_list = read.extract_intensities(inputfile, 0, len(scan_t))
    cnt = 1
    ## Cleaning up data ##
    if (len(scan_t) > 2 and scan_t[1] - scan_t[0] > 0.1):  ## if gap >0.1: second..
        scan_t = [i / 60.0 for i in scan_t]

    ## Extract image for each CWT detected peak, Can adjust to take blocks from entire mzML file if needed ##
    #for time in range(pos_time_val1+window_rt, pos_time_val2-window_rt, window_rt-60):
        #indexLargestMZ = len(max(mz_list, key=len))
        #for mzval in range(window_mz, indexLargestMZ-window_mz, window_mz-30):
    mzarr = [164.0909, 189.0875, 153.0664, 181.0613, 140.0348, 166.0728, 216.0427, 222.9960, 220.1185, 205.0977, 164.0712, 373.0955, 373.0955, 197.0614, 155.0167, 209.0814, 224.1287, 243.0770, 286.1113, 231.1596,  245.1753, 245.1753,475.3900   ]
    timearr = [0.66, 1.17, 1.94, 2.31, 2.65, 2.94, 3.25, 3.90, 4.00, 4.26, 6.08, 6.90, 7.15, 7.97, 8.40, 9.68, 9.88, 10.83, 11.18, 11.54,11.56, 12.28, 14.25 ]
    for time in range(len(mzarr)):
    #for time in range(len(predictionsArrTime)):
        cnt+=1
        #if(float(predictionsArrTime[time]) < 20.0 and float(predictionsArrTime[time]) > 2.5):
        mz0 = mzarr[time]
        rt0 = timearr[time]
        #mz0 = predictionsArrMz[time]
        #rt0 = predictionsArrTime[time]

        pos_rt=scan_t.index(find_nearest(scan_t, rt0))
        pos_rt1 = pos_rt - window_rt
        pos_rt2 = pos_rt + window_rt
        if pos_rt2 >= len(scan_t):
            pos_rt1 = len(scan_t) - window_rt * 2
            pos_rt2 = len(scan_t)
        elif pos_rt1 < 0:
            pos_rt1 = 0
            pos_rt2 = 2 * window_rt

        pos_mzorig = mz_list[pos_rt].index(find_nearest(mz_list[pos_rt], mz0))

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
            mzvalarrsplit.append(round(mz_list[pos_rt][pos_mzorig - mzmz], 6))
        for mzmz in range(1, window_mz):
            mzvalarrsplit.append(round(mz_list[pos_rt][pos_mzorig + mzmz], 6))



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
        for l in range(0,len(area)):
            for m in range(0,len(area[0])):
                if(area[l][m] > 0):
                    area[l][m] = np.log10(area[l][m])

        ## Create figure and axes objects. Adjust values and create the image ##
        fig, ax = plt.subplots()
        fig.set_figheight(10)
        fig.set_figwidth(15)
        img = ax.imshow(area, cmap='Greys', aspect= 'auto')

        ## Label each pixel with Intensity, *uncomment* to use ##
        #for y in range(0, window_rt*2):
            #for x in range(0, window_mz*2):
                #text = ax.text(x, y, round(area[y][x], 3),
                               #ha="center", va="center", color="w")

        ## Setting ticks and values according to the window mz and window rt ##
        xticks = []
        xlabels = []
        yticks = []
        ylabels = []
        for xtick in range(2*window_mz):
            xticks.append(xtick)
        for xlabel in range(2*window_mz):
            xlabels.append(round(mzvalarrsplit[xlabel], 3))
        for ytick in range(2*window_rt):
            yticks.append(ytick)
        for ylabel in range(2*window_rt):
            ylabels.append(round(scan_t[pos_rt1+ylabel], 3))
        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels)
        ax.set_yticks(yticks)
        ax.set_yticklabels(ylabels)
        every_nth = 6
        for n, label in enumerate(ax.xaxis.get_ticklabels()):
            if n % every_nth != 0:
                label.set_visible(False)
        for n, label in enumerate(ax.yaxis.get_ticklabels()):
            if n % every_nth != 0:
                label.set_visible(False)
        #plt.locator_params(nbins = 3)
        ## Create title, axes labels, and colorbar ##
        fig.suptitle("Prediction " + str(cnt) + " M/Z: " + str(mz0) + "  RT: " + str(rt0))
        plt.xlabel('M/Z')
        plt.ylabel('Retention Time')
        fig.colorbar(img)
        plt.savefig(RESULTS_PATH + '\Signal_Images\CONFIRMED_PEAKS\ ' + str(cnt) + '.png')
        plt.close()
        #breakpoint()
        #breakpoint()
    #Return peak objects with images attatched, create breakpoint to evaluate for debug






