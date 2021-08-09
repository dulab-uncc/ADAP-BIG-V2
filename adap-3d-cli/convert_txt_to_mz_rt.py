""" conversion module

-convert mzml inference boxes into specific m/z and rt values

"""
from os import listdir
from os.path import isfile, join
import params
from numpy import loadtxt
from collections import OrderedDict
from pathlib import Path

def getinferencearrs():
    onlyfiles = listdir(params.txt_inference_path)
    arr_of_inferences = []
    for file in onlyfiles:
        with open(params.txt_inference_path + "\\" + file) as my_file:
            txt = my_file.read().splitlines()
            splitarr = []
            for arr in txt:
                splitarr.append(arr.split())
            arr_of_inferences.append(splitarr)
    return arr_of_inferences

def getinferencefilenames():
   templist =  listdir(params.txt_inference_path)
   final_list = []
   for txtfile in templist:
       idxofdot = 0
       for i in range(len(txtfile)):
           if(txtfile[i]=="."):
               idxofdot = i
       final_list.append(txtfile[9:idxofdot])
   return final_list

def convert(mz_rt_img_arr):
    pass