import json
import itertools
from tqdm import tqdm
##from more_itertools import ilen
from utils import *


def load_tweets_from_filepath(filepath):
    with open(filepath, 'r') as file:
        tweets = (json.loads(line) for line in file.readlines())
    return tweets


def load_tweets_from_filepaths(filepaths, progressbar=False, n_filepaths=None):
    if progressbar:
        return itertools.chain.from_iterable(map(load_tweets_from_filepath, tqdm(filepaths, total=n_filepaths)))
    else:
        return itertools.chain.from_iterable(map(load_tweets_from_filepath, filepaths))


def get_tweettypes(tweet):
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

def eat_tweettypes(filepaths, extension=None, keep_tweettypes=['original', 'retweet', 'reply', 'quote'],
                   n_filepaths=None):
    if not isinstance(keep_tweettypes, set): keep_tweettypes = set(keep_tweettypes)
    assert keep_tweettypes.issubset(set(['original', 'retweet', 'reply', 'quote']))
    tweets = load_tweets_from_filepaths(filepaths,
                                        progressbar=True if n_filepaths else False,
                                        n_filepaths=n_filepaths)
    tweets = filter(subset_func, tweets)
    tweets = map(get_tweettypes, tweets)
    tweets = filter(lambda tupl: len(keep_tweettypes.intersection(tupl[1])) > 0, tweets)
    return tweets




# test script eat tweettypes args
#irectory = '/Volumes/Data/mt_data/ger/2017-09-24'
#xtension = '.jsonl'
#ilepaths = get_filepaths(directory, extension)
#_filepaths = len(list(get_filepaths(directory, extension)))
#ubset_func = lambda tweet: True
#weets = eat_tweettypes(filepaths, extension=extension, n_filepaths=n_filepaths)
#