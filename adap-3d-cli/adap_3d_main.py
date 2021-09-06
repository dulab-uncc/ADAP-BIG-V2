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

from convert_txt_to_mz_rt import getinferencearrs, getinferencefilenames, convert, savetestimg
import params
import pickle

def main():
    if not os.path.isdir(r'../mzml-img-blocks-new-test-5'):
        os.system('mkdir .\mzml-img-blocks-new-test-5')
    get_image_for_blocks2(params.profile_mzml_path, window_mz = 30, window_rt= 70, timetoignoreL = 2.5, timetoignoreR = 19)
    breakpoint()

    #if not os.path.isdir(r'../mzml-img-blocks-new-test-3'):
        #os.system('mkdir .\mzml-img-blocks-new-test-3')
    #imgs = get_image_for_blocks(params.profile_mzml_path, window_mz = 30, window_rt= 70, timetoignoreL = 2.5, timetoignoreR = 19)
    #pickle.dump(imgs, open(params.results_path + "\\saveADAP-Test-3.p", "wb"))
    #breakpoint()
    """
    Debug lines
    """

    imgs = pickle.load(open(params.results_path + "\\saveADAP.p", "rb"))
    # check_similarities_between_v1_v2()

    # Run yolov5 inference and save txt/img results in the runs folder of the yolov5 clone
    os.chdir(r"../ADAP-3D-V2/yolov5")
    os.system("python detect.py --weights " + params.weights_path + " --img 140 --conf 0.5 --source " + params.source_path + " --save-txt --save-conf")
    arrofpredictions = getinferencearrs()
    arroffilenames = getinferencefilenames()
    dataframetoexport = convert(imgs[0], imgs[1], arroffilenames, arrofpredictions, params.window_mz, params.window_rt)
    dataframetoexport.to_csv(params.results_path + "\ADAP-3D-Predictions.csv")

if __name__ == '__main__':
    main()

