import pytest
from eat_tweets import *
from utils import *


def test_eat_tweettypes():
    directory = 'test_data'
    extension = '.jsonl'
    filepaths = get_filepaths(directory, extension)
    n_filepaths = len(list(get_filepaths(directory, extension)))
    subset_func = lambda tweet: True
    tweets = dict(eat_tweettypes(filepaths, extension=extension, n_filepaths=n_filepaths))
    assert tweets == load_pickle('test_data/tweets.pickle')