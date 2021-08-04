import os
from GET_OBJECT_IMGS import get_image_for_blocks

if __name__ == '__main__':
    if not os.path.isdir(r'Blocks'):
        os.system('mkdir .\Blocks')
    #get_image_for_blocks(r"C:\Users\jerry\Desktop\DCSM_PROFILE.mzML", r"C:\Users\jerry\Desktop\Results", window_mz = 25, window_rt= 65)
    os.chdir(r"yolov5")
    os.system("python detect.py --weights C:\\Users\\jerry\\Desktop\\ADAP-3D-V2\\best.pt --img 416 --conf 0.4 --source C:\\Users\\jerry\\Desktop\\ADAP-3D-V2\\Blocks --save-txt")

