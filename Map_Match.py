# -*- coding:utf-8 -*-
__author__ = 'Neo'

import os
import math
import datetime
import utilities
import unicodecsv

INER_DATA_DIR = "Intermediate"
GRIDE_FILE = 'grids_dict'
LONGITUDE_POSITION_IN_CSV = 2
LATITUDE_POSITION_IN_CSV = 3

RADIUS = 6371000
MAXDIST = 10000
STEP = 0.02

class Map_Match:
    __min_lat = 0
    __max_lat = 0
    __min_lon = 0
    __max_lon = 0
    __num_lat = 0
    __num_lon = 0
    __num_grids = 0
    __grids = {}

    def __get_output_file_name(self, input_file_name):
        name = input_file_name.split('.')
        name[0] += '+'
        return name[0] + '.' + name[1]

    def match(self, folder_name):
        # 输入是文件夹名称
        # 文件夹内每个文件是剪好的一条轨迹
        # 循环打开每个文件,对每个文件做轨迹匹配
        # 匹配完在每个csv文件每行末尾增加字段:seg_id,dis
        os.chdir('Raw/' + folder_name)
        for file in os.listdir('.'):
            # print file
            self.__match_per_freight(file, self.__get_output_file_name(file))
        os.chdir('..')

    def __match_per_freight(self, input_file, output_file):
        rows_list = []
        with open(input_file) as input_csv:
            reader = unicodecsv.reader(input_csv)
            for row in reader:
                point = self.__construct_point(float(row[LONGITUDE_POSITION_IN_CSV]),
                                               float(row[LATITUDE_POSITION_IN_CSV]))
                matched_segment, segment_type, distance = self.__match_point_naive(point)
                row.append(matched_segment, segment_type, distance)
                rows_list.append(row)
        if not os.path.exists(output_file):
            f = open(output_file, 'w')
            f.close()
        with open(output_file, 'a') as output_csv:
            writer = unicodecsv.writer(output_csv)
            writer.writerows(rows_list)

    def __construct_point(self, x, y):
        point = dict()
        point["x"] = x
        point["y"] = y
        return point

    def __match_point_naive(self, point):
        point_id = self.__find_grid_id(point["x"], point["y"])
        neighbor_grid = self.__find_neighbor(point_id)
        min_dist = MAXDIST
        min_route = None
        for grid_id in neighbor_grid:
            routes = self.__grids[str(grid_id)]
            for route in routes:
                dist = self.__cal_point_route(point, route)
                if dist < min_dist:
                    min_route = route.keys()[0]
                    min_type = route.values()[0]['highway']
                    min_dist = dist
        return min_route, min_type, min_dist

    def __init__(self):

        s_time = datetime.datetime.now()
        self.__get_range_of_map()
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "get_range_of_map cost %s\n" % str(cost_time)
        utilities.write_log('matching.log', log)

        s_time = datetime.datetime.now()
        self.__get_grids()
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "get_grids cost %s\n" % str(cost_time)
        utilities.write_log('matching.log', log)

        pass

    def __get_grids(self):
        self.__grids = utilities.read_json(GRIDE_FILE, INER_DATA_DIR)

    def __find_grid_id(self, y, x):
        loc_x = int((x - self.__min_lat) / STEP)
        if loc_x == self.__num_lat:
            loc_x -= 1
        loc_y = int((y - self.__min_lon) / STEP)
        if loc_y == self.__num_lon:
            loc_y -= 1
        loc = loc_x * self.__num_lon + loc_y
        return loc

    def __get_range_of_map(self):
        range_of_map = utilities.read_json('map_info', INER_DATA_DIR)
        self.__min_lat, self.__max_lat, self.__min_lon, \
        self.__max_lon, self.__num_lat, self.__num_lon, self.__num_grids = range_of_map

    def __cal_probe_distance(self, s_lat, s_lon, e_lat, e_lon):
        s_lat = math.radians(s_lat)
        s_lon = math.radians(s_lon)
        e_lat = math.radians(e_lat)
        e_lon = math.radians(e_lon)
        theta_lat = s_lat - e_lat
        theta_long = s_lon - e_lon
        first = pow(math.sin(theta_lat / 2.0), 2)
        second = math.cos(s_lat) * math.cos(e_lat) * pow(math.sin(theta_long / 2.0), 2)
        angle = 2 * math.asin(math.sqrt(first + second))
        return math.floor(RADIUS * angle + 0.5)

    def __find_neighbor(self, grid_id):
        right_up = self.__num_lon - 1
        left_down = self.__num_lon * (self.__num_lat - 1)
        right_down = self.__num_lon * self.__num_lat - 1
        up = range(1, right_up)
        down = range(left_down + 1, right_down)
        left = range(self.__num_lon, left_down, self.__num_lon)
        right = range(self.__num_lon + right_up, right_down, self.__num_lon)
        if grid_id in up:
            ret_id = self.__find_neighbor_up(grid_id)
        elif grid_id in down:
            ret_id = self.__find_neighbor_down(grid_id)
        elif grid_id in left:
            ret_id = self.__find_neighbor_left(grid_id)
        elif grid_id in right:
            ret_id = self.__find_neighbor_right(grid_id)
        elif grid_id == 0:
            ret_id = self.__find_neighbor_left_up(grid_id)
        elif grid_id == left_down:
            ret_id = self.__find_neighbor_left_down(grid_id)
        elif grid_id == right_up:
            ret_id = self.__find_neighbor_right_up(grid_id)
        elif grid_id == right_down:
            ret_id = self.__find_neighbor_right_down(grid_id)
        else:
            ret_id = self.__find_neighbor_inside(grid_id)
        return ret_id

    def __cal_point_route(self, point, segment):
        s_x = float(segment.values()[0]["snode"][0])
        s_y = float(segment.values()[0]["snode"][1])
        e_x = float(segment.values()[0]["enode"][0])
        e_y = float(segment.values()[0]["enode"][1])
        p_x, p_y = self.__get_project_point(point, s_x, s_y, e_x, e_y)
        if (p_x - s_x) * (p_x - e_x) < 0 and (p_y - s_y) * (p_y - e_y) < 0:
            return self.__cal_probe_distance(point["x"], point["y"], p_x, p_y)
        else:
            return min(self.__cal_probe_distance(point["x"], point["y"], s_x, s_y),
                       self.__cal_probe_distance(point["x"], point["y"], e_x, e_y))

    def __get_project_point(self, point, x1, y1, x2, y2):
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

    def __find_neighbor_left_up(self, grid_id):
        ret_id = list()
        ret_id.append(grid_id)
        ret_id.append(1)
        ret_id.append(self.__num_lon)
        ret_id.append(self.__num_lon + 1)
        return ret_id

    def __find_neighbor_right_up(self, grid_id):
        ret_id = list()
        ret_id.append(grid_id)
        ret_id.append(grid_id - 1)
        ret_id.append(grid_id + self.__num_lon)
        ret_id.append(grid_id + self.__num_lon - 1)
        return ret_id

    def __find_neighbor_left_down(self, grid_id):
        ret_id = list()
        ret_id.append(grid_id)
        ret_id.append(grid_id - self.__num_lon)
        ret_id.append(grid_id - self.__num_lon + 1)
        ret_id.append(grid_id+1)
        return ret_id

    def __find_neighbor_right_down(self, grid_id):
        ret_id = list()
        ret_id.append(grid_id)
        ret_id.append(grid_id - self.__num_lon - 1)
        ret_id.append(grid_id - self.__num_lon)
        ret_id.append(grid_id - 1)
        return ret_id

    def __find_neighbor_up(self, grid_id):
        ret_id = list()
        ret_id.append(grid_id - 1)
        ret_id.append(grid_id)
        ret_id.append(grid_id+1)
        ret_id.append(grid_id + self.__num_lon - 1)
        ret_id.append(grid_id + self.__num_lon)
        ret_id.append(grid_id + self.__num_lon + 1)
        return ret_id

    def __find_neighbor_down(self, grid_id):
        ret_id = list()
        ret_id.append(grid_id - 1)
        ret_id.append(grid_id)
        ret_id.append(grid_id + 1)
        ret_id.append(grid_id - self.__num_lon - 1)
        ret_id.append(grid_id - self.__num_lon)
        ret_id.append(grid_id - self.__num_lon + 1)
        return ret_id

    def __find_neighbor_left(self, grid_id):
        ret_id = list()
        ret_id.append(grid_id - self.__num_lon)
        ret_id.append(grid_id)
        ret_id.append(grid_id + self.__num_lon)
        ret_id.append(grid_id - self.__num_lon + 1)
        ret_id.append(grid_id + 1)
        ret_id.append(grid_id + self.__num_lon + 1)
        return ret_id

    def __find_neighbor_right(self, grid_id):
        ret_id = list()
        ret_id.append(grid_id - self.__num_lon)
        ret_id.append(grid_id)
        ret_id.append(grid_id + self.__num_lon)
        ret_id.append(grid_id - self.__num_lon - 1)
        ret_id.append(grid_id - 1)
        ret_id.append(grid_id + self.__num_lon - 1)
        return ret_id

    def __find_neighbor_inside(self, grid_id):
        ret_id = list()
        ret_id.append(grid_id - 1)
        ret_id.append(grid_id)
        ret_id.append(grid_id + 1)
        ret_id.append(grid_id - self.__num_lon - 1)
        ret_id.append(grid_id - self.__num_lon)
        ret_id.append(grid_id - self.__num_lon + 1)
        ret_id.append(grid_id + self.__num_lon - 1)
        ret_id.append(grid_id + self.__num_lon)
        ret_id.append(grid_id + self.__num_lon + 1)
        return ret_id

if __name__ == "__main__":
    map_matching = Map_Match()

    utilities.write_log('matching.log', '\n')
    s_time = datetime.datetime.now()
    map_matching.match('B61962')
    e_time = datetime.datetime.now()
    cost_time = e_time - s_time
    log = "Map matching cost %s\n" % str(cost_time)
    utilities.write_log('matching.log', log)

    # map_matching.match('B61962')
