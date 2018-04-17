#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Udacity Data Science For Business Nanodegree
Part 1: Data wrangling
Project: Wrange OpenStreetMap Data
Student: Jerome Vergueiro Vonk

Script: 3_count_unique_users.py
Goal: count how many unique users entered data into the map
"""
import xml.etree.cElementTree as ET
import pprint
import os
import sys

DATA_PATH   = "..\\1. Data\\Full\\Madrid_custom_11122017.osm"
SAMPLE_PATH = "..\\1. Data\\Sample\\Madrid_custom_11122017_sample_1.osm"

OUTPUT_FILE = "output\\3_count_unique_users.txt"

def get_user(element):
    return


def process_map(filename):
    """Iterate through every tag in the data file and get the user id, if there is one. Return a dictionary of unique users"""
    users = set()
    for _, element in ET.iterparse(filename):
        if element.tag in ["node", "way", "relation"]:
            if not element.attrib['uid'] in users:
                users.add(element.attrib['uid'])

    return users


def test(dataset):
    """Perform the test on the selected dataset"""
    print("Running 3_count_unique_users.py")
    users = set()
    
    # Run against the sample or the full data?
    if dataset == "sample":
        users = process_map(SAMPLE_PATH)
    else:
        users = process_map(DATA_PATH)
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as fo:
        pprint.pprint(users, fo)


if __name__ == "__main__":
    dataset = "full"
    if len(sys.argv) > 1:
        dataset = sys.argv[1]
        
    test(dataset)