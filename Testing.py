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
TIME_POSITION_IN_CSV = 1
ROAD_TYPE_POSITION_IN_CSV = 10
TEST_FOLDER = 'B61962'

RADIUS = 6371000

class Speed_Overload_Testing:
    __average_speeds = {}
    __speed_limit = {}

    def overload_test(self, folder):
        self.speed_test(folder)

    def __init__(self):
        s_time = datetime.datetime.now()
        self.__get_speed_limit()
        e_time = datetime.datetime.now()
        cost_time = e_time - s_time
        log = "get_speed_limit cost %s\n" % str(cost_time)
        utilities.write_log('matching.log', log)

    def __get_speed_limit(self):
        self.__speed_limit = utilities.read_json('speed_limit', INER_DATA_DIR)

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
            if file.split('.')[0][-1] == '+':
                self.__speed_test_per_freight(file, self.__get_output_file_name(file))
        os.chdir('..')

    def __speed_test_per_freight(self, input_file, output_file):
        rows_list = []
        with open(input_file) as input_csv:
            reader = unicodecsv.reader(input_csv)
            reader_iter = reader.__iter__()
            row_former = reader_iter.next()
            row_later = reader_iter.next()
            former_lon = float(row_former[LONGITUDE_POSITION_IN_CSV])
            former_lat = float(row_former[LATITUDE_POSITION_IN_CSV])
            former_minite = float(row_former[TIME_POSITION_IN_CSV].split(':')[1])
            former_second = float(row_former[TIME_POSITION_IN_CSV].split(':')[2])
            former_type = row_former[ROAD_TYPE_POSITION_IN_CSV]
            later_lon = float(row_later[LONGITUDE_POSITION_IN_CSV])
            later_lat = float(row_later[LATITUDE_POSITION_IN_CSV])
            later_minite = float(row_later[TIME_POSITION_IN_CSV].split(':')[1])
            later_second = float(row_later[TIME_POSITION_IN_CSV].split(':')[2])
            distance_later = self.__cal_probe_distance(former_lat, former_lon, later_lat, later_lon)
            time_later = (later_minite + 60.0 - former_minite) % 60.0 * 60.0 + later_second - former_second
            # print time_later
            # print later_minite, former_minite, later_second, former_second
            # 做两个循环外变量,否则捕捉异常时会出错
            distance_former = distance_later
            time_former = time_later
            v_former = distance_later / time_later
            is_overspeed = v_former > self.__speed_limit[former_type]
            row_former.extend([v_former, is_overspeed])
            rows_list.append(row_former)
            try:
                while True:
                    row_former = row_later
                    former_lon = later_lon
                    former_lat = later_lat
                    former_minite = later_minite
                    former_second = later_second
                    former_type = row_former[ROAD_TYPE_POSITION_IN_CSV]
                    distance_former = distance_later
                    time_former = time_later
                    row_later = reader_iter.next()
                    later_lon = float(row_later[LONGITUDE_POSITION_IN_CSV])
                    later_lat = float(row_later[LATITUDE_POSITION_IN_CSV])
                    later_minite = float(row_later[TIME_POSITION_IN_CSV].split(':')[1])
                    later_second = float(row_later[TIME_POSITION_IN_CSV].split(':')[2])
                    distance_later = self.__cal_probe_distance(former_lat, former_lon, later_lat, later_lon)
                    time_later = (later_minite + 60.0 - former_minite) % 60.0 * 60.0 + later_second - former_second
                    if time_later == 0:
                        v_former = 0
                    else:
                        v_former = (distance_former + distance_later) / (time_former + time_later)
                    is_overspeed = v_former > self.__speed_limit[former_type]
                    row_former.extend([v_former, is_overspeed])
                    rows_list.append(row_former)
            except StopIteration:
                v_former = distance_former / time_former
                is_overspeed = v_former > self.__speed_limit[former_type]
                row_former.extend([v_former, is_overspeed])
                rows_list.append(row_former)
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


if __name__ == "__main__":
    speed_test = Speed_Overload_Testing()
    utilities.write_log('speed.log', '\n')
    s_time = datetime.datetime.now()
    speed_test.speed_test(TEST_FOLDER)
    e_time = datetime.datetime.now()
    cost_time = e_time - s_time
    log = "speed test cost %s\n" % str(cost_time)
    utilities.write_log('testing.log', log)
