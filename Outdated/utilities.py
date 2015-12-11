__author__ = 'Tissue'

import os
import json
import pickle
from sklearn import metrics
import numpy as np

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


def show_metrics(X, labels, labels_true):
    print "-"*15 + "METRICS" + "-"*15
    print "Numbers of cluster:", len(set(labels))
    print "Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels)
    print "Completeness: %0.3f" % metrics.completeness_score(labels_true, labels)
    print "V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels)
    print "Adjusted rand index: %0.3f" % metrics.adjusted_rand_score(labels_true, labels)
    print "Adjusted mutual information: %0.3f" % metrics.adjusted_mutual_info_score(labels_true, labels)
    print "Silhouette Coefficient: %0.3f" % metrics.silhouette_score(np.array(X), labels)
    print "-" * 37

def construct_point(x, y):
    point = dict()
    point["x"] = x
    point["y"] = y
    return point

def remove_duplicate(data):
    ret_list = list()
    ret_list.append(data[0])
    for i in range(1, len(data)):
        if data[i] == data[i-1]:
            pass
        else:
            ret_list.append(data[i])
    return ret_list

if __name__ == "__main__":
    # data = [1,1,1,1,2,3,4,1,4,4,4,5]
    # print remove_duplicate(data)
    with open('asdf.txt', 'a') as out_file:
        out_file.write('asdf\n')
        out_file.write('asdf\n')
    pass