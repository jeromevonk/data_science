#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Udacity Data Science For Business Nanodegree
Part 1: Data wrangling
Project: Wrangle OpenStreetMap Data
Student: Jerome Vergueiro Vonk

Script: create_database.py
Goal: inserto into mongodb database reading from json file

"""
# -----------------------------------------------------------------------------------------------------------------------------------
# This apparently can be done much faster using the 'mongoimport' deamon on the local machine
# cd C:\Dropbox\Lelo\Trabalho\Skills\Data Science\_github\Wrangling OSM data for Madrid\3. Preparing_database\output
# "C:\Program Files\MongoDB\Server\3.6\bin\mongoimport.exe" --db Madrid --collection nodes_ways --drop --file nodes_and_ways.json
# -----------------------------------------------------------------------------------------------------------------------------------
import json

def create_database():
    """Create database from the json file"""

    # Connect to database
    from pymongo import MongoClient
    try:
        client = MongoClient('localhost:27017')
    except:
        print("Could not connect to MongoDB")
        return

    # Database will be called Madrid
    db = client.Madrid

    # Collection will be called nodes_ways
    collection = db.nodes_ways

    with open('..\\3. Preparing_database\\output\\nodes_and_ways.json') as file:
        for line in file:

            # Convert from json to python format
            collection.insert(json.loads(line))

    print("Collection now has {} documents".format(collection.count() ) )


if __name__ == '__main__':
    #print("Running create_database_mongodb.py")
    create_database()


