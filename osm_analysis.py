# -*- coding:utf-8 -*-
__author__ = 'Neo'

from collections import defaultdict

from utilities import read_pickle, read_json
from road_map import get_tags_list


WHOLE_WAYS = read_json("whole_ways.txt")


def count_way_tag_freq(way_map):
	ret_dict = defaultdict(int)

	for way in way_map:
		way_tag = way["tags"]["highway"]
		ret_dict[way_tag] += 1

	return ret_dict


def divide_way(way_map):
	ret_dict = defaultdict(list)

	for way in way_map:
		way_tag = way["tags"]["highway"]
		ret_dict[way_tag].append(way["id"])

	return ret_dict


def reveal_equivalence(one_way_group, whole_ways=WHOLE_WAYS):
	test_way_id = one_way_group[0]
	nodes_info = whole_ways[str(test_way_id)]["nodes_info"]
	n_nodes = len(nodes_info)
	s_lat, s_lon = nodes_info[0][1], nodes_info[0][2]
	m_lat, m_lon = nodes_info[n_nodes/2][1], nodes_info[n_nodes/2][2]
	e_lat, e_lon = nodes_info[-1][1], nodes_info[-1][2]
	print test_way_id, ":", (s_lat, s_lon), (m_lat, m_lon), (e_lat, e_lon)


if __name__ == "__main__":
	osm_map = read_pickle("road_map.txt")
	way_map = get_tags_list(osm_map)
	#print way_map[0]
	tag_freq = count_way_tag_freq(way_map=way_map)
	#print tag_freq
	way_groups = divide_way(way_map)
	reveal_equivalence(way_groups["trunk"])