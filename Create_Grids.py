__author__ = 'Fang'

import datetime
import utilities as util
import math

WAY_DATA = "ways_dict"
INER_DATA_DIR = "Intermediate"
LOG_FILE = "Logs/Create_gids.log"
STEP = 0.02

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

if __name__ == "__main__":

    s_time = datetime.datetime.now()
    ways_dirt = util.read_json(WAY_DATA, INER_DATA_DIR)
    with open(LOG_FILE, 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "load ways cost %s\n" % str(cost_time)
        log_file.write(log)

    s_time = datetime.datetime.now()
    min_lat, max_lat, min_lon, max_lon = get_geo_range()
    num_lat = int(math.ceil((max_lat - min_lat) / STEP) + 0.1)
    num_lon = int(math.ceil((max_lon - min_lon) / STEP) + 0.1)
    num_grids = num_lat * num_lon
    with open(LOG_FILE, 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "calculate range is (%s , %s),(%s , %s)\n" % (str(min_lat), str(min_lon), str(max_lat), str(max_lon))
        log_file.write(log)
        log = "num of lat is %s\n" % str(num_lat)
        log_file.write(log)
        log = "num of lon is %s\n" % str(num_lon)
        log_file.write(log)

    s_time = datetime.datetime.now()
    grids_dict = get_grids()
    with open(LOG_FILE, 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "cut grids cost %s\n" % str(cost_time)
        log_file.write(log)

    s_time = datetime.datetime.now()
    util.write_json("grids_dict", INER_DATA_DIR, grids_dict)
    with open(LOG_FILE, 'a') as log_file:
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "grids_dict.json save cost %s\n" % str(cost_time)
        log_file.write(log)