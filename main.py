import pandas as pd
from lib.eat_tweets import *
from lib.eat_engagements import *
from lib.utils import *


def do_main(tweet_directory,
            extension,
            output_directory,
            subset_func=lambda tweet: True,
            keep_tweettypes=['original'],
            attributes=['created_at', 'user.screen_name', 'user.name', 'user.favourites_count', 'text', 'lang']):
    '''
    extracts (optional: a subset) of all tweets in the tweet directory with specified attributes. also
    extracts engagements towards those tweets. stores output as .csvs

    :param str tweet_directory: directory with tweetfiles
    :param str extension: extension of tweetfiles in tweet_directory, e.g. '.jsonl'
    :param str output_directory: where 'tweets.csv' and 'engagements.csv' will be dumped
    :param func subset_func: function to provide custom subsetting on whether a tweet shall be extracted
    :param list keep_tweettypes: which tweettypes to keep. all tweettypes are ['original', 'retweet', 'reply', 'quote']
    :param list attributes: tweet attributes to extract
    :return:
    '''

    if not output_directory[-1] == '/': output_directory += '/'

    print('Eating tweets...')
    filepaths = get_filepaths(tweet_directory, extension)
    n_filepaths = len(list(get_filepaths(tweet_directory, extension)))
    tweets = eat_tweets(filepaths, attributes, keep_tweettypes=keep_tweettypes,
                        subset_func=subset_func, n_filepaths=n_filepaths)
    tweets = pd.DataFrame(tweets)
    tweets.columns = ['id', 'tweettypes'] + attributes
    tweets.drop_duplicates(subset=['id'], inplace=True)
    tweets.to_csv(output_directory + 'tweets.csv', index=False)

    print('Eating engagements...')
    filepaths = get_filepaths(tweet_directory, extension)
    engagements = eat_engagements(filepaths, tweets['id'], n_filepaths=n_filepaths)

    engagements = pd.DataFrame(engagements)
    engagements.columns = ['observed timestamp', 'observed in tweet.id', 'tweet.id', 'engagement type', 'count']
    tweetid2screenname = dict(zip(tweets['id'], tweets['user.screen_name']))
    tweetid2createdat = dict(zip(tweets['id'], tweets['created_at']))
    engagements['user.screen_name'] = [tweetid2screenname[id_] for id_ in engagements['tweet.id']]
    engagements['created_at'] = [tweetid2createdat[id_]for id_ in engagements['tweet.id']]
    engagements.drop_duplicates(subset=['observed in tweet.id', 'tweet.id', 'engagement type'],inplace=True)
    engagements.to_csv(output_directory + 'engagements.csv', index=False)

    return tweets, engagements


if __name__ == '__main__':

    # args 0: directories
    TWEET_DIRECTORY = 'sample_data'
    EXTENSION = '.jsonl'
    OUTPUT_DIRECTORY = 'sample_output'

    # arg 1: custom subsetting for tweet by politicians only
    pt = 'sample_data/screenname2party.json'
    politicians_screennames = set([scn for scn, party in load_json(pt).items()])
    SUBSET_FUNC = lambda tweet: safe_get(tweet, *('user', 'screen_name')) in politicians_screennames

    # go
    do_main(tweet_directory=TWEET_DIRECTORY,
            extension=EXTENSION,
            output_directory=OUTPUT_DIRECTORY,
            subset_func=SUBSET_FUNC)