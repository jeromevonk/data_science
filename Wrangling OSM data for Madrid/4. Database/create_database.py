#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Udacity Data Science For Business Nanodegree
Part 1: Data wrangling
Project: Wrangle OpenStreetMap Data
Student: Jerome Vergueiro Vonk

Script: create_database.py
Goal: inserto into database reading from csv files

Reference: https://docs.python.org/2/library/sqlite3.html
"""

import csv, sqlite3, os


NODES_PATH     = "..\\3. Preparing_database\\output\\nodes.csv"
NODE_TAGS_PATH = "..\\3. Preparing_database\\output\\nodes_tags.csv"
WAYS_PATH      = "..\\3. Preparing_database\\output\\ways.csv"
WAY_NODES_PATH = "..\\3. Preparing_database\\output\\ways_nodes.csv"
WAY_TAGS_PATH  = "..\\3. Preparing_database\\output\\ways_tags.csv"

def create_database():
    """Create database from the csv files"""

    # If database already exists, delete it
    try:
        os.remove("madrid.db")
    except:
        pass

    # Connect to database
    conn = sqlite3.connect("madrid.db")

    # Create a cursor
    c = conn.cursor()

    # --------------------------------------------------------
    # Create and populate the nodes table
    # --------------------------------------------------------
    c.execute('''CREATE TABLE nodes
               (node_id INTEGER PRIMARY KEY,
                lat REAL,
                lon REAL,
                user TEXT,
                uid INTEGER,
                version INTEGER,
                changeset INTEGER,
                timestamp TEXT)''')


    # Populate with the csv file
    with open(NODES_PATH, 'r', encoding="utf-8") as csv_file:
        reader = csv.DictReader (csv_file, delimiter=',')
        to_db = [(i['id'], i['lat'], i['lon'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp']) for i in reader]

    # Insert the rows
    c.executemany("INSERT INTO nodes VALUES (?, ?, ?, ?, ?, ?, ?, ?);", (to_db))


    # --------------------------------------------------------
    # Create and populate the node_tags table
    # --------------------------------------------------------
    c.execute('''CREATE TABLE node_tags
               (node_id INTEGER NOT NULL,
                key TEXT,
                value TEXT,
                type TEXT,
                FOREIGN KEY (node_id) REFERENCES nodes(node_id))''')


    # Populate with the csv file
    with open(NODE_TAGS_PATH, 'r', encoding="utf-8") as csv_file:
        reader = csv.DictReader (csv_file, delimiter=',')
        to_db = [(i['id'], i['key'], i['value'], i['type'], ) for i in reader]

    # Insert the rows
    c.executemany("INSERT INTO node_tags VALUES (?, ?, ?, ?);", (to_db))


    # --------------------------------------------------------
    # Create and populate the ways table
    # --------------------------------------------------------
    c.execute('''CREATE TABLE ways
               (way_id INTEGER PRIMARY KEY,
                user TEXT,
                uid INTEGER,
                version INTEGER,
                changeset INTEGER,
                timestamp TEXT)''')


    # Populate with the csv file
    with open(WAYS_PATH, 'r', encoding="utf-8") as csv_file:
        reader = csv.DictReader (csv_file, delimiter=',')
        to_db = [(i['id'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp']) for i in reader]

    # Insert the rows
    c.executemany("INSERT INTO ways VALUES (?, ?, ?, ?, ?, ?);", (to_db))

    # --------------------------------------------------------
    # Create and populate the way_nodes table
    # --------------------------------------------------------
    c.execute('''CREATE TABLE way_nodes
               (way_id INTEGER NOT NULL,
                node_id INTEGER,
                position INTEGER,
                FOREIGN KEY (way_id) REFERENCES ways(way_id),
                FOREIGN KEY (node_id) REFERENCES nodes(node_id))''')


    # Populate with the csv file
    with open(WAY_NODES_PATH, 'r', encoding="utf-8") as csv_file:
        reader = csv.DictReader (csv_file, delimiter=',')
        to_db = [(i['id'], i['node_id'], i['position'] ) for i in reader]

    # Insert the rows
    c.executemany("INSERT INTO way_nodes VALUES (?, ?, ?);", (to_db))

    # --------------------------------------------------------
    # Create and populate the way_tags table
    # --------------------------------------------------------
    c.execute('''CREATE TABLE way_tags
               (way_id INTEGER NOT NULL,
                key TEXT,
                value TEXT,
                type TEXT,
                FOREIGN KEY (way_id) REFERENCES ways(way_id))''')


    # Populate with the csv file
    with open(WAY_TAGS_PATH, 'r', encoding="utf-8") as csv_file:
        reader = csv.DictReader (csv_file, delimiter=',')
        to_db = [(i['id'], i['key'], i['value'], i['type'], ) for i in reader]

    # Insert the rows
    c.executemany("INSERT INTO way_tags VALUES (?, ?, ?, ?);", (to_db))

    # Save (commit) the changes
    conn.commit()

    # Now, close the connection
    conn.close()


if __name__ == '__main__':
    print("Running create_database.py")
    create_database()