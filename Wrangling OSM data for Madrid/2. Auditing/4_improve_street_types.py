#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Udacity Data Science For Business Nanodegree
Part 1: Data wrangling
Project: Wrange OpenStreetMap Data
Student: Jerome Vergueiro Vonk

Script: 4_improve_street_types.py
Goal: audit data to figure out what needs fixing regarding unexpected street types and write a function to perform the changes

REFERENCE: street types in Spain found in https://administracionelectronica.gob.es/ctt/resources/Soluciones/238/Area%2520descargas/Catalogo%2520de%2520Tipos%2520de%2520Via.xlsx
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import os
import sys

DATA_PATH   = "..\\1. Data\\Full\\Madrid_custom_11122017.osm"
SAMPLE_PATH = "..\\1. Data\\Sample\\Madrid_custom_11122017_sample_1.osm"

OUTPUT_FILE = "output\\4_improve_street_types.txt"

street_type_re = re.compile(r'^[^\s]+', re.IGNORECASE)

expected = ["Calle", "Plaza", "Avenida", "Vía", "Alameda", "Camino", "Pasaje", "Paseo", "Rambla",
            "Travesía", "Carrera", "Carretera", "Ronda", "Cuesta", "Glorieta", "Costanilla",
            "Callejón", "Bulevar", "Corredera", "Gran", "Acceso", "Autovía", "Puerta", "Urbanización"]


mapping = { "CL": "Calle", "C/": "Calle", "calle": "Calle",
            "AUTOP.": "Autopista", "Avda.": "Avenida", "Via": "Vía",  "plaza": "Plaza", 
            "CR": "Carrera", "CTRA.": "Carretera", "Ctra": "Carretera"
           }


def audit_street_type(street_types, street_name):
    """Audits the street type according to expected values"""
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    """Returns true if the element attribute is a street name"""
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    """Returns a dictionary containing all the street types in the data file"""
    osm_file = open(osmfile, "r", encoding="utf8")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    """Makes an improvement in the address (name) according to the dictionary (mapping)"""
    m = street_type_re.search(name)
    not_good_type = m.group()
    
    try:
        name = name.replace(not_good_type, mapping[not_good_type])
        return name
    except: 
        return False


def test(dataset):
    """Perform the test on the selected dataset """
    print("Running 4_improve_street_types.py")
    st_types = defaultdict(set)
    
    # Run against the sample or the full data?
    if dataset == "sample":
        st_types = audit(SAMPLE_PATH)
    else:
        st_types = audit(DATA_PATH)
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as fo:
        pprint.pprint(dict(st_types), fo)
        
        # Modify street names
        for st_type, ways in st_types.items():
            for name in ways:
                better_name = update_name(name, mapping)
                if better_name:
                    fo.write("{} => {}\n".format(name,  better_name))
                else:
                    fo.write("Not fixed: {}\n".format(name))

if __name__ == '__main__':
    dataset = "full"
    if len(sys.argv) > 1:
        dataset = sys.argv[1]
        
    test(dataset)