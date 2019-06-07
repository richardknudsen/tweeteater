import pandas as pd
from lib.eat_tweets import *
from lib.eat_engagements import *
from lib.utils import *


def do_main(tweet_directory,
            extension,
            output_directory,
            subset_func=lambda tweet: True,
            keep_tweettypes=['original'],
            attributes=['created_at', 'user.screen_name', 'user.name', 'user.favourites_count',
                        'text', 'extended_tweet.full_text', 'lang']):
    '''
    extracts (optional: a subset) of all tweets in the tweet directory with specified attributes. also
    extracts engagements towards those tweets. stores output as .csvs

    tweets are stored in a csv where each column represents a tweet

    engagements are stored in a csv where each row is either an engagement or the observation of an engagement count,
    with the following columns:

        'engagement_created_at': the time when the engagement or the engagement count was observed
        'engagement_id': the id of the tweet in which the engagement or the engagement count was observed
        'engagement_screen_name': the screen name of the user engaging, if 'engagement_type' is one of
                                  {'reply', 'quote', 'count'}
        'original_tweet_id': the id of the tweet that was engaged upon
        'engagement_type': one of {'favourite_count', 'retweet_count', 'reply', 'retweet', 'quote'}
                           The counts represent truly observed counts. 'reply', 'quote' and 'retweet'
                           represent an insample engagement and hence 'engagement_count' = 1 for those values.
        'engagement_count': the engagement count


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
    engagements.columns = ['engagement_created_at', 'engagement_id', 'engagement_screen_name',
                           'original_tweet_id', 'engagement_type', 'engagement_count']
    tweetid2screenname = dict(zip(tweets['id'], tweets['user.screen_name']))
    tweetid2createdat = dict(zip(tweets['id'], tweets['created_at']))
    engagements['original_tweet_screen_name'] = [tweetid2screenname[id_] for id_ in engagements['original_tweet_id']]
    engagements['original_tweet_created_at'] = [tweetid2createdat[id_]for id_ in engagements['original_tweet_id']]
    engagements.drop_duplicates(subset=['engagement_id', 'original_tweet_id', 'engagement_type'], inplace=True)
    engagements.to_csv(output_directory + 'engagements.csv', index=False)

    return tweets, engagements


if __name__ == '__main__':

    # define directories
    TWEET_DIRECTORY = 'sample_data' # the directory with the tweet files
    EXTENSION = '.jsonl' # the extension of the tweetfiles
    OUTPUT_DIRECTORY = 'sample_output' # the directory where the output

    # define custom subsetting function, in this case, only consider tweets for which "user.screen_name"
    # is in a target set of screen names of politicians
    pt = 'sample_data/screenname2party.json'
    politicians_screennames = set([scn for scn, party in load_json(pt).items()])
    SUBSET_FUNC = lambda tweet: safe_get(tweet, *('user', 'screen_name')) in politicians_screennames

    # go
    do_main(tweet_directory=TWEET_DIRECTORY,
            extension=EXTENSION,
            output_directory=OUTPUT_DIRECTORY,
            subset_func=SUBSET_FUNC)