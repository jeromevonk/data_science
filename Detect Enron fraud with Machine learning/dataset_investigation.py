#-------------------------------------------------------------------------------
# Name:        Investigation on Enron dataset
# Purpose:     Auxiliar script for the final project. Used to peform some investigations
#              on the dataset and features
#
# Author:      Jerome Vonk
#
# Created:     02/04/2018
#-------------------------------------------------------------------------------

#!/usr/bin/python

def exploreFeature(feature):
    for key in enron_data.keys():
        print enron_data[key][feature]


def plotFeature(name, data):
    import matplotlib.pyplot as plt
    plt.hist(data)
    plt.xlabel(name)
    #plt.show()
    plt.savefig("{}.png".format(name))
    plt.clf()


def computeFraction( poi_messages, all_messages ):
    """ compute the fraction of messages to/from a person that are from/to a POI """
    fraction = 0

    if poi_messages == 'NaN' or all_messages == 'NaN':
        fraction = 'NaN'
    else:
        fraction = float(poi_messages)/all_messages

    return fraction

import sys
import pickle
sys.path.append("../tools/")


### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    enron_data = pickle.load(data_file)


# How many persons?
print 'Number of persons: ', len(enron_data)
for person in enron_data:
    #print person
    pass

# For each person, how many features?
features_names = []
print "List of features:"
for person in  enron_data:
    for feature, feature_value in enron_data[person].iteritems():
        features_names.append(feature)
    break
print "Number of features: ", len(features_names)
print features_names

# How many persons of interest?
count_poi = 0
for person in enron_data:
        if enron_data[person]["poi"] == 1:
            count_poi += 1
print "Persons of interest: ", count_poi
print "Non-POIs: ", len(enron_data) - count_poi


# Missing?

for feature in features_names:
    print "NaN percentage for ", feature, " :", round(float(sum([1 for key in enron_data.keys() if enron_data[key][feature] == 'NaN']))/len(enron_data), 3)

# Is there someone with NaN for all features?
for person in enron_data:
    valid = False
    for feature, feature_value in enron_data[person].iteritems():
        if feature_value != 'NaN' and feature != 'poi':
            valid = True
            break
    if valid == False:
        print "Found someone with NaN for all values: ", person


# Plots
from feature_format import featureFormat, targetFeatureSplit
features_list = ['poi','salary', 'to_messages', 'deferral_payments', 'total_payments', 'exercised_stock_options', 'bonus', 'restricted_stock', 'shared_receipt_with_poi', 'restricted_stock_deferred', 'total_stock_value', 'expenses', 'loan_advances', 'from_messages', 'other', 'from_this_person_to_poi', 'poi', 'director_fees', 'deferred_income', 'long_term_incentive', 'from_poi_to_this_person']
data = featureFormat(enron_data, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

#for i in range(1, len(features_list)):
    #plotFeature(features_list[i], features[i-1] )


# Negative salary?
import numpy as np
np_features =  np.array(features)

import pprint
#pprint.pprint(np_features[:,0])


# Pandas
import pandas as pd
df = pd.DataFrame.from_dict(enron_data, orient = 'index')

subzero = df[df < 0]
print len(subzero)


#for person in enron_data:
#    for feature, feature_value in enron_data[person].iteritems():
#        if feature_value != 'NaN' and feature_value < 0:
#            print person, feature, feature_value


# As seen in class, we will compute the fraction of exchanged messages with POIs over the total messages
for name in enron_data:
    person_dict = enron_data[name]

    fraction_from_poi =  computeFraction(person_dict['from_poi_to_this_person'], person_dict['to_messages'])
    #print fraction_from_poi
    person_dict["fraction_from_poi"] = fraction_from_poi

    fraction_to_poi =  computeFraction(person_dict['from_this_person_to_poi'], person_dict['from_messages'])
    #print fraction_to_poi
    person_dict["fraction_to_poi"] = fraction_to_poi


for feature in ["fraction_from_poi", "fraction_to_poi"]:
    print "NaN percentage for ", feature, " :", round(float(sum([1 for key in enron_data.keys() if enron_data[key][feature] == 'NaN']))/len(enron_data), 3)