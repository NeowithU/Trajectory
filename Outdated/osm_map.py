# -*- coding:utf-8 -*-
__author__ = 'Neo'

import unicodecsv
import overpass
import os
import glob
import numpy as np
from sklearn.cluster import DBSCAN, MeanShift, estimate_bandwidth, Birch
from sklearn.metrics.pairwise import euclidean_distances

from utilities import read_json
from utilities import write_pickle
from utilities import show_metrics

SJZ_LAT_MIN_THRES = 3600000
SJZ_LAT_MAX_THRES = 4000000
SJZ_LON_MIN_THRES = 11000000
SJZ_LON_MAX_THRES = 12000000

SH_LAT_MIN_THRES = 3000000
SH_LAT_MAX_THRES = 3400000
SH_LON_MIN_THRES = 12000000
SH_LON_MAX_THRES = 12500000

DATA_DIR = "Raw"
TEMP_DIR = "Intermediate"
SAMPLE_DATA = "utfB61962.csv"

def get_one_geo_range(file_name, dir_name=DATA_DIR):
	lat_list = list()
	lon_list = list()
	os.chdir(dir_name)
	with open(file_name) as csvFile:
		reader = unicodecsv.reader(csvFile, encoding="utf-8")
		for row in reader:
			lon_list.append(float(row[0]))
			lat_list.append(float(row[1]))
	lat_min = min(lat_list)
	lat_max = max(lat_list)
	lon_min = min(lon_list)
	lon_max = max(lon_list)
	os.chdir("..")
	return (lat_min, lat_max), (lon_min, lon_max)


def get_all_geo_range(dir_name, type_postfix="csv"):
	os.chdir(dir_name)
	ret_dict = dict()
	for csv_file in glob.glob("*." + type_postfix):
		file_name = csv_file.split(".")[0]
		with open(csv_file) as inFile:
			lat_list = list()
			lon_list = list()
			# skip first line
			inFile.readline()
			lines = inFile.readlines()
			for line in lines:
				parts = line.split("|")
				lat_list.append(float(parts[1]))
				lon_list.append(float(parts[0]))
			lat_min = min(lat_list)
			lat_max = max(lat_list)
			lon_min = min(lon_list)
			lon_max = max(lon_list)
			ret_dict[file_name] = [(lat_min, lat_max), (lon_min, lon_max)]
	os.chdir("..")
	return ret_dict


def get_training_set(geo_ranges_file):
	geo_data = read_json(geo_ranges_file)
	X = list()

	for key in geo_data.keys():
		lat = geo_data[key][0]
		lon = geo_data[key][1]
		X.append([lat[0], lat[1], lon[0], lon[1]])

	return X


def get_training_set_norm(geo_ranges_file):
	geo_data = read_json(geo_ranges_file)
	X = list()

	for key in geo_data.keys():
		lat = geo_data[key][0]
		lon = geo_data[key][1]
		X.append([lat[0], lat[1], lon[0], lon[1]])

	# normalize using ndarray indexing
	X = np.array(X)
	lat_min_max = np.max(X[..., 0])
	lat_max_max = np.max(X[..., 1])
	lon_min_max = np.max(X[..., 2])
	lon_max_max = np.max(X[..., 3])

	X[..., 0] = X[..., 0] / lat_min_max
	X[..., 1] = X[..., 1] / lat_max_max
	X[..., 2] = X[..., 2] / lon_min_max
	X[..., 3] = X[..., 3] / lon_max_max

	return X


def get_geo_cluster(geo_ranges_file, labels_true_dict, set_eps=5):
	geo_data = read_json(geo_ranges_file)
	labels_true = list()
	X = list()

	# put geo_data into X and train in DBSCAN
	for key in geo_data.keys():
		lat = geo_data[key][0]
		lon = geo_data[key][1]
		X.append([lat[0], lat[1], lon[0], lon[1]])
		labels_true.append(labels_true_dict[key])

	db = DBSCAN(eps=set_eps).fit(X)
	labels = db.labels_

	# show metrics
	show_metrics(X, labels, labels_true)


def get_geo_cluster_norm(geo_ranges_file, labels_true_dict):
	geo_data = read_json(geo_ranges_file)
	labels_true = list()

	# get labels
	for key in geo_data.keys():
		labels_true.append(labels_true_dict[key])

	# get training set
	X = get_training_set_norm(geo_ranges_file)
	db = DBSCAN(eps=0.02).fit(X)
	labels = db.labels_

	# shoe metrics
	show_metrics(X, labels, labels_true)


def get_geo_cluster_min(geo_ranges_file, labels_true_dict):
	geo_data = read_json(geo_ranges_file)
	labels_true = list()
	X = list()

	# put geo_data into X and train in DBSCAN
	for key in geo_data.keys():
		lat = geo_data[key][0]
		lon = geo_data[key][1]
		X.append([lat[0], lat[1], lon[0], lon[1]])
		labels_true.append(labels_true_dict[key])

	bandwith = estimate_bandwidth(np.array(X), quantile=0.5)
	ms = MeanShift(bandwith).fit(X)
	labels = ms.labels_

	# show metrics
	show_metrics(X, labels, labels_true)


def get_geo_cluster_brc(geo_ranges_file, labels_true_dict):
	geo_data = read_json(geo_ranges_file)
	labels_true = list()
	X = list()

	# put geo_data into X and train in DBSCAN
	for key in geo_data.keys():
		lat = geo_data[key][0]
		lon = geo_data[key][1]
		X.append([lat[0], lat[1], lon[0], lon[1]])
		labels_true.append(labels_true_dict[key])

	brc = Birch().fit(X)
	labels = brc.labels_

	# show metrics
	show_metrics(X, labels, labels_true)


def get_clusters_labels():
	labels_true = dict()
	median_info = read_json("median_info.txt")

	for file_name in median_info.keys():
		key_name = file_name.split(".")[0]
		lat_median = median_info[file_name][0]
		lon_median = median_info[file_name][1]

		if SJZ_LAT_MIN_THRES < lat_median < SJZ_LAT_MAX_THRES and SJZ_LON_MIN_THRES < lon_median < SJZ_LON_MAX_THRES:
			labels_true[key_name] = 0
		elif SH_LAT_MIN_THRES < lat_median < SH_LAT_MAX_THRES and SH_LON_MIN_THRES < lon_median < SH_LON_MAX_THRES:
			labels_true[key_name] = 1
		else:
			labels_true[key_name] = -1

	return labels_true


def get_osm_map(lat_min, lat_max, lon_min, lon_max):
	# construct map query
	api = overpass.API()
	map_query = overpass.MapQuery(lat_min, lon_min, lat_max, lon_max)
	response = api.Get(map_query)
	map_data = response[unicode("elements")]

	# write map to file
	write_pickle("foo.txt", map_data)


def get_pairwise_distances(geo_ranges_file):
	geo_data = read_json(geo_ranges_file)
	X = list()

	# put geo_data into X and train in DBSCAN
	for key in geo_data.keys():
		lat = geo_data[key][0]
		lon = geo_data[key][1]
		X.append([lat[0], lat[1], lon[0], lon[1]])

	dist = euclidean_distances(X, X)
	print dist.shape
	print dist[0]
	print np.min(dist[0][1:])


if __name__ == "__main__":
	"""
	print get_one_geo_range(test_file_name)
	geo_data = get_all_geo_range(DATA_DIR)
	print len(geo_data.keys())
	#write_json("geo_ranges.txt", geo_data)
	"""
	labels_true_dict = get_clusters_labels()
	#get_geo_cluster("geo_ranges.txt", labels_true_dict)
	#X = get_training_set_norm("geo_ranges.txt")
	#print X[0:5]
	get_geo_cluster_min("geo_ranges.txt", labels_true_dict)
	#et_geo_cluster_min("geo_ranges.txt", labels_true_dict)
	#get_geo_cluster_brc("geo_ranges.txt", labels_true_dict)
	#get_pairwise_distances("geo_ranges.txt")
