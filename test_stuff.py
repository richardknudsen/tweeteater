import pytest
from lib.eat_tweets import *
from lib.eat_engagements import *
from lib.utils import *


def test_get_tweettypes():
    tweets = [{'retweeted_status': {'id': 1}, 'in_reply_to_status_id': None},
              {'quoted_status': {'id': 1}, 'in_reply_to_status_id': None},
              {'in_reply_to_status_id': None},
              {'in_reply_to_status_id': 1, 'quoted_status': {'id': 1}}]
    tweettypes_true = [set(['retweet']), set(['quote']), set(['original']), set(['reply', 'quote'])]
    tweets = map(get_tweettypes, tweets)
    tweettypes_test = list(map(lambda tweet: tweet.get('tweettypes'), tweets))
    assert tweettypes_test == tweettypes_true


def test_get_attributes():
    attributes = ['1', '2.2']
    tweet = {'1': 1, '2': {'2': 2}, 'id': 11}
    assert get_attributes(tweet, attributes) == ([1, 2])


def test_eat_tweets():
    directory = 'test_data'
    extension = '.jsonl'
    filepaths = get_filepaths(directory, extension)
    n_filepaths = len(list(get_filepaths(directory, extension)))
    attributes = ['created_at', 'user.screen_name']
    subset_func = lambda tweet: True
    keep_tweettypes = ['original', 'retweet', 'reply', 'quote']
    tweets = eat_tweets(filepaths, attributes, keep_tweettypes=keep_tweettypes,
                                 subset_func=subset_func, n_filepaths=n_filepaths)
    assert list(tweets) == load_pickle('test_data/test_tweets.pickle')


def test_get_engagements():
    ids = [2, 3]
    tweet1 = {'id': 1,
              'created_at': '01',
              'retweeted_status': {'id': 2, 'favorite_count': 3, 'retweet_count': 4},
              'in_reply_to_status_id': None}
    tweet2 = {'id': 1,
              'created_at': '01',
              'retweeted_status': {'id': 0, 'favorite_count': 3, 'retweet_count': 4},
              'in_reply_to_status_id': None}
    tweet3 = {'id': 4,
              'created_at': '01',
              'quoted_status_id': 2,
              'quoted_status': {'id': 2, 'favorite_count': 7, 'retweet_count': 8},
              'in_reply_to_status_id': 3}
    assert get_engagements(get_tweettypes(tweet1), ids=ids) == [('01', 1, 2, 'favourite_count', 3),
                                                                ('01', 1, 2, 'retweet_count', 4)]
    assert get_engagements(get_tweettypes(tweet2), ids=ids) == []
    assert get_engagements(get_tweettypes(tweet3), ids=ids) == [('01', 4, 2, 'favourite_count', 7),
                                                                ('01', 4, 2, 'retweet_count', 8),
                                                                ('01', 4, 2, 'quote', 1),
                                                                ('01', 4, 3, 'reply', 1)]
