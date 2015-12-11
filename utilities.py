# -*- coding:utf-8 -*-
__author__ = 'Neo'

import os
import json
import pickle

DATA_DIR = "Raw"
TEMP_DIR = "Intermediate"
SAMPLE_DATA = "utfB61962.csv"

def read_json(file_name):
    os.chdir(TEMP_DIR)
    with open(file_name) as inFile:
        ret_dict = json.load(inFile)
    os.chdir('..')
    return ret_dict

def write_json(file_name, data_dict):
    os.chdir(TEMP_DIR)
    with open(file_name, "wb") as outFile:
        json.dump(data_dict, outFile, indent=4)
    os.chdir('..')


def read_pickle(file_name):
    os.chdir(TEMP_DIR)
    with open(file_name) as inFile:
        ret_pick = pickle.load(inFile)
    os.chdir('..')
    return ret_pick

def write_pickle(file_name, data):
    os.chdir(TEMP_DIR)
    with open(file_name, "wb") as outFile:
        pickle.dump(data, outFile)
    os.chdir(TEMP_DIR)