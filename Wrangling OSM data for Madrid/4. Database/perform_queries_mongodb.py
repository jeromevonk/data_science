#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Udacity Data Science For Business Nanodegree
Part 1: Data wrangling
Project: Wrangle OpenStreetMap Data
Student: Jerome Vergueiro Vonk

Script: perform_queries_mongodb.py
Goal: perform queries on the database

Reference: https://docs.python.org/2/library/sqlite3.html
"""

import os

def aggregate(collection, pipeline, file_path):
    """Perfom an aggregation  and save the output in a json file"""
    result =  [doc for doc in collection.aggregate(pipeline)]

    import pprint
    pprint.pprint(result)

    import json
    with open(file_path, 'w') as outfile:
        json.dump(result, outfile)

def perform_queries():
    """Perfom a list of queries on the database"""

    # Connect to database
    from pymongo import MongoClient
    try:
        client = MongoClient('localhost:27017')
    except:
        print("Could not connect to MongoDB")
        return

    # Database is called Madrid
    db = client.Madrid

    # Collection is called nodes_ways
    collection = db.nodes_ways

    # Make sure the output directory exists
    os.makedirs(os.path.dirname("queries\\"), exist_ok=True)

    # --------------------------------------------------------
    # Perform the desired queries
    # --------------------------------------------------------

    # Retrieve the users that appear the most
    pipeline = [ { "$match"  : { "type": {"$eq" : "node" } } },
                 { "$group"  : { "_id" : "$created.user", "count": {"$sum" : 1}, "uid": {"$addToSet" : "$created.uid"}  } },
                 { "$sort"   : { "count" : -1 } },
                 { "$limit"  : 10 } ]

    #aggregate(collection, pipeline, "queries\\users.json")


    # What type of cuisine appears the most
    pipeline = [ { "$match"  : { "type": {"$eq" : "node" } } },
                 { "$match"  : { "cuisine": {"$exists" : True } } },
                 { "$group"  : { "_id" : "$cuisine", "count": {"$sum" : 1}  } },
                 { "$sort"   : { "count" : -1 } },
                 { "$limit"  : 10 } ]

    #aggregate(collection, pipeline, "queries\\cuisine.json")

    # What postcode appears the most
    pipeline = [ { "$match"  : { "type": {"$eq" : "way" } } },
                 { "$match"  : { "address.postcode": {"$exists" : True } } },
                 { "$group"  : { "_id" : "$address.postcode", "count": {"$sum" : 1}  } },
                 { "$sort"   : { "count" : -1 } },
                 { "$limit"  : 10 } ]

    aggregate(collection, pipeline, "queries\\postcode.json")



if __name__ == '__main__':
    print("Running perform_queries_mongodb.py")
    perform_queries()