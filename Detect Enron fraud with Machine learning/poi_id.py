#-------------------------------------------------------------------------------
# Name:        POI Identification on Enron dataset
#
# Author:      Jerome Vonk
#
# Created:     02/04/2018
#-------------------------------------------------------------------------------

#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data, test_classifier

def computeFraction( poi_messages, all_messages ):
    """ compute the fraction of messages to/from a person that are from/to a POI """
    fraction = 0

    if poi_messages == 'NaN' or all_messages == 'NaN':
        fraction = 0
    else:
        fraction = float(poi_messages)/all_messages

    return fraction



# This variable will hold the best classifier found
best_classifier = None

### Task 1: Select what features you'll use.

# For starters, I'll keep almost all features (getting rid of e-mail address, only)
# because I'll use an univariate feature selection routine which will hopefully select
# the most relevant features

features_list = ['poi','salary', 'to_messages', 'deferral_payments', 'total_payments',
                 'exercised_stock_options', 'bonus', 'restricted_stock', 'shared_receipt_with_poi',
                 'restricted_stock_deferred', 'total_stock_value', 'expenses', 'loan_advances',
                 'from_messages', 'other', 'from_this_person_to_poi',  'director_fees',
                 'deferred_income', 'long_term_incentive', 'from_poi_to_this_person']

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
# These are either found by manually examining the rows or looping by the features.
# See "dataset_investigation.py"
data_dict.pop("LOCKHART EUGENE E", 0)             # Has all the features (besided poi) equal to 'NaN'
data_dict.pop("TOTAL", 0 )                        #  As seen in the class, this is a sum of financial data
data_dict.pop("THE TRAVEL AGENCY IN THE PARK", 0) # Does not look like a person


### Task 3: Create new feature(s) |  Store to my_dataset for easy export below.
my_dataset = data_dict

# As seen in class, we will compute the fraction of exchanged messages with POIs over the total messages
for name in my_dataset:
    person_dict = my_dataset[name]

    fraction_from_poi =  computeFraction(person_dict['from_poi_to_this_person'], person_dict['to_messages'])
    person_dict["fraction_from_poi"] = fraction_from_poi

    fraction_to_poi =  computeFraction(person_dict['from_this_person_to_poi'], person_dict['from_messages'])
    person_dict["fraction_to_poi"] = fraction_to_poi

features_list.append('fraction_from_poi')
features_list.append('fraction_to_poi')

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)


# Feature selection
from sklearn.feature_selection import SelectPercentile, SelectKBest, f_classif, chi2
selector = SelectKBest(f_classif, k=10)
selector.fit(features, labels)
selected_features_Kbest_10 = selector.transform(features)

# Create a new features_list with the 10 selected from Kbest
support = selector.get_support(indices=True)
features_list_Kbest_10 = ['poi']
for i in support:
    features_list_Kbest_10.append(features_list[i+ 1] ) # + 1 because "poi" is the first on that list

### Task 4: Try a varity of classifiers

'''from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()

# Classifier 1: |Naive Bayes|   Accuracy: 0.82213	Precision: 0.3255	Recall: 0.3115
from sklearn.naive_bayes import GaussianNB
clf_GNB = GaussianNB()

# Classifier 2: |SVM|   Accuracy: 0.78660	Precision: 0.19347	Recall: 0.18950
from sklearn.svm import SVC
clf_SVC = SVC(kernel = 'rbf', C = 100000)
#clf_SVC = SVC(kernel = 'linear')

# Classifier 3: |Decision Tree|   Accuracy: 0.8228	Precision: 0.32847	Recall: 0.315
from sklearn.tree import DecisionTreeClassifier
clf_dt = DecisionTreeClassifier()

# Classifier 4: |KNeighbors|   Accuracy: 0.86707	Precision: 0.50308	Recall: 0.245
from sklearn.neighbors import KNeighborsClassifier
clf_KN = KNeighborsClassifier(n_neighbors = 3)

# Classifier 5: |AdaBoost|    Accuracy: 0.83827	Precision: 0.36329	Recall: 0.283
from sklearn.ensemble import AdaBoostClassifier
clf_ada = AdaBoostClassifier(n_estimators=50)

# Classifier 6: |RandomForest|  Accuracy: 0.86633	Precision: 0.49417	Recall: 0.106
from sklearn.ensemble import RandomForestClassifier
clf_rf = RandomForestClassifier(max_depth=2, random_state=0)


# Construct a pipeline
from sklearn.pipeline import Pipeline
#steps = [('MinMaxScaler', scaler), ('Classifier', clf_SVC)]
steps = [('Classifier', clf_ada)]
pipe = Pipeline(steps)

# Test the classifier
test_classifier(pipe, my_dataset, features_list_Kbest_10) '''

# I tried 6 classifiers, without tunning the parameters much.
# RandomForest showed the best accuracy, but Decision Tree showed a better ballance
# between precision and recall (both above 0.3, which is what we are looking for



### Task 5: Tune your classifier to achieve better than .3 precision and recall using testing script
# ----------------------------------------------------------------------------------------------------
# Naive bayes does not have attributes to be tunned, but we can try with different number of features
# ----------------------------------------------------------------------------------------------------
'''for num_feat in range(2, len(features_list)):

    # Select features
    selector = SelectKBest(f_classif, k=num_feat)
    selector.fit(features, labels)
    selected_features = selector.transform(features)

    # Get the selected features
    features_list_exaustive = ['poi']
    support = selector.get_support(indices=True)
    print support
    for i in support:
        features_list_exaustive.append(features_list[i+ 1] ) # + 1 because "poi" is the first on that list
    print features_list_exaustive

    # Apply Naive Bayes algorithm
    clf_GNB = GaussianNB()
    test_classifier(clf_GNB, my_dataset, features_list_exaustive)'''
# -------------------------------------------------------------------------------------
# The best result was found by Naive Bayes with 6 features, so let's save
# the classifier and the features list
# -------------------------------------------------------------------------------------

# Select features
selector = SelectKBest(f_classif, k=6)
selector.fit(features, labels)
selected_features = selector.transform(features)

# Get the selected features
features_list_exaustive = ['poi']
support = selector.get_support(indices=True)
for i in support:
    features_list_exaustive.append(features_list[i+ 1] ) # + 1 because "poi" is the first on that list

# Apply Naive Bayes algorithm
from sklearn.naive_bayes import GaussianNB
best_classifier = GaussianNB()
#test_classifier(best_classifier, my_dataset, features_list_exaustive)

# -------------------------------------------------------------------------------------
# Try tunning Decision Trees
# -------------------------------------------------------------------------------------
'''from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
param_grid = {'criterion': ['gini', 'entropy'],
              'min_samples_split': [2, 10],
              'max_features' : [6, 8, 10] }
grid = GridSearchCV( DecisionTreeClassifier(random_state=0), param_grid, scoring = 'f1')

# Train the algorithm
grid.fit(selected_features_Kbest_10, labels)

# Test the classifier with the given test function from testerp.y, which uses
# cross-validation techniques
test_classifier(grid.best_estimator_, my_dataset, features_list)'''


### Task 6: Dump your classifier, dataset, and features_list so anyone can check your results.
dump_classifier_and_data(best_classifier, my_dataset, features_list_exaustive)