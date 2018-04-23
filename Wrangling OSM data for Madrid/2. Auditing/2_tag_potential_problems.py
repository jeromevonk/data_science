#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Udacity Data Science For Business Nanodegree
Part 1: Data wrangling
Project: Wrangle OpenStreetMap Data
Student: Jerome Vergueiro Vonk

Script: 2_tag_potential_problems.py
Goal: check potential problems witht the tags starting with <tag>
"""

import xml.etree.cElementTree as ET
import pprint
import re
import os
import sys

lower        = re.compile(r'^([a-z]|_)*$')
lower_colon  = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

DATA_PATH   = "..\\1. Data\\Full\\Madrid_custom_11122017.osm"
SAMPLE_PATH = "..\\1. Data\\Sample\\Madrid_custom_11122017_sample_1.osm"

OUTPUT_FILE = "output\\2_tag_potential_problems.txt"


def key_type(element, keys):
    """For a given tag, look for potential problems"""
    if element.tag == "tag":
        if lower.search(element.attrib['v']):
            #print(element.attrib['v'], "lower")
            keys['lower'] += 1

        elif lower_colon.search(element.attrib['v']):
            #print(element.attrib['v'], 'lower_colon')
            keys['lower_colon'] += 1

        elif problemchars.search(element.attrib['v']):
            #print(element.attrib['v'], 'problemchars')
            keys['problemchars'] += 1
        else:
            #print(element.attrib['v'], 'other')
            keys['other'] += 1

    return keys



def process_map(filename):
    """Iterate through every tag in the data file"""
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    osm_file = open(filename, "r", encoding="utf8")
    for _, element in ET.iterparse(osm_file):
        keys = key_type(element, keys)

    return keys



def test(dataset):
    """Perform the test on the selected dataset"""
    print("Running 2_tag_potential_problems.py")
    keys = {}

    # Run against the sample or the full data?
    if dataset == "sample":
        keys = process_map(SAMPLE_PATH)
    else:
        keys = process_map(DATA_PATH)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as fo:
        pprint.pprint(keys, fo)

if __name__ == "__main__":

    dataset = "full"
    if len(sys.argv) > 1:
        dataset = sys.argv[1]

    test(dataset)