#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Udacity Data Science For Business Nanodegree
Part 1: Data wrangling
Project: Wrangle OpenStreetMap Data
Student: Jerome Vergueiro Vonk

Script: preparing_database.py
Goal: prepare the data to be inserted into a SQL database


"""
import os
import sys
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus
import schema

DATA_PATH   = "..\\1. Data\\Full\\Madrid_custom_11122017.osm"
SAMPLE_PATH = "..\\1. Data\\Sample\\Madrid_custom_11122017_sample_1.osm"

NODES_PATH     = "output\\nodes.csv"
NODE_TAGS_PATH = "output\\nodes_tags.csv"
WAYS_PATH      = "output\\ways.csv"
WAY_NODES_PATH = "output\\ways_nodes.csv"
WAY_TAGS_PATH  = "output\\ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS      = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS       = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS  = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

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


def auditStreetType(secondary, secondary_dic):
    """Audit the street type, according to expected street types dictionary"""
    global improved_address
    m = street_type_re.search(secondary.attrib['v'])
    if m:
        street_type = m.group()

        if street_type in expected:
            # Street type is what we expect, all good here
            secondary_dic['value'] = secondary.attrib['v']
        else:
            # Try to improve the street type
            try:
                secondary_dic['value'] = secondary.attrib['v'].replace(street_type, mapping[street_type])
                improved_address += 1
                #print("Corrected \'{}\' to \'{}\'".format(secondary.attrib['v'], secondary_dic['value']) )

            except BaseException as e:
                # We could't fix this by automation
                secondary_dic['value'] = secondary.attrib['v']
                #print("Do not know how to fix '{}\'".format(secondary.attrib['v']))


def auditPostalCode(secondary, secondary_dic):
    """Audit the postal code (for Madrid, must be between 28000 and 29000)"""
    global improved_address
    try:
        postcode = int(secondary.attrib['v'])
        if postcode >= 28000 and postcode <= 28999:
            secondary_dic['value'] = secondary.attrib['v']
            return True
        elif postcode == 2839:
            # This has been added after examining the output on the first run
            #print("Correcting '2839' to '28039'")
            secondary_dic['value'] = "28039"
            improved_address += 1
            return True
        else:
            #print("Postal code looks invalid: ", postcode)
            return False
    except:
        if secondary.attrib['v'] == "E28016":
            # This has been added after examining the output on the first run
            #print("Correcting 'E28016' to '28016'")
            secondary_dic['value'] = "28016"
            improved_address += 1
            return True
        else:
            #print("Postal is not a number: ", secondary.attrib['v'])
            return False

def create_tags_dictionary(element, secondary):
    """Create a dictionary for the secondary tag that the element has"""
    secondary_dic = {}

    # If the tag "k" value contains problematic characters, the tag should be ignored
    m = PROBLEMCHARS.search(secondary.attrib['k'])
    if m:
        print("Found a problem with \'k\' value: ", secondary.attrib['k'])
        return None

    # If the tag "k" value contains a ":" the characters before the ":" should be set as the tag type
    # and characters after the ":" should be set as the tag key
    m = LOWER_COLON.search(secondary.attrib['k'])
    if m:
        secondary_dic['type'], secondary_dic['key'] = secondary.attrib['k'].split(":", 1)
    else:
        secondary_dic['type'] = "regular"
        secondary_dic['key']  = secondary.attrib['k']

    # Value: the tag "v" attribute value
    if not is_street_name(secondary):

        if not is_postal_code(secondary):
            secondary_dic['value'] = secondary.attrib['v']
        else:
            # If it is a postcode, let's check if the postcode looks legit (for Madrid, must have 5 numbers and start with 28)
            if False == auditPostalCode(secondary, secondary_dic):
                # there's an invalid postal code, so let's ignore this tag
                return None
    else:
        # If this is a street name, let's audit the street type
        auditStreetType(secondary, secondary_dic)

    # The TOP LEVEL (so we use element, not secundary) node/way ID
    secondary_dic['id'] = element.attrib['id']

    return secondary_dic

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS, problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements


    if element.tag == 'node':

        # Fill the node attributes
        for item in NODE_FIELDS:
            node_attribs[item] = element.attrib[item]

        # Do we have secondary tags?
        for secondary in element:

            # Fill in the secondary tags
            if secondary.tag == "tag":

                # Create a dictionary for the secondary tag
                secondary_dic = create_tags_dictionary(element, secondary)

                # Check if tag was valid
                if secondary_dic ==  None:
                    continue

                # Add the secondary dictionary to the tags list
                tags.append(secondary_dic)

        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':

        # Fill the way fields
        for item in WAY_FIELDS:
            way_attribs[item] = element.attrib[item]

        # Do we have secondary tags?
        position = 0
        for secondary in element:

            # Fill in the secondary tags
            if secondary.tag == "tag":

                # Create a dictionary for the secondary tag
                secondary_dic = create_tags_dictionary(element, secondary)

                # Check if tag was validated
                if secondary_dic ==  None:
                    continue

                # Add the secondary dictionary to the tags list
                tags.append(secondary_dic)

            # This are the way nodes
            elif secondary.tag == "nd":

                # Create a dictionary for the child nodes
                child_nodes = {}

                # The TOP LEVEL (so we use element, not secundary) node/way ID
                child_nodes['id'] = element.attrib['id']

                # node_id: the ref attribute value of the nd tag
                child_nodes['node_id'] = secondary.attrib['ref']

                # position: the index starting at 0 of the nd tag i.e. what order the nd tag appears within the way element
                child_nodes['position'] = position
                position += 1

                # Add the child_nodes dictionary to the tags list
                way_nodes.append(child_nodes)

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.items())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))

def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    # Make sure the output directory exists
    os.makedirs(os.path.dirname(NODES_PATH), exist_ok=True)

    with open(NODES_PATH,     'w', encoding="utf-8", newline='') as nodes_file, \
         open(NODE_TAGS_PATH, 'w', encoding="utf-8", newline='') as nodes_tags_file, \
         open(WAYS_PATH,      'w', encoding="utf-8", newline='') as ways_file, \
         open(WAY_NODES_PATH, 'w', encoding="utf-8", newline='') as way_nodes_file, \
         open(WAY_TAGS_PATH,  'w', encoding="utf-8", newline='') as way_tags_file:

        # Create all DictWriter
        nodes_writer     = csv.DictWriter(nodes_file,      NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer      = csv.DictWriter(ways_file,       WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file,  WAY_NODES_FIELDS)
        way_tags_writer  = csv.DictWriter(way_tags_file,   WAY_TAGS_FIELDS)

        # Write all the headers
        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

def prepare_database(dataset, validate):
    """Process all the information and write .csv files to be imported into database"""
    # Run against the sample or the full data?
    if dataset == "sample":
        process_map(SAMPLE_PATH, validate)
    else:
        process_map(DATA_PATH, validate)

if __name__ == '__main__':
    # Note: Validation is ~ 10X slower.
    print("Running preparing_database.py")

    dataset = "full"
    if len(sys.argv) > 1:
        dataset = sys.argv[1]

    prepare_database(dataset, validate = False)

    print("{} address(es) were improved".format(improved_address))
