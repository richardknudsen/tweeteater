import json
import itertools
import functools
from tqdm import tqdm
from lib.utils import *


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
    extract tweettypes of a tweet and returns tuple of (tweet , set of types)

    :param dict-like tweet: tweet
    :returns tuple: (tweet, set of types), e.g. ({...}, {'retweet'})
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
    return tweet, tweettypes
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
    tweettypes = map(get_tweettypes, tweets)
    tweettypes = map(lambda tupl: (tupl[0].get('id'), tupl[1]), tweettypes)
    tweettypes = filter(lambda tupl: len(keep_tweettypes.intersection(tupl[1])) > 0, tweettypes)
    return tweettypes


def get_attributes(tweet, attributes):
    '''
    extracts attributes from a tweet object

    :param dict tweet: the tweet object
    :param list attributes: list of attributes to extract, nested attributes separated with '.', e.g. 'user.screen_name'
    :returns tuple: returns tuple of ({...}, [attribute[0], attribute[1], ...])
    '''
    values = []
    for attribute in attributes:
        keys = attribute.split('.')
        values.append(safe_get(tweet, *keys))
    return tweet, values


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
    tweetattributes = map(functools.partial(get_attributes, attributes=attributes), tweets)
    tweetattributes = map(lambda tupl: (tupl[0].get('id'), tupl[1]), tweetattributes)
    return tweetattributes


def get_engagements(tupl, ids):
    '''
    workhorse of engagement extraction. extracts engagements from a single tuple (tweet, tweettypes).

    :param tuple tupl: single tuple (tweet, tweettypes) coming out of get_tweettypes
    :param list ids: list the tweet ids with respect to which engagements are extracted (usually 'original' tweets)
    :returns list of tuples: engagement information extract from the single tweet, that is
                            [(tweet ID, tweet ID of reference tweet, engagement type, value), ...], e.g.
                            [(1, 2, 'favourite_count', 1), ('1', '2', 'retweet_count', 4)], meaning tweet
                            1 contains the information that the favourite count of tweet 2 is 2 and the
                            retweet count is 4 at the time tweet 1 was made. engagement types can be
                            'favourite_count', 'retweet_count', 'reply', or 'quote'. The counts represent
                            counts as contained in tweet objects, 'reply' and 'quote' are simple in-sample
                            counts and hence, on the level of a single tweet, always equal to one.
    '''
    tweet = tupl[0]
    tweettypes = tupl[1]
    tweet_id = tweet.get('id')
    engagements = []
    if 'retweet' in tweettypes:
        retweeted_id = safe_get(tweet, *('retweeted_status', 'id'))
        if retweeted_id in ids:
            retweeted_favourite_count = safe_get(tweet, *('retweeted_status', 'favorite_count'))
            retweeted_retweet_count = safe_get(tweet, *('retweeted_status', 'retweet_count'))
            engagements.append((tweet_id, retweeted_id, 'favourite_count', retweeted_favourite_count))
            engagements.append((tweet_id, retweeted_id, 'retweet_count', retweeted_retweet_count))
    if 'quote' in tweettypes:
        quoted_id = safe_get(tweet, *('quoted_status', 'id'))
        if quoted_id in ids:
            quoted_favourite_count = safe_get(tweet, *('quoted_status', 'favorite_count'))
            quoted_retweet_count = safe_get(tweet, *('quoted_status', 'retweet_count'))
            engagements.append((tweet_id, quoted_id, 'favourite_count', quoted_favourite_count))
            engagements.append((tweet_id, quoted_id, 'retweet_count', quoted_retweet_count))
            engagements.append((tweet_id, quoted_id, 'quote', 1))
    if 'reply' in tweettypes:
        replied_to_id = tweet.get('in_reply_to_status_id')
        if replied_to_id in ids:
            engagements.append((tweet_id, replied_to_id, 'reply', 1))
    return engagements



def eat_engagements(filepaths, ids, n_filepaths=None):
    '''
    extracts engagements from tweets in files

    :param iterable filepaths: an iterable with the paths of the tweetfiles
    :param list ids: list the tweet ids with respect to which engagements are extracted (usually 'original' tweets)
    :param int n_filepaths: optional, if not None, this is used to print progress
    :returns itertool.chain object: generator-type object of
                                    [(tweet ID, tweet ID of reference tweet, engagement type, value), ...]. for more
                                    see documentation of get_engagements
    '''
    if not isinstance(ids, set): ids = set(ids)
    tweets = load_tweets_from_filepaths(filepaths,
                                        progressbar=True if n_filepaths else False,
                                        n_filepaths=n_filepaths)
    tweettypes = map(get_tweettypes, tweets)
    engagements = map(functools.partial(get_engagements, ids=ids), tweettypes)
    engagements = filter(lambda engs: len(engs) > 0, engagements)
    engagements = itertools.chain.from_iterable(engagements)
    return engagements
