__author__ = 'Fang'

import json
import os
import datetime
import utilities as util

INIT_DATA_DIR = "init_data"
NODE_DATA = "3p.json"
WAY_DATA = "3w.json"
INER_DATA_DIR = "Intermediate"
LOG_FILE = "Logs/Prepare_ways.log"

def get_nodes():
    os.chdir(INIT_DATA_DIR)
    with open(NODE_DATA) as data:
        nodes_data = json.load(data)
    os.chdir("..")
    nodes_list = nodes_data[u"elements"]
    nodes_dict = dict()
    for item in nodes_list:
        if item[u"type"] == u"node":
            tmp_id = item[u"id"]
            tmp_lat = item[u"lat"]
            tmp_lon = item[u"lon"]
            nodes_dict[tmp_id] = { u"lat" : tmp_lat , u"lon" : tmp_lon}
    return nodes_dict

def get_ways():
    os.chdir(INIT_DATA_DIR)
    with open(WAY_DATA) as data:
        ways_data = json.load(data)
    os.chdir("..")
    ways_list = ways_data[u"elements"]
    ways_dict = dict()
    for item in ways_list:
        if (item[u"type"] == u"way") and (u"tags" in item) and (u"highway" in item[u"tags"]):
            tmp_id = item[u"id"]
            nodes_list = list()
            for node_id in item[u"nodes"]:
                if nodes_dict.has_key(node_id):
                    tmp_node = nodes_dict[node_id]
                    tmp_lat = tmp_node[u"lat"]
                    tmp_lon = tmp_node[u"lon"]
                    nodes_list.append({ u"lat" : tmp_lat , u"lon" : tmp_lon})
            if len(nodes_list) > 1:
                ways_dict[tmp_id] = { u"highway" : item[u"tags"][u"highway"] , u"nodes" : nodes_list }
    return ways_dict


if __name__ == "__main__":

    s_time = datetime.datetime.now()
    nodes_dict = get_nodes()
    with open(LOG_FILE, 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "nodes_dict create cost %s\n" % str(cost_time)
        log_file.write(log)

    s_time = datetime.datetime.now()
    util.write_json("nodes_dict", INER_DATA_DIR, nodes_dict)
    with open(LOG_FILE, 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "nodes_dict.json save cost %s\n" % str(cost_time)
        log_file.write(log)

    s_time = datetime.datetime.now()
    ways_dict = get_ways()
    with open(LOG_FILE, 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "ways_dict create cost %s\n" % str(cost_time)
        log_file.write(log)

    s_time = datetime.datetime.now()
    util.write_json("ways_dict", INER_DATA_DIR, ways_dict)
    with open(LOG_FILE, 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "ways_dict.json save cost %s\n" % str(cost_time)
        log_file.write(log)
