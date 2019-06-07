from lib.eat_tweets import *

def get_engagements(tweet, ids):
    '''
    workhorse of engagement extraction. extracts engagements from a tweet towards a list of target tweets
    specified by the ids

    :param dict tweet: single tweet
    :param list ids: list the tweet ids with respect to which engagements are extracted (usually 'original' tweets)
    :returns list of tuples: engagement information extract from the single tweet, that is
                             [('engagement_created_at', 'engagement_id', 'engagement_screen_name',
                             'original_tweet_id', 'engagement_type', 'engagement_count'), ...],

                             e.g.
                             [('2019-08-07 00:00:00', 1, NA, 4, 'favourite_count', 3)],
                             meaning the tweet with id 1 contains the information that the favourite count of the tweet
                             with id 4 was 3 at time '2019-08-07 00:00:00'.

                             'engagement_type' is one of 'favourite_count', 'retweet_count', 'reply', 'retweet' or
                             'quote'. The counts represent truly observed counts. 'reply', 'quote' and 'retweet'
                             represent an insample engagement and hence 'engagement_count' = 1 for those values.

                             since the engagements cannot be attributed for the counts, 'engagement_screen_name'
                             is None for those rows.
    '''
    id_ = tweet.get('id')
    created_at = tweet.get('created_at')
    user_screenname = safe_get(tweet, *('user', 'screen_name'))
    engagements = []
    if 'retweet' in tweet.get('tweettypes'):
        retweeted_id = safe_get(tweet, *('retweeted_status', 'id'))
        if retweeted_id in ids:
            retweeted_favourite_count = safe_get(tweet, *('retweeted_status', 'favorite_count'))
            retweeted_retweet_count = safe_get(tweet, *('retweeted_status', 'retweet_count'))
            engagements.append((created_at, id_, None, retweeted_id, 'favourite_count', retweeted_favourite_count))
            engagements.append((created_at, id_, None, retweeted_id, 'retweet_count', retweeted_retweet_count))
            engagements.append((created_at, id_, user_screenname, retweeted_id, 'retweet', 1))
    if 'quote' in tweet.get('tweettypes'):
        quoted_id = safe_get(tweet, *('quoted_status', 'id'))
        if quoted_id in ids:
            quoted_favourite_count = safe_get(tweet, *('quoted_status', 'favorite_count'))
            quoted_retweet_count = safe_get(tweet, *('quoted_status', 'retweet_count'))
            engagements.append((created_at, id_, None, quoted_id, 'favourite_count', quoted_favourite_count))
            engagements.append((created_at, id_, None, quoted_id, 'retweet_count', quoted_retweet_count))
            engagements.append((created_at, id_, user_screenname, quoted_id, 'quote', 1))
    if 'reply' in tweet.get('tweettypes'):
        replied_to_id = tweet.get('in_reply_to_status_id')
        if replied_to_id in ids:
            engagements.append((created_at, id_, user_screenname, replied_to_id, 'reply', 1))
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
