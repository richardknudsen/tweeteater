import json
import itertools
import functools
from tqdm import tqdm
##from more_itertools import ilen
from utils import *


def load_tweets_from_filepath(filepath):
    '''
    loads a single JSON tweet file where each line corresponds to a tweet

    :param str filepath: the filepath of the tweetfile
    :returns generator: generator containing the tweets as dicts
    '''
    with open(filepath, 'r') as file:
        tweets = (json.loads(line) for line in file.readlines())
    return tweets


def load_tweets_from_filepaths(filepaths, progressbar=False, n_filepaths=None):
    '''
    loads tweets from multiple file

    :param iterable filepaths: an iterable with the paths of the tweetfiles
    :param bool progressbar: whether to print progress, when True, this requires n_filepaths
    :param int n_filepaths: optional, if not None, this is used to print progress
    :returns itertool.chain object: generator-type containing the tweets as dicts
    '''
    assert not(progressbar == True and n_filepaths == None)
    if progressbar:
        return itertools.chain.from_iterable(map(load_tweets_from_filepath, tqdm(filepaths, total=n_filepaths)))
    else:
        return itertools.chain.from_iterable(map(load_tweets_from_filepath, filepaths))


def get_tweettypes(tweet):
    '''
    extract tweettypes of a tweet and returns tuple of (tweet id, set of types)

    :param dict-like tweet: tweet
    :returns tuple: (tweet id, set of types), e.g. (1, {'retweet'})
    '''
    tweettypes = set()
    if 'retweeted_status' in tweet:
        tweettypes.add('retweet')
    if tweet['in_reply_to_status_id'] != None:
        tweettypes.add('reply')
    if 'quoted_status' in tweet:
        tweettypes.add('quote')
    if len(tweettypes) == 0:
        tweettypes.add('original')
    return tweet.get('id'), tweettypes
#

def eat_tweettypes(filepaths, keep_tweettypes=['original', 'retweet', 'reply', 'quote'],
                   subset_func=lambda tweet: True, n_filepaths=None):
    '''
    reads tweets from JSONs, subsets by tweettypes as well as by custom function
    and returns tweet ID and types

    :param iterable filepaths: an iterable with the paths of the tweetfiles
    :param list keep_tweettypes: a list (or array-like) of the tweet types to filter, default is all
    :param func subset_func: function to provide custom subsetting, default is all
    :param int n_filepaths: optional, if not None, this is used to print progress
    :returns map: map object with tuples of tweet ID and set of types, e.g. [(1, {'retweet'}), (2, {'original'})]
    '''
    if not isinstance(keep_tweettypes, set): keep_tweettypes = set(keep_tweettypes)
    assert keep_tweettypes.issubset(set(['original', 'retweet', 'reply', 'quote']))
    tweets = load_tweets_from_filepaths(filepaths,
                                        progressbar=True if n_filepaths else False,
                                        n_filepaths=n_filepaths)
    tweets = filter(subset_func, tweets)
    tweets = map(get_tweettypes, tweets)
    tweets = filter(lambda tupl: len(keep_tweettypes.intersection(tupl[1])) > 0, tweets)
    return tweets


def get_attributes(tweet, attributes):
    '''
    extracts attributes from a tweet object

    :param dict tweet: the tweet object
    :param list attributes: list of attributes to extract, nested attributes separated with '.', e.g. 'user.screen_name'
    :returns tuple: returns tuple of (tweet ID, [attribute[0], attribute[1], ...])
    '''
    values = []
    for attribute in attributes:
        keys = attribute.split('.')
        values.append(safe_get(tweet, *keys))
    return tweet.get('id'), values


def eat_tweetattributes(filepaths, ids, attributes, n_filepaths=None):
    '''
    extracts tweet attributes for a set of tweets specified by ID from tweets stored in filepaths

    :param iterable filepaths: an iterable with the paths of the tweetfiles
    :param iterable ids: list (or set) with target tweets
    :param list attributes: list of attributes to extract, nested attributes separated with '.', e.g. 'user.screen_name'
    :param int n_filepaths: optional, if not None, this is used to print progress
    :returns map: containing tuples of (tweet ID, [attribute[0], attribute[1], ...])
    '''
    if not isinstance(ids, set): ids = set(ids)
    tweets = load_tweets_from_filepaths(filepaths,
                                        progressbar=True if n_filepaths else False,
                                        n_filepaths=n_filepaths)
    tweets = filter(lambda tweet: tweet.get('id') in ids, tweets)
    tweets = map(functools.partial(get_attributes, attributes=attributes), tweets)
    return tweets
