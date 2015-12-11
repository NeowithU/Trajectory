# -*- coding:utf-8 -*-
__author__ = 'Neo'

from math import *
from collections import defaultdict
import os
import numpy as np
import unicodecsv

from utilities import read_json, construct_point
from osm_map import get_one_geo_range

RADIUS = 6371000
MAXDIST = 10000
GRID_LEN = 10

COEFFICIENT = 1000000.0

DATA_DIR = "Raw"
TEMP_DIR = "Intermediate"
SAMPLE_DATA = "la.csv"

def cal_probe_distance(s_lat, s_lon, e_lat, e_lon):
	s_lat = radians(s_lat)
	s_lon = radians(s_lon)
	e_lat = radians(e_lat)
	e_lon = radians(e_lon)
	theta_lat = s_lat - e_lat
	theta_long = s_lon - e_lon
	first = pow(sin(theta_lat / 2.0), 2)
	second = cos(s_lat) * cos(e_lat) * pow(sin(theta_long / 2.0), 2)
	angle = 2 * asin(sqrt(first + second))
	return floor(RADIUS * angle + 0.5)

def get_range_array(start, stop, step):
	i_start = int(start * COEFFICIENT)
	i_stop = int(stop * COEFFICIENT)
	i_step = int(step * COEFFICIENT / GRID_LEN)
	i_list = range(i_start, i_stop, i_step)
	return [item / COEFFICIENT for item in i_list]

def find_neighbor_left_up(grid_id, grid_len):
	ret_id = list()
	ret_id.append(grid_id)
	ret_id.append(1)
	ret_id.append(grid_len)
	ret_id.append(grid_len+1)
	return ret_id

def find_neighbor_right_up(grid_id, grid_len):
	ret_id = list()
	ret_id.append(grid_id)
	ret_id.append(grid_id-1)
	ret_id.append(grid_id+grid_len)
	ret_id.append(grid_id+grid_len-1)
	return ret_id

def find_neighbor_left_down(grid_id, grid_len):
	ret_id = list()
	ret_id.append(grid_id)
	ret_id.append(grid_id-grid_len)
	ret_id.append(grid_id-grid_len+1)
	ret_id.append(grid_id+1)
	return ret_id

def find_neighbor_right_down(grid_id, grid_len):
	ret_id = list()
	ret_id.append(grid_id)
	ret_id.append(grid_id-grid_len-1)
	ret_id.append(grid_id-grid_len)
	ret_id.append(grid_id-1)
	return ret_id

def find_neighbor_up(grid_id, grid_len):
	ret_id = list()
	ret_id.append(grid_id-1)
	ret_id.append(grid_id)
	ret_id.append(grid_id+1)
	ret_id.append(grid_id+grid_len-1)
	ret_id.append(grid_id+grid_len)
	ret_id.append(grid_id+grid_len+1)
	return ret_id

def find_neighbor_down(grid_id, grid_len):
	ret_id = list()
	ret_id.append(grid_id-1)
	ret_id.append(grid_id)
	ret_id.append(grid_id+1)
	ret_id.append(grid_id-grid_len-1)
	ret_id.append(grid_id-grid_len)
	ret_id.append(grid_id-grid_len+1)
	return ret_id

def find_neighbor_left(grid_id, grid_len):
	ret_id = list()
	ret_id.append(grid_id-grid_len)
	ret_id.append(grid_id)
	ret_id.append(grid_id+grid_len)
	ret_id.append(grid_id-grid_len+1)
	ret_id.append(grid_id+1)
	ret_id.append(grid_id+grid_len+1)
	return ret_id

def find_neighbor_right(grid_id, grid_len):
	ret_id = list()
	ret_id.append(grid_id-grid_len)
	ret_id.append(grid_id)
	ret_id.append(grid_id+grid_len)
	ret_id.append(grid_id-grid_len-1)
	ret_id.append(grid_id-1)
	ret_id.append(grid_id+grid_len-1)
	return ret_id

def find_neighbor_inside(grid_id, grid_len):
	ret_id = list()
	ret_id.append(grid_id-1)
	ret_id.append(grid_id)
	ret_id.append(grid_id+1)
	ret_id.append(grid_id-grid_len-1)
	ret_id.append(grid_id-grid_len)
	ret_id.append(grid_id-grid_len+1)
	ret_id.append(grid_id+grid_len-1)
	ret_id.append(grid_id+grid_len)
	ret_id.append(grid_id+grid_len+1)
	return ret_id

def find_neighbor(grid_id, grid_len):
	right_up = grid_len - 1
	left_down = grid_len * (grid_len-1)
	right_down = grid_len * grid_len - 1
	up = range(1, right_up)
	#print up
	down = range(left_down+1, right_down)
	#print down
	left = range(1*grid_len, left_down, grid_len)
	#print left
	right = range(1*grid_len + right_up, right_down, grid_len)
	#print right

	if grid_id in up:
		ret_id = find_neighbor_up(grid_id, grid_len)
	elif grid_id in down:
		ret_id = find_neighbor_down(grid_id, grid_len)
	elif grid_id in left:
		ret_id = find_neighbor_left(grid_id, grid_len)
	elif grid_id in right:
		ret_id = find_neighbor_right(grid_id, grid_len)
	elif grid_id == 0:
		ret_id = find_neighbor_left_up(grid_id, grid_len)
	elif grid_id == left_down:
		ret_id = find_neighbor_left_down(grid_id, grid_len)
	elif grid_id == right_up:
		ret_id = find_neighbor_right_up(grid_id, grid_len)
	elif grid_id == right_down:
		ret_id = find_neighbor_right_down(grid_id, grid_len)
	else:
		ret_id = find_neighbor_inside(grid_id, grid_len)

	return ret_id

def get_grid_map_modify(modify_whole_slices):
    ret_grid = defaultdict(list)
    print "321"
    for slice_name in modify_whole_slices:
        ndlist = modify_whole_slices[slice_name]["data"]
        print "123"
        print LAT_RANGE, LON_RANGE
        for nd in ndlist:
            grid = get_grid_id(WHOLE_NODES[str(nd)]["lat"], WHOLE_NODES[str(nd)]["lon"], LAT_RANGE, LON_RANGE)
            ret_grid[str(grid)].append(slice_name)
    print ret_grid.items()
    return ret_grid

def find_id(x, range_list):
	ret_id = 0
	for i in range(len(range_list)-1, 0, -1):
		if x >= range_list[i]:
			ret_id = i
			break
	return ret_id

def get_grid_id(lat, lon, lat_range, lon_range):
	lat_id = find_id(lat, lat_range)
	lon_id = find_id(lon, lon_range)
	return lat_id * 10 + lon_id

def get_project_point(point, x1, y1, x2, y2):
	x0 = point["x"]
	y0 = point["y"]
	fenzi = (x1-x0) * (x1-x2) + (y1-y0) * (y1-y2)
	fenmu = math.pow(x1-x2, 2) + math.pow(y1-y2, 2)
	if fenmu == 0.0:
		return x1, y1
	temp = fenzi / fenmu
	ret_x = x1 + temp * (x2-x1)
	ret_y = y1 + temp * (y2-y1)
	return ret_x, ret_y

def cal_point_route(point, route_id):
	route = MODIFY_WHOLE_SLICES[route_id]
	s_inter = str(route["s_inter"])
	e_inter = str(route["e_inter"])
	s_x = WHOLE_NODES[s_inter]["lat"]
	s_y = WHOLE_NODES[s_inter]["lon"]
	e_x = WHOLE_NODES[e_inter]["lat"]
	e_y = WHOLE_NODES[e_inter]["lon"]
	p_x, p_y = get_project_point(point, s_x, s_y, e_x, e_y)
	dist = cal_probe_distance(point["x"], point["y"], p_x, p_y)

	return dist

def match_route_naive(traj, grid_map):
	ret_route = list()
	for point in traj:
		point_id = get_grid_id(point["x"], point["y"], LAT_RANGE, LON_RANGE)
		neighbor_grid = find_neighbor(point_id, GRID_LEN)
		#print "neighbor grid:", neighbor_grid
		min_dist = MAXDIST
		min_route = None
		for grid_id in neighbor_grid:
			routes = grid_map[str(grid_id)]
			#print "routes:", routes
			for route in routes:
				dist = cal_point_route(point, route)
				if dist < min_dist:
					min_route = route
					min_dist = dist

		ret_route.append((min_route, min_dist))

	return ret_route

def generate_test_traj(file_name, end, dir_name=DATA_DIR):
    ret_traj = list()
    os.chdir(dir_name)
    with open(file_name) as csvFile:
        reader = unicodecsv.reader(csvFile, encoding="utf-8")
        i = 0
        for row in reader:
            ret_traj.append(construct_point(float(row[1]), float(row[0])))
            i += 1
            if i >= end:
                break
    os.chdir("..")
    # print ret_traj
    return ret_traj

if __name__ == "__main__":
    # calculate min and max range
    (MIN_LAT, MAX_LAT), (MIN_LON, MAX_LON) = get_one_geo_range(file_name=SAMPLE_DATA)
    LAT_RANGE = get_range_array(MIN_LAT, MAX_LAT, MAX_LAT-MIN_LAT)
    LON_RANGE = get_range_array(MIN_LON, MAX_LON, MAX_LON-MIN_LON)
    # read ways and nodes data from file
    WHOLE_WAYS = read_json("whole_ways.txt")
    WHOLE_NODES = read_json("whole_nodes.txt")
    NEW_WHOLE_INTER = read_json("new_whole_inter.txt")
    MODIFY_WHOLE_SLICES = read_json("modify_whole_slices.txt")
    # get grid map
    modify_grid_map = get_grid_map_modify(MODIFY_WHOLE_SLICES)
    # map matching
    traj = generate_test_traj(file_name=SAMPLE_DATA, end=10)
    match_routes = match_route_naive(traj, modify_grid_map)
    dist = [data[1] for data in match_routes]
    print np.average(dist)
    print match_routes