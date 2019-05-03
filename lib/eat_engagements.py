from lib.eat_tweets import *

def get_engagements(tweet, ids):
    '''
    workhorse of engagement extraction. extracts engagements from a tweet.

    :param dict tweet: single tweet
    :param list ids: list the tweet ids with respect to which engagements are extracted (usually 'original' tweets)
    :returns list of tuples: engagement information extract from the single tweet, that is
                            [(tweet ID, tweettypes, tweet ID of reference tweet, engagement type, value), ...], e.g.
                            [(1, 2, 'favourite_count', 1), ('1', '2', 'retweet_count', 4)], meaning tweet
                            1 contains the information that the favourite count of tweet 2 is 2 and the
                            retweet count is 4 at the time tweet 1 was made. engagement types can be
                            'favourite_count', 'retweet_count', 'reply', or 'quote'. The counts represent
                            counts as contained in tweet objects, 'reply' and 'quote' are simple in-sample
                            counts and hence, on the level of a single tweet, always equal to one.
    '''
    tweet_id = tweet.get('id')
    tweet_created_at = tweet.get('created_at')
    engagements = []
    if 'retweet' in tweet.get('tweettypes'):
        retweeted_id = safe_get(tweet, *('retweeted_status', 'id'))
        if retweeted_id in ids:
            retweeted_favourite_count = safe_get(tweet, *('retweeted_status', 'favorite_count'))
            retweeted_retweet_count = safe_get(tweet, *('retweeted_status', 'retweet_count'))
            engagements.append((tweet_created_at, tweet_id, retweeted_id, 'favourite_count', retweeted_favourite_count))
            engagements.append((tweet_created_at, tweet_id, retweeted_id, 'retweet_count', retweeted_retweet_count))
    if 'quote' in tweet.get('tweettypes'):
        quoted_id = safe_get(tweet, *('quoted_status', 'id'))
        if quoted_id in ids:
            quoted_favourite_count = safe_get(tweet, *('quoted_status', 'favorite_count'))
            quoted_retweet_count = safe_get(tweet, *('quoted_status', 'retweet_count'))
            engagements.append((tweet_created_at, tweet_id, quoted_id, 'favourite_count', quoted_favourite_count))
            engagements.append((tweet_created_at, tweet_id, quoted_id, 'retweet_count', quoted_retweet_count))
            engagements.append((tweet_created_at, tweet_id, quoted_id, 'quote', 1))
    if 'reply' in tweet.get('tweettypes'):
        replied_to_id = tweet.get('in_reply_to_status_id')
        if replied_to_id in ids:
            engagements.append((tweet_created_at, tweet_id, replied_to_id, 'reply', 1))
    return engagements


def eat_engagements(filepaths, ids, n_filepaths=None):
    '''
    extracts engagements from tweets in files

    :param iterable filepaths: an iterable with the paths of the tweetfiles
    :param list ids: list the tweet ids with respect to which engagements are extracted (usually 'original' tweets)
    :param int n_filepaths: optional, if not None, this is used to print progress
    :returns itertool.chain object: generator-type object of
                                    [(tweet ID, tweettypes, tweet ID of reference tweet, engagement type, value), ...].
                                    for more see documentation of get_engagements
    '''
    if not isinstance(ids, set): ids = set(ids)
    tweets = load_tweets_from_filepaths(filepaths,
                                        progressbar=True if n_filepaths else False,
                                        n_filepaths=n_filepaths)
    tweets = map(get_tweettypes, tweets)
    engagements = map(functools.partial(get_engagements, ids=ids), tweets)
    engagements = filter(lambda engs: len(engs) > 0, engagements)
    engagements = itertools.chain.from_iterable(engagements)
    return engagements
