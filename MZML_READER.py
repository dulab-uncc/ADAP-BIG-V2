import numpy as np
import sys
import codecs
from base64 import b64decode as b64dec
from struct import unpack as unpack
import zlib
import bisect as bs
import xml.etree.cElementTree as et
import scipy.signal as signal
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import logging

def extract_timevals(inputfile):
    fn1 = inputfile
    scan_time = []
    #spec_m = []

    spec_idx = 0
    for event, elem in et.iterparse(fn1, ("start", "end")):

        if (elem.tag.endswith('cvParam') and elem.attrib['name'] == 'time array'): break

        if (elem.tag.endswith('cvParam') and elem.attrib['name'] == 'scan start time' and event == 'end'):
            scan_time.append(float(elem.attrib['value']))

        if (elem.tag.endswith("spectrum") or elem.tag.endswith("chromatogram")):
            spec_len = elem.attrib['defaultArrayLength']
            spec_idx = int(elem.attrib['index'])
            # print (spec_idx, spec_len)    ##@@ To be deleted...@@##

        elif (spec_idx == 0 and elem.tag.endswith('cvParam')):
            if (elem.attrib['name'] == '64-bit float'):
                spec_type = 'd'
            elif (elem.attrib['name'] == '32-bit float'):
                spec_type = 'f'
            elif (elem.attrib['name'] == 'zlib compression'):
                spec_comp = 'zlib'
            elif (elem.attrib['name'] == 'm/z array'):
                spec_name = 'mz'
            elif (elem.attrib['name'] == 'intensity array'):
                spec_name = 'i'
            elif (elem.attrib['name'] == 'time array'):
                spec_name = 't'

    scan_num = spec_idx + 1

    return scan_time


def extract_intensities(inputfile, left_bound, right_bound):
    fn1 = inputfile
    spec_i = []
    spec_idx = 0

    for event, elem in et.iterparse(fn1, ("start", "end")):

        if (elem.tag.endswith('cvParam') and elem.attrib['name'] == 'time array'): break
        #
        #        if(elem.tag.endswith('cvParam') and elem.attrib['name']=='scan start time' and event=='end'):
        #            scan_time.append(elem.attrib['value'])

        if (elem.tag.endswith("spectrum") or elem.tag.endswith("chromatogram")):
            spec_len = elem.attrib['defaultArrayLength']
            spec_idx = int(elem.attrib['index'])
            # print (spec_idx)

            # if left_bound > spec_idx : continue     ##@@ any problem?? @@##
            if spec_idx >= right_bound: break

        elif (elem.tag.endswith('cvParam') and spec_idx >= left_bound):
            if (elem.attrib['name'] == '64-bit float'):
                spec_type = 'd'
            elif (elem.attrib['name'] == '32-bit float'):
                spec_type = 'f'
            elif (elem.attrib['name'] == 'zlib compression'):
                spec_comp = 'zlib'
            elif (elem.attrib['name'] == 'm/z array'):
                spec_name = 'mz'
            elif (elem.attrib['name'] == 'intensity array'):
                spec_name = 'i'
            elif (elem.attrib['name'] == 'time array'):
                spec_name = 't'
        elif (elem.tag.endswith("binary") and event == 'end' and spec_idx >= left_bound and spec_name == 'i'):
            #logging.debug("event: {}, spec_idx: {}, spec_len: {}, spec_type: {}, spec_comp: {}, spec_name: {}".format(event, spec_idx, spec_len, spec_type, spec_comp, spec_name))
            unpackedData = []
            base64Data = elem.text.encode("utf-8")
            decodedData = b64dec(base64Data)
            decodedData = zlib.decompress(decodedData)
            fmt = "{endian}{arraylength}{floattype}".format(endian="<", arraylength=spec_len, floattype=spec_type)

            unpackedData = unpack(fmt, decodedData)
            spec_i.append(list(unpackedData))

    return spec_i

def extract_mzvals(inputfile, left_bound, right_bound):
    fn1 = inputfile
    spec_m = []
    spec_idx = 0

    for event, elem in et.iterparse(fn1, ("start", "end")):

        if (elem.tag.endswith('cvParam') and elem.attrib['name'] == 'time array'): break
        #
        #        if(elem.tag.endswith('cvParam') and elem.attrib['name']=='scan start time' and event=='end'):
        #            scan_time.append(elem.attrib['value'])

        if (elem.tag.endswith("spectrum") or elem.tag.endswith("chromatogram")):
            spec_len = elem.attrib['defaultArrayLength']
            spec_idx = int(elem.attrib['index'])
            # print (spec_idx)

            # if left_bound > spec_idx : continue     ##@@ any problem?? @@##
            if spec_idx >= right_bound: break

        elif (elem.tag.endswith('cvParam') and spec_idx >= left_bound):
            if (elem.attrib['name'] == '64-bit float'):
                spec_type = 'd'
            elif (elem.attrib['name'] == '32-bit float'):
                spec_type = 'f'
            elif (elem.attrib['name'] == 'zlib compression'):
                spec_comp = 'zlib'
            elif (elem.attrib['name'] == 'm/z array'):
                spec_name = 'mz'
            elif (elem.attrib['name'] == 'intensity array'):
                spec_name = 'i'
            elif (elem.attrib['name'] == 'time array'):
                spec_name = 't'
        elif (elem.tag.endswith("binary") and event == 'end' and spec_idx >= left_bound and spec_name == 'mz'):
            #logging.debug("event: {}, spec_idx: {}, spec_len: {}, spec_type: {}, spec_comp: {}, spec_name: {}".format(event, spec_idx, spec_len, spec_type, spec_comp, spec_name))
            unpackedData = []
            base64Data = elem.text.encode("utf-8")
            decodedData = b64dec(base64Data)
            decodedData = zlib.decompress(decodedData)
            fmt = "{endian}{arraylength}{floattype}".format(endian="<", arraylength=spec_len, floattype=spec_type)

            unpackedData = unpack(fmt, decodedData)
            spec_m.append(list(unpackedData))

    return spec_m


