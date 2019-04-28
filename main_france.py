import pandas as pd
from lib.eat_tweets import *
from lib.utils import *


if __name__ == '__main__':
    TWEET_DIRECTORY = '/Volumes/Data/mt_data/fr/json_cleaned'
    EXT = '.jsonl'
    OUTPUT_DIRECTORY = '/Users/richardknudsen/Dropbox/Dokumente_Richard/RA_upf/prep_hannah/data/'

    # subset for politicians
    pt = '/Users/richardknudsen/Downloads/france_target_screennames_v2.csv'
    politicians_screennames = set(pd.read_csv(pt, header=None)[0].tolist())
    subset_func = lambda tweet: safe_get(tweet, *('user', 'screen_name')) in politicians_screennames

    # keep original tweets only
    keep_tweettypes = ['original']

    # load tweets
    print('Load tweets...')
    filepaths = get_filepaths(TWEET_DIRECTORY, EXT)
    n_filepaths = len(list(get_filepaths(TWEET_DIRECTORY, EXT)))
    tweettypes = eat_tweettypes(filepaths, keep_tweettypes=keep_tweettypes,
                                subset_func=subset_func, n_filepaths=n_filepaths)
    ids = [id_ for id_, types in tweettypes]

    # extract attributes
    print('Extract attributes...')
    attributes = ['created_at', 'user.screen_name', 'user.name', 'text', 'lang']
    filepaths = get_filepaths(TWEET_DIRECTORY, EXT)
    n_filepaths = len(list(get_filepaths(TWEET_DIRECTORY, EXT)))
    tweet_attributes = eat_tweetattributes(filepaths, ids, attributes, n_filepaths=n_filepaths)
    tweet_attributes = pd.DataFrame([[a] + b for a, b in tweet_attributes])
    tweet_attributes.columns = ['id'] + attributes
    tweet_attributes.to_csv(OUTPUT_DIRECTORY + 'tweets.csv', index=False)

    # extract engagement
    print('Extract engagement...')
    filepaths = get_filepaths(TWEET_DIRECTORY, EXT)
    n_filepaths = len(list(get_filepaths(TWEET_DIRECTORY, EXT)))
    engagements = eat_engagements(filepaths, ids, n_filepaths=n_filepaths)
    engagements = pd.DataFrame(list(engagements))
    engagements.columns = ['observed timestamp', 'observed in tweet.id', 'tweet.id',
                           'engagement type', 'count']
    tweetid2screenname = dict(zip(tweet_attributes['id'], tweet_attributes['user.screen_name']))
    tweetid2createdat = dict(zip(tweet_attributes['id'], tweet_attributes['created_at']))
    engagements['user.screen_name'] = [tweetid2screenname[id_]
                                       for id_ in engagements['tweet.id']]
    engagements['created_at'] = [tweetid2createdat[id_]
                                 for id_ in engagements['tweet.id']]
    engagements.to_csv(OUTPUT_DIRECTORY + 'engagements.csv', index=False)