# -*- coding:utf-8 -*-
__author__ = 'Neo'

import os
import json
import glob
import pickle

DATA_DIR = "Raw"
TEMP_DIR = "Intermediate"
SAMPLE_DATA = "utfB61962.csv"
LOG_FOLDER = '/Users/Neo/Documents/Worksapce/DSM/Trajectory/Logs/'

def read_json(file_name, dir_name):
    os.chdir(dir_name)
    with open(file_name) as inFile:
        ret_dict = json.load(inFile)
    os.chdir('..')
    return ret_dict

def write_json(file_name, dir_name, data_dict):
    os.chdir(dir_name)
    with open(file_name, "wb") as outFile:
        json.dump(data_dict, outFile, indent=4)
    os.chdir('..')

def read_pickle(file_name, dir_name):
    os.chdir(dir_name)
    with open(file_name) as inFile:
        ret_pick = pickle.load(inFile)
    os.chdir('..')
    return ret_pick

def write_pickle(file_name, dir_name, data):
    os.chdir(dir_name)
    with open(file_name, "wb") as outFile:
        pickle.dump(data, outFile)
    os.chdir('..')

def download_map(geo_range, download_nodes):
    command = 'wget -o ../Logs/download.log -O '
    if download_nodes:
        command += '3n.json'
    else :
        command += '3w.json'
    command += ' "http://overpass-api.de/api/interpreter?data=[out:json];node(bbox);out;&bbox=' + geo_range + '"'
    print command
    os.system(command)

def write_log(log_file_name, log_info):
    os.chdir('Logs')
    log = open(log_file_name, 'a')
    log.write(log_info)
    os.chdir('..')

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