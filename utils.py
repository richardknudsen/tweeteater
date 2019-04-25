import os

def get_filepaths(directory, extension=None):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if extension == None or file.endswith(extension):
                yield os.path.join(root, file)


import pickle

def load_pickle(filepath):
    with open(filepath, 'rb') as file:
        return pickle.load(file)

def dump_pickle(filepath, object):
    with open(filepath, 'wb') as file:
        pickle.dump(object, file)