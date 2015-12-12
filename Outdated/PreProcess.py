__author__ = 'Fang'

import os
import math
import json
import datetime
import utilities as util

INIT_DATA_DIR = "Raw"
RAW_NODE_DATA = "3n.json"
RAW_WAY_DATA = "3w.json"
INER_DATA_DIR = "Intermediate"
GEO_RANGE = '116.318,27.147,122.481,35.178'
LOG_FILE = "Logs/PreProcess.log"
WAY_DATA = "ways_dict"
STEP = 0.02

class PreProcess:
    __step = 0.02
    __nodes_dict = {}

    def __init__(self):

        s_time = datetime.datetime.now()
        self.__nodes_dict = self.get_nodes()
        with open(LOG_FILE, 'a') as log_file:
            e_time = datetime.datetime.now()
            cost_time = e_time - s_time
            log = "nodes_dict create cost %s\n" % str(cost_time)
            log_file.write(log)

        s_time = datetime.datetime.now()
        util.write_json("nodes_dict", INER_DATA_DIR, self.__nodes_dict)
        with open(LOG_FILE, 'a') as log_file:
            e_time = datetime.datetime.now()
            cost_time = e_time - s_time
            log = "nodes_dict.json save cost %s\n" % str(cost_time)
            log_file.write(log)

        s_time = datetime.datetime.now()
        ways_dict = self.get_ways()
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


    def __get_nodes(self):
        os.chdir(INER_DATA_DIR)
        if not os.path.exists(RAW_NODE_DATA):
            util.download_map(GEO_RANGE, True)
        with open(RAW_NODE_DATA) as data:
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

    def __get_ways(self):
        os.chdir(INIT_DATA_DIR)
        if not os.path.exists(RAW_WAY_DATA):
            util.download_map(GEO_RANGE, False)
        with open(RAW_WAY_DATA) as data:
            ways_data = json.load(data)
        os.chdir("..")
        ways_list = ways_data[u"elements"]
        ways_dict = dict()
        for item in ways_list:
            if (item[u"type"] == u"way") and (u"tags" in item) and (u"highway" in item[u"tags"]):
                tmp_id = item[u"id"]
                nodes_list = list()
                for node_id in item[u"nodes"]:
                    if self.__nodes_dict.has_key(node_id):
                        tmp_node = self.__nodes_dict[node_id]
                        tmp_lat = tmp_node[u"lat"]
                        tmp_lon = tmp_node[u"lon"]
                        nodes_list.append({ u"lat" : tmp_lat , u"lon" : tmp_lon})
                if len(nodes_list) > 1:
                    ways_dict[tmp_id] = { u"highway" : item[u"tags"][u"highway"] , u"nodes" : nodes_list }
        return ways_dict

    def get_geo_range():
        min_lat = min_lon = 1000000
        max_lat = max_lon = -1000000
        for item in ways_dirt.values():
            for node in item[u"nodes"]:
                tmp_lat = float(node[u"lat"])
                tmp_lon = float(node[u"lon"])
                min_lat = min(min_lat, tmp_lat)
                min_lon = min(min_lon, tmp_lon)
                max_lat = max(max_lat, tmp_lat)
                max_lon = max(max_lon, tmp_lon)
        return min_lat, max_lat, min_lon, max_lon

    def find_grid_id(x, y):
        loc_x = int((x - min_lat) / STEP)
        if loc_x == num_lat:
            loc_x -= 1
        loc_y = int((y - min_lon) / STEP)
        if loc_y == num_lon:
            loc_y -= 1
        loc = loc_x * num_lon + loc_y
        return loc

    def gen_segment(seg_id, sx, sy, ex, ey, highway):
        return { seg_id : { u"highway" : highway , u"snode" : (sx, sy) , u"enode" : (ex, ey) } }

    def get_grids():
        grids_dict = dict()
        for i in range(num_grids):
            grids_dict[i] = list()
        for (way_id, item) in ways_dirt.items():
            nodes = item[u"nodes"]
            length = len(nodes)
            highway = item[u"highway"]
            last_lat = float(nodes[0][u"lat"])
            last_lon = float(nodes[0][u"lon"])
            last_loc = find_grid_id(last_lat, last_lon)
            for i in range(1,length):
                tmp_lat = float(nodes[i][u"lat"])
                tmp_lon = float(nodes[i][u"lon"])
                tmp_loc = find_grid_id(tmp_lat, tmp_lon)
                grids_dict[last_loc].append(gen_segment(unicode(last_lon) + u"_" + unicode(way_id) + u"_" + unicode(i - 1), last_lat, last_lon, tmp_lat, tmp_lon, highway))
                if(tmp_loc != last_loc):
                    grids_dict[tmp_loc].append(gen_segment(unicode(tmp_loc) + u"_" + unicode(way_id) + u"_" + unicode(i - 1), last_lat, last_lon, tmp_lat, tmp_lon, highway))
                last_lat = tmp_lat
                last_lon = tmp_lon
                last_loc = tmp_loc
        return grids_dict