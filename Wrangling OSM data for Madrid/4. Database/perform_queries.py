#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Udacity Data Science For Business Nanodegree
Part 1: Data wrangling
Project: Wrange OpenStreetMap Data
Student: Jerome Vergueiro Vonk

Script: perform_queries.py
Goal: perform queries on the database

Reference: https://docs.python.org/2/library/sqlite3.html
"""

import sqlite3
import csv
import os

def perform_query(cursor, columns, file_path, query):
    """Perfom a query and save the output in a csv file"""
    cursor.execute(query)
    results =  cursor.fetchall()
    
    # Save in a csv file
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(columns)
        for row in results:
            writer.writerow(row)
    

def perform_queries():
    """Perfom a list of queries on the database"""
    # Connect to database
    conn = sqlite3.connect("madrid.db")
    
    # Create a cursor
    cursor = conn.cursor()
    
    # Make sure the output directory exists
    os.makedirs(os.path.dirname("queries\\"), exist_ok=True)

    # --------------------------------------------------------
    # Perform all the queries we want
    # --------------------------------------------------------
    
    # Retrieve the users that appear the most
    results = perform_query(cursor, 
                            ["user", "id", "count"],
                            "queries\\users.csv",
                            "select user, uid, count(*) as count from nodes group by user order by count desc limit 10")
                            
    # What type of cuisine appears the most
    results = perform_query(cursor, 
                            ["cuisine", "count"],
                            "queries\\cuisine.csv",
                            "select value, count(*) as count from node_tags where key='cuisine' group by value order by count desc")                        

    # What type of cuisine appears the most
    results = perform_query(cursor, 
                            ["postcode", "count"],
                            "queries\\postcode.csv",
                            "select value, count(*) as count from way_tags where key='postcode' group by value order by count desc")                                                        

    # Now, close the connection
    conn.close()


if __name__ == '__main__':
    print("Running perform_queries.py")
    perform_queries()