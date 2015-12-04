# -*- coding:utf-8 -*-
__author__ = 'Neo'

import os
import glob
import pickle
import unicodecsv
import datetime
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

DATA_DIR = "Raw"
TEMP_DIR = "Intermediate"
DEFAULT_FILTER = {"min_lon": 70, "min_lat": 10, "max_lon": 135, "max_lat": 55}
CSV_FILE = "location_address.csv"

def convert(input_file, output_file):
    with open(input_file) as in_file:
        lines = in_file.readlines()
        with open(output_file,'w+') as out_file:
            for line in lines:
                out_file.writelines((line.decode('gb2312')).encode('utf_8'))

def convert_all(data_dir = DATA_DIR):
    os.chdir(data_dir)
    for file in glob.glob("*.csv"):
        output_name = 'utf' + file
        convert(file, output_name)
    os.chdir("..")

def find_abnormal_data(data_dir = DATA_DIR, filter = DEFAULT_FILTER):
    s_time = datetime.datetime.now()
    abnormal_list = list()
    os.chdir(data_dir)
    t_min_lon = filter["min_lon"]
    t_min_lat = filter["min_lat"]
    t_max_lon = filter["max_lon"]
    t_max_lat = filter["max_lat"]
    for csv_file in glob.glob("utf*.csv"):
        with open(csv_file) as csvFile:
            name = csv_file.split(".")[0]
            reader = unicodecsv.reader(csvFile, encoding="utf_8")
            for row in reader:
                lon = float(row[2])
                lat = float(row[3])
                if t_min_lon <= lon <= t_max_lon and t_min_lat <= lat <= t_max_lat:
                    pass
                else:
                    abnormal_list.append(name)
                    print "Abnormal found"
                    break
    os.chdir("..")
    e_time = datetime.datetime.now()
    print "find_abnormal time:", e_time - s_time
    return abnormal_list

def get_all_geo_ranges(data_dir = DATA_DIR):
    s_time = datetime.datetime.now()
    os.chdir(data_dir)
    ranges_list = list()
    for file in glob.glob("utf*.csv"):
        file_name = file.split(".")[0][2:]
        with open(file) as csvFile:
            lat_list = list()
            lon_list = list()
            reader = unicodecsv.reader(csvFile, encoding='utf-8')
            for row in reader:
                lon_list.append(float(row[2]))
                lat_list.append(float(row[3]))
            min_lon, max_lon = np.min(lon_list), np.max(lon_list)
            min_lat, max_lat = np.min(lat_list), np.max(lat_list)
            ranges_list.append([file_name, min_lon, min_lat, max_lon, max_lat])
    os.chdir("..")
    e_time = datetime.datetime.now()
    print "get_all_ranges time:", e_time - s_time
    return ranges_list

def write_data_pickle(file_name, data, write_dir = TEMP_DIR):
    if not os.path.exists(write_dir):
        os.mkdir(write_dir)
    os.chdir(write_dir)
    with open(file_name, "wb") as outFile:
        pickle.dump(data, outFile, -1)
    os.chdir("..")

def read_data_pickle(file_name, read_dir = TEMP_DIR):
    os.chdir(read_dir)
    with open(file_name, "rb") as inFile:
        data = pickle.load(inFile)
    os.chdir("..")
    return data

def read_csv(file_name, read_dir = DATA_DIR):
    os.chdir(DATA_DIR)
    with open(file_name) as csvFile:
        reader = unicodecsv.reader(csvFile, encoding="gb2312")
        i = 0
        for row in reader:
            print row[0]
            print row[1]
            print row[2]
            i += 1
            if i >= 10:
                break
    os.chdir("..")

if __name__ == "__main__":
    # convert_all()
    # find_abnormal_data()
    # write_data_pickle("all_ranges.txt", get_all_geo_ranges())
    # read_csv(CSV_FILE)
    os.chdir(DATA_DIR)
    convert("location_address.csv", "la.csv")
    os.chdir("..")
    pass