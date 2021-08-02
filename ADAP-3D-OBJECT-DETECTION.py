import os
import math
import numpy as np
import multiprocessing as mp
import pickle
import time
from GET_OBJECT_IMGS import get_image_for_blocks
import pandas as pd
import logging


if __name__ == '__main__':
    if not os.path.isdir(r'.\Blocks'):
        os.system('mkdir .\Blocks')
    get_image_for_blocks(r"C:\Users\jerry\Desktop\DCSM_PROFILE.mzML", r"C:\Users\jerry\Desktop\Results", window_mz = 25, window_rt= 65)
    os.chdir("/yolov5")
    os.system("python detect.py --weights /best.pt --img 416 --conf 0.4 --source ../Blocks")

