# -*- coding:utf-8 -*-
__author__ = 'Neo'

import os
import unicodecsv

TEST_FOLDER = 'Raw'
TEST_FILE = 'B61962/2+.csv'

def get_output_file_name(input_file_name):
    name = input_file_name.split('.')
    name[0] += '+'
    return name[0] + '.' + name[1]

def match_per_freight(input_file, output_file):
    liiist = []
    string = 'test'
    os.chdir(TEST_FOLDER)
    with open(input_file) as input_csv:
        reader = unicodecsv.reader(input_csv)
        for row in reader:
            row.append(string)
            liiist.append(row)
    os.chdir('..')
    if not os.path.exists(output_file):
        # os.mknod(output_file)
        f = open(output_file, 'w')
        f.close()
    with open(output_file, 'a') as output_csv:
        writer = unicodecsv.writer(output_csv)
        writer.writerows(liiist)

def extract_time(input_file):
    liiist = []
    string = 'test'
    os.chdir(TEST_FOLDER)
    with open(input_file) as input_csv:
        reader = unicodecsv.reader(input_csv)
        for row in reader:
            print row[10]
            row_segments = row[1].split(':')
            print row_segments[1], row_segments[2]
            print float(row_segments[1]) + 60 - float(row_segments[2])
            break
    os.chdir('..')

if __name__ == "__main__":
    # match_per_freight('B61962/2.csv', 'Test/3.csv')
    # print get_output_file_name('B61962/2.csv')
    # aaa = [1, 2, 3, 4, 5]
    # ater = aaa.__iter__()
    # val = ater.next()
    # try:
    #     while True:
    #         val = ater.next()
    #         print val
    # except StopIteration:
    #     pass
    extract_time(TEST_FILE)
