#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Udacity Data Science For Business Nanodegree
Part 1: Data wrangling
Project: Wrangle OpenStreetMap Data
Student: Jerome Vergueiro Vonk

Script: 1_count_tags.py
Goal: discover what types of tags there are how many of which
"""
import xml.etree.cElementTree as ET
import pprint
import os
import sys

DATA_PATH   = "..\\1. Data\\Full\\Madrid_custom_11122017.osm"
SAMPLE_PATH = "..\\1. Data\\Sample\\Madrid_custom_11122017_sample_1.osm"

OUTPUT_FILE = "output\\1_count_tags_.txt"

def count_tags(filename):
    """Parse all tags in the data file and create a dictionary containing tag types and quantity"""
    dict_tags = {}

    osm_file = open(filename, "r", encoding="utf8")
    for event, elem in ET.iterparse(osm_file):
        if elem.tag in dict_tags:
            dict_tags[elem.tag] += 1
        else:
            dict_tags[elem.tag] = 1

    return dict_tags

def test(dataset):
    """Perform the test on the selected dataset"""
    print("Running 1_count_tags.py")
    tags = {}

    # Run against the sample or the full data?
    if dataset == "sample":
        tags = count_tags(SAMPLE_PATH)
    else:
        tags = count_tags(DATA_PATH)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as fo:
        pprint.pprint(tags, fo)

if __name__ == "__main__":

    dataset = "full"
    if len(sys.argv) > 1:
        dataset = sys.argv[1]

    test(dataset)