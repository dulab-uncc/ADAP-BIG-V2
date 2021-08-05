import os
from .get_object_block_imgs import get_image_for_blocks
from .params import *
def main():
    if not os.path.isdir(r'../mzml-img-blocks'):
        os.system('mkdir .\Blocks')
    get_image_for_blocks(profile_mzml_path, results_path, window_mz = 25, window_rt= 65,timetoignoreL = 2, timetoignoreR = 20)
    os.chdir(r"../yolov5")
    os.system("python detect.py --weights C:\\Users\\jerry\\Desktop\\ADAP-3D-V2\\adap-3d-cli\\best.pt --img 416 --conf 0.4 --source C:\\Users\\jerry\\Desktop\\ADAP-3D-V2\\mzml-img-blocks --save-txt")

if __name__ == '__main__':
    main()

