import pytest
from lib.eat_tweets import *
from lib.utils import *


def test_eat_tweettypes():
    directory = 'test_data'
    extension = '.jsonl'
    filepaths = get_filepaths(directory, extension)
    n_filepaths = len(list(get_filepaths(directory, extension)))
    subset_func = lambda tweet: True
    tweets = dict(eat_tweettypes(filepaths, subset_func=subset_func, n_filepaths=n_filepaths))
    assert tweets == load_pickle('test_data/tweettypes.pickle')


def test_get_attributes():
    attributes = ['1', '2.2']
    tweet = {'1': 1, '2': {'2': 2}, 'id': 11}
    assert get_attributes(tweet, attributes) == (tweet, [1, 2])


def test_eat_tweetattributes():
    directory = 'test_data'
    extension = '.jsonl'
    filepaths = get_filepaths(directory, extension)
    n_filepaths = len(list(get_filepaths(directory, extension)))
    ids = [id_ for id_, types in load_pickle('test_data/tweettypes.pickle').items()]
    attributes = ['created_at', 'user.screen_name']
    tweet_attributes = eat_tweetattributes(filepaths, ids, attributes, n_filepaths=n_filepaths)
    assert dict(tweet_attributes) == load_pickle('test_data/tweets_attributes.pickle')


def test_get_engagements():
    ids = [2, 3]
    tweet1 = {'id': 1,
              'retweeted_status': {'id': 2, 'favorite_count': 3, 'retweet_count': 4},
              'in_reply_to_status_id': None}

    tweet2 = {'id': 1,
              'retweeted_status': {'id': 0, 'favorite_count': 3, 'retweet_count': 4},
              'in_reply_to_status_id': None}
    tweet3 = {'id': 4,
              'quoted_status_id': 2,
              'quoted_status': {'id': 2, 'favorite_count': 7, 'retweet_count': 8},
              'in_reply_to_status_id': 3}
    assert get_engagements(get_tweettypes(tweet1), ids=ids) == [(1, 2, 'favourite_count', 3),
                                                                (1, 2, 'retweet_count', 4)]
    assert get_engagements(get_tweettypes(tweet2), ids=ids) == []
    assert get_engagements(get_tweettypes(tweet3), ids=ids) == [(4, 2, 'favourite_count', 7),
                                                                (4, 2, 'retweet_count', 8),
                                                                (4, 2, 'quote', 1),
                                                                (4, 3, 'reply', 1)]
