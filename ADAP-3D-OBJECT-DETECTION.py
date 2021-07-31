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
    get_image_for_blocks(r"C:\Users\jerry\Desktop\DCSM_PROFILE.mzML", r"C:\Users\jerry\Desktop\Results", window_mz = 25, window_rt= 65)


