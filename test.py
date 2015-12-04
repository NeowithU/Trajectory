# -*- coding:utf-8 -*-
__author__ = 'Neo'

import os
import sys
import unicodecsv
import overpass
import pickle
import datetime
import matplotlib.pyplot as plt
import numpy as np
from utilities import read_json, write_json, write_pickle
from road_map import get_name_of_map

DATA_DIR =  "Raw"
TEMP_DIR = "Intermediate"
SAMPLE_DATA = "la.csv"

def read_geo_from_file(file_name = SAMPLE_DATA):
    lon_list = list()
    lat_list = list()
    os.chdir(DATA_DIR)
    with open(file_name) as csvFile:
        reader = unicodecsv.reader(csvFile, encoding="utf-8")
        for row in reader:
            lon_list.append(float(row[0]))
            lat_list.append(float(row[1]))
    os.chdir("..")
    return lon_list, lat_list

def gps_scatter(lon_list, lat_list):
    plt.scatter(lon_list, lat_list, s=1, c="red", alpha=0.05)
    plt.show()

def get_geo_range(lon_list, lat_list):
    ret_dict = dict()
    ret_dict["lat_min"] = np.min(lat_list)
    ret_dict["lat_max"] = np.max(lat_list)
    ret_dict["lon_min"] = np.min(lon_list)
    ret_dict["lon_max"] = np.max(lon_list)
    return ret_dict

def get_osm_map(geo_range):
    # Uncomment the below three lines and comment the next line to download the needed map
    # api = overpass.API(timeout=3600, responseformat="json", debug=True)
    # map_query = overpass.MapQuery('data=[out:json];(node(bbox);rel(bbox);way(bbox););&bbox=121.541368,31.1297119,121.64748,31.169746')
    # map_query = overpass.MapQuery(geo_range["lat_min"], geo_range["lon_min"], geo_range["lat_max"], geo_range["lon_max"])
    # way_query = overpass.WayQuery((31.1297119,121.541368,31.169746,121.64748))
    # response = api.Get(way_query)
    # response = api.Get("/api/interpreter?data=[out:json];(node(bbox);rel(bbox);way(bbox););(._;>;);out;&bbox=121.541368,31.1297119,121.64748,31.169746")
    # response = read_json(SAMPLE_DATA.split('.')[0][3:] + '.json')
    response = read_json('la.json')
    # write_json("bbb.json", response)
    way_data = response[unicode("elements")]
    # write_json(get_name_of_map(SAMPLE_DATA), way_data)
    write_pickle(get_name_of_map(SAMPLE_DATA), way_data)

if __name__ == "__main__":
    lon_list, lat_list = read_geo_from_file()
    # gps_scatter(lon_list, lat_list)
    geo_range = get_geo_range(lon_list, lat_list)
    # print geo_range
    get_osm_map(geo_range)