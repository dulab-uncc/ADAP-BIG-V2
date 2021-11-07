"""

mzml reader module

-extract time values for each scan
-extract mzarrs for each time
-extract intensity for each mz value in each mzarr for each time

"""

from base64 import b64decode as b64dec
from struct import unpack as unpack
import zlib
import xml.etree.cElementTree as et
from scipy.io import netcdf
import numpy as np


class netCDFReadHandler:
    """
    This class contains methods that handle mass spectra in netCDF format.
    """

    def __init__(self, data_file_str_w_path):
        self.data_file_full_name = data_file_str_w_path
        self.ncid = netcdf.netcdf_file(self.data_file_full_name, 'r')

        total_intensity_variable = self.ncid.variables['total_intensity']
        self.total_intensity = total_intensity_variable[:].copy()

        scan_acquisition_time_variable = self.ncid.variables['scan_acquisition_time']
        self.scan_acquisition_time = scan_acquisition_time_variable[:].copy()

        point_count_variable = self.ncid.variables['point_count']
        self.point_count = point_count_variable[:].copy()

        mass_values_variable = self.ncid.variables['mass_values']
        self.mass_values = mass_values_variable[:].copy()

        intensity_values_variable = self.ncid.variables['intensity_values']
        self.intensity_values = intensity_values_variable[:].copy()
        index_of_intensity_values_variable = self.ncid.variables['scan_index']
        self.index_of_intensity_values = index_of_intensity_values_variable[:].copy()

        self.total_number_of_scans = len(self.scan_acquisition_time)
        self.total_number_of_data_points = len(self.mass_values)
        # self.ncid.close()
        self.cur_index = 0

    def get_rt_from_scan_num(self, scan_num):
        return self.scan_acquisition_time[scan_num]

    def get_next_scan_mzvals_intensities(self):
        """ Returns the arrays of the mz values and the intensities (in that order) of the next
        scan. If this is the first time this function is called it just gets that information for
        the first scan."""
        mzandints = self.get_one_scan_by_scan_index(self.cur_index)
        self.cur_index += 1
        mzs = mzandints['mz']
        ints = mzandints['intensity']
        if len(mzs) == 0:
            return None, None
        return mzs, ints

    def get_file_name(self):
        return self.data_file_full_name

    def get_TIC(self):
        """
        This method extracts the TIC.

        Return a dictionary consisting of the scan_acquisition_time and the total_intensity.
        """

        tic = {}
        tic['scan_acquisition_time'] = self.scan_acquisition_time
        tic['total_intensity'] = self.total_intensity

        return tic

    def get_one_scan_by_scan_index(self, scan_index):
        """
        This method extracts one scan from the raw data.
        """

        if scan_index == 0:
            start_index = 0
            end_index = self.point_count[0]
        elif scan_index == 1:
            start_index = self.point_count[0]
            end_index = start_index + self.point_count[1]
        else:
            start_index = np.sum(self.point_count[0:scan_index])
            end_index = start_index + self.point_count[scan_index]
        if (start_index > len(self.mass_values) - 1) or (end_index > len(self.mass_values) - 1):
            scan = {}
            scan['mz'] = []
            scan['intensity'] = []
            return scan

        scan = {}
        scan['mz'] = self.mass_values[start_index:end_index]
        scan['intensity'] = self.intensity_values[start_index:end_index]

        return scan

    def get_act_scan_num(self, scan_number):
        """
        In CDF files the scans are just incrementally numbered so this is just a trick
        so you can call this function correctly from inside easyio.py regardless of
        the file type

        :param scan_number: integer referring to the index
        :return: scan_number
        """
        return scan_number


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


