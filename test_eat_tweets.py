import pytest
from eat_tweets import *
from utils import *


def test_eat_tweettypes():
    directory = 'test_data'
    extension = '.jsonl'
    filepaths = get_filepaths(directory, extension)
    n_filepaths = len(list(get_filepaths(directory, extension)))
    subset_func = lambda tweet: True
    tweets = dict(eat_tweettypes(filepaths, subset_func=subset_func, n_filepaths=n_filepaths))
    assert tweets == load_pickle('test_data/tweets.pickle')


def test_get_attributes():
    attributes = ['1', '2.2']
    tweet = {'1': 1, '2': {'2': 2}, 'id': 11}
    assert get_attributes(tweet, attributes) == (tweet, [1, 2])


def test_eat_tweetattributes():
    directory = 'test_data'
    extension = '.jsonl'
    filepaths = get_filepaths(directory, extension)
    n_filepaths = len(list(get_filepaths(directory, extension)))
    ids = [id_ for id_, types in load_pickle('test_data/tweets.pickle').items()]
    attributes = ['created_at', 'user.screen_name']
    tweet_attributes = eat_tweetattributes(filepaths, ids, attributes, n_filepaths=n_filepaths)
    assert dict(tweet_attributes) == load_pickle('test_data/tweets_attributes.pickle')
