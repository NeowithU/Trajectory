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

class Speed_Overload_Testing:
    __average_speeds = {}

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

    def speed_test(self, folder_name):
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

                rows_list.append(row)
        if not os.path.exists(output_file):
            f = open(output_file, 'w')
            f.close()
        with open(output_file, 'a') as output_csv:
            writer = unicodecsv.writer(output_csv)
            writer.writerows(rows_list)

    def __get_output_file_name(self, input_file_name):
        name = input_file_name.split('.')
        name[0] += '+'
        return name[0] + '.' + name[1]