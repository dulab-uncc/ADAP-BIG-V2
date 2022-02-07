"""

MAIN MODULE

-Calls module to block the mzml file into images
-Conducts yolov5 inference using the command line and saves the predictions to txt and image files
-Converts inference .txt files into m/z and rt + ranges CSV file

Computer Specifications:

Intel(R) Core(TM) i7-7700 CPU @ 3.60GHz
NVIDIA GeForce GTX 1070
32 GB 2133mHz RAM
500GB Samsung SSD

"""

import os
from get_object_block_imgs import get_image_for_blocks
# Import debug module
from get_object_block_training_and_debug import extract_training_data, check_similarities_between_v1_v2
import sys

sys.path.insert(0, '/Users/rbennet8/Desktop/ADAP-BIG-V2/yolov5')
from yolov5.detect import run
from convert_txt_to_mz_rt import getinferencearrs, getinferencefilenames, convert
import params
import pickle
import gc
import cv2
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

from datetime import datetime

"""
Function used to output the time at each step, so I'm able to track the progress.
"""
def getTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

def main():
    print("Start Time =", getTime())

    if not os.path.isdir(r'../Blocks'):
        print('- - CREATING BLOCKS DIRECTORY - -', getTime())
        os.system('mkdir ../Blocks')
    # extract_training_data(params.profile_mzml_path, window_mz = 48, window_rt= 80) # NOT PART OF THE WORK FLOW // Used to debug and get object blocks to train model on

    print('- - GETTING IMAGES FOR BLOCKS - -', getTime())
    imgs = get_image_for_blocks(params.profile_mzml_path, window_mz=48, window_rt=80, timetoignoreL=2.5, timetoignoreR=19, min_intensity_threshold=1000)
    # pickle.dump(imgs, open(params.results_path + "/img_data.p", "wb"))
    # imgs = pickle.load(open(params.results_path + "/img_data.p", 'rb'))

    print('- - RUNNING YOLO - -', getTime())
    run(weights=params.weights_path, imgsz=(160, 96), conf_thres=0.2, source=params.source_path, save_txt=True, save_conf=True)

    print('- - GETTING INFERENCES - -', getTime())
    arrofpredictions = getinferencearrs()

    print('- - GETTING INFERENCE FILE NAMES - -', getTime())
    arroffilenames = getinferencefilenames()

    print('- - CONVERTING FOR EXPORT - -', getTime())
    dataframetoexport = convert(imgs[2], imgs[1], arroffilenames, arrofpredictions, params.window_mz, params.window_rt)

    print('- - WRITING CSV - -', getTime())
    dataframetoexport.to_csv(params.results_path + "/Final Predictions.csv")

    print("End Time =", getTime())


if __name__ == '__main__':
    main()
