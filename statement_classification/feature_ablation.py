import os

# This script is for getting removing specific feature
def get_filter():
    with open(os.getcwd() + '/configuration', 'r') as f:
        for lines in f:
            feature_filter = lines.split()[2]
    return feature_filter