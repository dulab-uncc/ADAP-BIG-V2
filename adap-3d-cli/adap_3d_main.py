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

#Import debug module, comment out for final production
from get_object_block_training_and_debug import get_image_for_blocks2, check_similarities_between_v1_v2
import sys
sys.path.append(r"../ADAP-3D-V2/yolov5")
from detect import run
from convert_txt_to_mz_rt import getinferencearrs, getinferencefilenames, convert, savetestimg
import params
import pickle
import gc
import cv2
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

def main():
    if not os.path.isdir(r'../mzml-VT001'):
      os.system('mkdir .\mzml-VT001')
    get_image_for_blocks2(params.profile_mzml_path, window_mz = 48, window_rt= 80, timetoignoreL = 2.5, timetoignoreR = 19)
    breakpoint()


    #if not os.path.isdir(r'../CORRECT-BLOCKS-4'):
        #os.system('mkdir .\CORRECT-BLOCKS-4')
    imgs = get_image_for_blocks(params.profile_mzml_path, window_mz = 48, window_rt= 80, timetoignoreL = 2.5, timetoignoreR = 19)
    #breakpoint()
    pickle.dump(imgs, open(params.results_path + "\\ADAP-3D-MZ-INTENSITY-DATA-V2.p", "wb"))
    breakpoint()
    """
    Debug lines
    """
    #check_similarities_between_v1_v2()
    #breakpoint()

    # disable garbage collector
    #gc.disable()

    #imgs = pickle.load(open(params.results_path + "\\ADAP-3D-MZ-INTENSITY-DATA-V2-BINARY.p", 'rb'))

    # enable garbage collector again
    #gc.enable()
    #output.close()
    testvar1 = pickle.load(open(params.results_path + "\\testvar1.p", 'rb'))
    testvar2 = pickle.load(open(params.results_path + "\\testvar2.p", 'rb'))
    #pickle.dump(testvar, open(params.results_path + "\\testvar1.p", "wb"))
    #pickle.dump(testvar2, open(params.results_path + "\\testvar2.p", "wb"))


    rgb = pickle.load(open(r"C:\Users\jerry\Desktop\Results\rgb.p", "rb"))
    testing = rgb[0]
    newimgarr = []


    #for i in range(len(testvar1)):
     #for j in range(len(testvar1[0])):
      #if(testvar1[i][j] > 0):
       #testvar1[i][j] = np.log10(testvar1[i][j])

    maxval = np.amax(testvar1)
    minval = np.amin(testvar1)

    temparr = []
    for i in range(len(testvar1)):
     temp = []
     for j in range(len(testvar1[0])):
      temp.append(((maxval - testvar1[i][j]) / (maxval-minval))  * 255)
     temparr.append(temp)
    temparr = np.asarray(temparr)
    temparr = [[1, np.asarray([temparr, temparr, temparr])]]



    """
    plt.imshow(testing, cmap="Greys", aspect='auto', interpolation=None)
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.savefig(r'.\CORRECT-BLOCKS-4\ ' + "TEST.png")
    plt.close('all')
    """
    #breakpoint()


    #node_color = [(r, g, b) for r, g, b, a in mapper.to_rgba(data, bytes=True)]

    # Run yolov5 inference and save txt/img results in the runs folder of the yolov5 clone
    #os.chdir(r"../ADAP-3D-V2/yolov5")
    #os.system("python detect.py --weights " + params.weights_path + " --img 700 --conf 0.63 --source " + params.source_path + " --save-txt --save-conf")
    run(weights = params.weights_path, imgsz = 160, conf_thres =  0.63, save_txt = True,  save_conf = True, npimgs = temparr)

    breakpoint()


    run(weights=params.weights_path, imgsz=160, conf_thres=0.63, save_txt=True, save_conf=True, npimgs=imgs)
    arrofpredictions = getinferencearrs()
    arroffilenames = getinferencefilenames()
    dataframetoexport = convert(imgs[0], imgs[1], arroffilenames, arrofpredictions, params.window_mz, params.window_rt)
    dataframetoexport.to_csv(params.results_path + "\ADAP-3D-Predictions-run22.csv")

if __name__ == '__main__':
    main()

