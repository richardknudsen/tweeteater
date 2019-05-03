import pandas as pd
from lib.eat_tweets import *
from lib.utils import *


if __name__ == '__main__':
    TWEET_DIRECTORY = '/Volumes/Data/mt_data/ger'
    EXT = '.jsonl'
    OUTPUT_DIRECTORY = '/Users/richardknudsen/Dropbox/twitter_shared_data/ger_processed/'

    # subset for politicians
    pt = 'sample_data/screenname2party.json'
    politicians_screennames = set([scn for scn, party in load_json(pt).items()])
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
    attributes = ['created_at', 'user.screen_name', 'user.name', 'user.favourites_count', 'text', 'lang']
    filepaths = get_filepaths(TWEET_DIRECTORY, EXT)
    n_filepaths = len(list(get_filepaths(TWEET_DIRECTORY, EXT)))
    tweet_attributes = eat_tweetattributes(filepaths, ids, attributes, n_filepaths=n_filepaths)
    tweet_attributes = pd.DataFrame([[a] + b for a, b in tweet_attributes])
    tweet_attributes.columns = ['id'] + attributes
    tweet_attributes.drop_duplicates(subset=['id'], inplace=True)
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
    engagements.drop_duplicates(subset=['observed in tweet.id', 'tweet.id', 'engagement type'],
                                inplace=True)
    engagements.to_csv(OUTPUT_DIRECTORY + 'engagements.csv', index=False)