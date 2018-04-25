#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Udacity Data Science For Business Nanodegree
Part 1: Data wrangling
Project: Wrangle OpenStreetMap Data
Student: Jerome Vergueiro Vonk

Script: preparing_database.py
Goal: prepare the data to be inserted into a MongoDB database


"""
import os
import sys
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import json

DATA_PATH   = "..\\1. Data\\Full\\Madrid_custom_11122017.osm"
SAMPLE_PATH = "..\\1. Data\\Sample\\Madrid_custom_11122017_sample_1.osm"

OUTPUT_FILE    = "output\\nodes_and_ways.json"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
POS =  ['lat', 'lon']



# This mapping/expected dictionaries and the regular expression come from script '4_improve_street_types.py'
street_type_re = re.compile(r'^[^\s]+', re.IGNORECASE)
mapping = { "CL": "Calle", "C/": "Calle", "calle": "Calle", "CALLE": "Calle",
            "AUTOP.": "Autopista", "Avda.": "Avenida", "Via": "Vía",  "plaza": "Plaza",
            "CR": "Carrera", "CTRA.": "Carretera", "Ctra": "Carretera", "Pasage":"Pasaje"
           }

expected = ["Calle", "Plaza", "Avenida", "Vía", "Alameda", "Camino", "Pasaje", "Paseo", "Rambla",
            "Travesía", "Carrera", "Carretera", "Ronda", "Cuesta", "Glorieta", "Costanilla",
            "Callejón", "Bulevar", "Corredera", "Gran", "Acceso", "Autovía", "Puerta", "Urbanización"]

# Count how many addresses we were able to fix the street type
improved_address = 0

def is_street_name(elem):
    """Returns true if the element attribute is a street name"""
    return (elem.attrib['k'] == "addr:street")

def is_postal_code(elem):
    """Returns true if the element attribute is a postal code"""
    return (elem.attrib['k'] == "addr:postcode")


def auditStreetType(secondary):
    """Audit the street type, according to expected street types dictionary"""
    global improved_address
    improved_street_type = ""

    m = street_type_re.search(secondary.attrib['v'])
    if m:
        street_type = m.group()

        if street_type in expected:
            # Street type is what we expect, all good here
            improved_street_type = secondary.attrib['v']
        else:
            # Try to improve the street type
            try:
                improved_street_type = secondary.attrib['v'].replace(street_type, mapping[street_type])
                improved_address += 1
                #print("Corrected \'{}\' to \'{}\'".format(secondary.attrib['v'], improved_street_type) )

            except BaseException as e:
                # We could't fix this by automation
                improved_street_type = secondary.attrib['v']
                #print("Do not know how to fix '{}\'".format(secondary.attrib['v']))
    else:
        print("Should not get there")
        improved_street_type = "error"

    return improved_street_type


def auditPostalCode(secondary):
    """Audit the postal code (for Madrid, must be between 28000 and 29000)"""
    global improved_address
    improved_postcode = 0

    try:
        postcode = int(secondary.attrib['v'])
        if postcode >= 28000 and postcode <= 28999:
            improved_postcode = secondary.attrib['v']
            return True, improved_postcode
        elif postcode == 2839:
            # This has been added after examining the output on the first run
            #print("Correcting '2839' to '28039'")
            improved_postcode = "28039"
            improved_address += 1
            return True, improved_postcode
        else:
            #print("Postal code looks invalid: ", postcode)
            return False, improved_postcode
    except:
        if secondary.attrib['v'] == "E28016":
            # This has been added after examining the output on the first run
            #print("Correcting 'E28016' to '28016'")
            improved_postcode = "28016"
            improved_address += 1
            return True, improved_postcode
        else:
            #print("Postal is not a number: ", secondary.attrib['v'])
            return False, improved_postcode



def shape_element(element):
    node = {}
    node['address'] = {}
    node['node_refs'] = []

    if element.tag == "node" or element.tag == "way":
        # ----------------------------------------------------------------
        # First, we deal with the element attributes
        # ----------------------------------------------------------------

        # The type of the the elements
        node['type'] = element.tag

        # Copy the following attributes under the key "created"
        node['created'] = {}
        for item in CREATED:
            node["created"][item] = element.attrib[item]

        # Attributes for latitude and longitude should be added to a "pos" array
        try:
            node["pos"] = [float(element.attrib['lat']), float(element.attrib['lon']) ]
        except:
            pass


        # Copy the rest
        for item in element.attrib:
            if item not in CREATED and item not in POS:
                node[item] = element.attrib[item]

        # Now, let's deal with secondary attributes (if any)

        # ----------------------------------------------------------------
        # Do we have secondary tags?
        # ----------------------------------------------------------------
        for secondary in element:
            if secondary.tag == "tag":
                # If the tag "k" value contains problematic characters, the tag should be ignored
                if PROBLEMCHARS.search(secondary.attrib['k']):
                    pass
                # If the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
                elif secondary.attrib['k'].startswith("addr:"):
                    _, key = secondary.attrib['k'].split(":", 1)
                    if ':' in key:
                        #if there is a second ":" that separates the type/direction of a street, the tag should be ignored
                        pass
                    else:
                        # Audit
                        if is_street_name(secondary):
                            node["address"][key] = auditStreetType(secondary)
                        elif is_postal_code(secondary):
                            bValid, improved_postcode = auditPostalCode(secondary)
                            if bValid:
                                node["address"][key] = improved_postcode
                            else:
                                # Postcode turned out to be invalid, so ignore it
                                pass
                        else:
                            node["address"][key] = secondary.attrib['v']
                elif ':' in secondary.attrib['k']:
                    # If the second level tag "k" value does not start with "addr:",
                    # but contains ":", you can process it in a way that you feel is best
                    before_colon, after_colon = secondary.attrib['k'].split(":", 1)
                    before_colon += "_"
                    if before_colon not in node:
                         node[before_colon] = {}

                    node[before_colon][after_colon] = secondary.attrib['v']
                else:
                    node[secondary.attrib['k']] = secondary.attrib['v']

            elif secondary.tag == "nd":
                # For "way" specifically
                if secondary.tag == "nd":
                    node['node_refs'].append(secondary.attrib['ref'])

        # Check for empty containers
        if 0 == len(node['address'].keys()):
            node.pop('address', None)

        if 0 == len(node['node_refs']):
            node.pop('node_refs', None)

        return node
    else:
        return None


def process_map(file_in, pretty = False):
    """Iteratively process each XML element and write to json"""
    # The pretty=True option adds additional spaces
    # to the output, making it significantly larger
    with codecs.open(OUTPUT_FILE, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")


def prepare_database(dataset):
    """Process all the information and write .csv files to be imported into database"""
    # Run against the sample or the full data?
    if dataset == "sample":
        process_map(SAMPLE_PATH)
    else:
        process_map(DATA_PATH)

if __name__ == '__main__':
    print("Running preparing_database_mongodb.py")

    dataset = "full"
    if len(sys.argv) > 1:
        dataset = sys.argv[1]

    prepare_database(dataset)

    print("{} address(es) were improved".format(improved_address))
