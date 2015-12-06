# -*- coding:utf-8 -*-
__author__ = 'Neo'

# Just testing

import os
import pickle
import datetime
from utilities import write_json, read_json
from collections import defaultdict

DATA_DIR = "Raw"
TEMP_DIR = "Intermediate"
# SAMPLE_DATA = "utfB61962.csv"
SAMPLE_DATA = "la.csv"

def get_name_of_map(file_name):
    # return 'map_of_' + file_name.split('.')[0][3:] + '.txt'
    return 'map_of_' + file_name.split('.')[0] + '.txt'

def get_raw_data(file_name):
    os.chdir(TEMP_DIR)
    with open(get_name_of_map(file_name)) as inFile:
        data = pickle.load(inFile)
    os.chdir('..')
    return data

def get_tags_list(raw_data):
    ret_list = list()
    for item in raw_data:
        if unicode("tags") in item:
            temp_dict = item[unicode("tags")]
            if unicode("highway") in temp_dict.keys():
                ret_list.append(item)
    return ret_list

def get_whole_nodes(raw_data):
    ret_nodes = dict()
    for item in raw_data:
        ele_type = item[unicode("type")]
        if ele_type == "node":
            node_id = item[unicode("id")]
            lat = item[unicode("lat")]
            lon = item[unicode("lon")]
            ret_nodes[node_id] = {"lat": lat, "lon": lon}
    return ret_nodes

def get_a_node(node_id, whole_nodes):
    if node_id in whole_nodes.keys():
        lat = whole_nodes[node_id]["lat"]
        lon = whole_nodes[node_id]["lon"]
        ret_a_node = [node_id, lat, lon]
    else:
        ret_a_node = None
    return ret_a_node

def get_whole_ways(tags_list, whole_nodes):
    ret_dict = dict()
    j = 0
    s_time = datetime.datetime.now()
    with open('whole_ways.log', 'a') as log_file:
        log_file.flush()
    for item in tags_list:
        ele_type = item[unicode("type")]
        if ele_type == "way":
            way_id = item[unicode("id")]
            j += 1
            if j % 100 == 0:
                with open('whole_ways.log', 'a') as log_file:
                    e_time = datetime.datetime.now()
                    cost_time = e_time - s_time
                    log = 'The ' + str(j) + 'th way is ' + str(way_id) + " at " + str(cost_time) + '\n'
                    log_file.write(log)
            nodes_id = item[unicode("nodes")]
            nodes_info = list()
            for node_id in nodes_id:
                temp_node = get_a_node(node_id=node_id, whole_nodes=whole_nodes)
                if temp_node != None:
                    nodes_info.append(temp_node)
            ret_dict[way_id] = {"nodes_info": nodes_info}
    return ret_dict

# Get intersections
def get_node_count(whole_ways):
    nodes_freq = defaultdict(int)
    for way_id in whole_ways:
        nodes_info = whole_ways[way_id]["nodes_info"]
        for node in nodes_info:
            node_id = node[0]
            nodes_freq[node_id] += 1
    return nodes_freq


def get_intersection_point_modify(nodes_freq, whole_nodes):
    intersect_points = list()
    for node_id in nodes_freq.keys():
        if nodes_freq[node_id] >= 2:
            temp_node = get_a_node(node_id, whole_nodes)
            if temp_node != None:
                intersect_points.append(temp_node)
    return intersect_points


def slice_way_normal(way_id, nodes_list, slice_indexes, whole_ways_slices):
    slice_num = len(slice_indexes)
    for i in range(slice_num-1):
        slice_name = str(way_id) + "_" + str(i)
        temp_dict = dict()
        s_id = nodes_list[slice_indexes[i]]
        e_id = nodes_list[slice_indexes[i+1]]
        temp_dict["s_inter"] = s_id
        temp_dict["e_inter"] = e_id
        temp_dict["data"] = nodes_list[slice_indexes[i]: slice_indexes[i+1]+1]
        whole_ways_slices[slice_name] = temp_dict


def construct_slice(way_id, s_id, e_id, data, whole_ways_slices, postfix=0):
    slice_name = str(way_id) + "_" + str(postfix)
    temp_dict = dict()
    temp_dict["s_inter"] = s_id
    temp_dict["e_inter"] = e_id
    temp_dict["data"] = data
    whole_ways_slices[slice_name] = temp_dict


def slice_way_one(way_id, nodes_list, slice_indexes, whole_ways_slices):
    # check lacking inter point position
    inter_pos = slice_indexes[0]
    if inter_pos == len(nodes_list)-1:
        fake_inter_pos = 0
        s_id = nodes_list[fake_inter_pos]
        e_id = nodes_list[inter_pos]
        data = nodes_list[fake_inter_pos: inter_pos+1]
        construct_slice(way_id, s_id, e_id, data, whole_ways_slices)
    elif inter_pos == 0:
        fake_inter_pos = len(nodes_list)-1
        s_id = nodes_list[inter_pos]
        e_id = nodes_list[fake_inter_pos]
        data = nodes_list[inter_pos: fake_inter_pos+1]
        construct_slice(way_id, s_id, e_id, data, whole_ways_slices)
    else:
        #print "Error! way_id:", way_id, ",pos:", inter_pos
        mid = nodes_list[inter_pos]
        s_id = nodes_list[0]
        e_id = nodes_list[len(nodes_list)-1]
        construct_slice(way_id, s_id, mid, nodes_list[0: inter_pos+1], whole_ways_slices)
        construct_slice(way_id, mid, e_id, nodes_list[inter_pos: len(nodes_list)], whole_ways_slices, postfix=1)

def get_ways_slices_modify(whole_ways, intersect_points):
    whole_ways_slices = dict()
    inter_nodes_id = [point[0] for point in intersect_points]
    for way_id in whole_ways.keys():
        nodes_info = whole_ways[way_id]["nodes_info"]
        nodes_list = [node[0] for node in nodes_info]
        # find and count inter points
        inter_list = list()
        for i, item in enumerate(nodes_list):
            if item in inter_nodes_id:
                inter_list.append(i)
        if len(inter_list) > 1:
            slice_way_normal(way_id, nodes_list, inter_list, whole_ways_slices)
        elif len(inter_list) == 1:
            slice_way_one(way_id, nodes_list, inter_list, whole_ways_slices)
    return whole_ways_slices


if __name__ == "__main__":
    raw_data = get_raw_data(SAMPLE_DATA)
    # whole_nodes = get_whole_nodes(raw_data = raw_data)

    s_time = datetime.datetime.now()
    whole_nodes = read_json("whole_nodes.txt")
    with open('test.log', 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = 'Reading nodes finished at ' + str(cost_time) + '\n'
        log_file.write(log)

    # print "whole nodes:", len(whole_nodes.keys())
    # print "after 1"
    # write_json("whole_nodes.txt", whole_nodes)
    # print "write 1"

    # tags_list = get_tags_list(raw_data = raw_data)
    print "after 2"

    whole_ways = read_json("whole_ways.txt")

    # whole_ways = get_whole_ways(tags_list=tags_list, whole_nodes=whole_nodes)
    print "after 3"
    # write_json("whole_ways.txt", whole_ways)
    print "write 3"

    s_time = datetime.datetime.now()
    nodes_freq = get_node_count(whole_ways)
    with open('test.log', 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = 'Counting nodes finished at ' + str(cost_time) + '\n'
        log_file.write(log)

    print "after 4"

    s_time = datetime.datetime.now()
    new_inter_points = get_intersection_point_modify(nodes_freq, whole_nodes=whole_nodes)
    with open('test.log', 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = 'Finding inter points finished at ' + str(cost_time) + '\n'
        log_file.write(log)

    print "after 5"

    s_time = datetime.datetime.now()
    write_json("new_whole_inter.txt", new_inter_points)
    with open('test.log', 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = 'Writing inter nodes finished at ' + str(cost_time) + '\n'
        log_file.write(log)
    print "write 5"

    s_time = datetime.datetime.now()
    new_whole_slices = get_ways_slices_modify(whole_ways, intersect_points=new_inter_points)
    with open('test.log', 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = 'Finding way slices finished at ' + str(cost_time) + '\n'
        log_file.write(log)
    print "after 6"

    s_time = datetime.datetime.now()
    write_json("modify_whole_slices.txt", new_whole_slices)
    with open('test.log', 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = 'Writing way slices finished at ' + str(cost_time) + '\n'
        log_file.write(log)
    print "write 6"