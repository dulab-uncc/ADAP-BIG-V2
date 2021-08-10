"""adap_3d_main module

-Calls module to block the mzml file into images
-Conducts yolov5 inference using the command line and saves the predictions to txt and image files

"""

import os
from get_object_block_imgs import get_image_for_blocks
from get_object_block_training_and_debug import get_image_for_blocks2
from convert_txt_to_mz_rt import getinferencearrs, getinferencefilenames, convert
import params
import pickle

def main():
    #os.chdir(r"../ADAP-3D-V2")
    #if not os.path.isdir(r'../mzml-img-blocks'):
        #os.system('mkdir .\mzml-img-blocks')
    #imgs = get_image_for_blocks(params.profile_mzml_path, window_mz = 25, window_rt= 65, timetoignoreL = 10, timetoignoreR = 12)
    #pickle.dump(imgs, open(params.results_path + "\\saveADAP.p", "wb"))
    #os.chdir(r"../ADAP-3D-V2/yolov5")
    #os.system("python detect.py --weights " + params.weights_path + " --img 640 --conf 0.4 --source " + params.source_path + " --save-txt --save-conf")
    imgs = pickle.load(open(params.results_path + "\\saveADAP.p", "rb"))
    arrofpredictions = getinferencearrs()
    arroffilenames = getinferencefilenames()
    dataframetoexport = convert(imgs[0], imgs[1], arroffilenames, arrofpredictions, params.window_mz, params.window_rt)
    dataframetoexport.to_csv(params.results_path + "\ADAP-3D-Predictions.csv")

if __name__ == '__main__':
    main()

