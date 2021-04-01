import tweepy
from tweepy import StreamListener
import json
from pymongo import MongoClient
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from datetime import datetime
from config import *
from tweet_classes import *
from utils import *
import pickle

client = MongoClient()
db = client.db_twitter
tweets = db.football_tweets

class MyStreamListener(StreamListener):
    def on_data(self, raw_data):
        data = json.loads(raw_data)
        tweets.insert_one(data)
    # def on_status(self, status):
    #     print(status.text)
    def on_error(self, status_code):
        print(status_code)

def stream():
    with open('twitter_keys.json', 'r') as myfile:
        auth_data = myfile.read()

    twitter_auth = json.loads(auth_data)
    auth = tweepy.OAuthHandler(twitter_auth['key'], twitter_auth['secret'] )
    auth.set_access_token(twitter_auth['token'], twitter_auth['token_secret'])

    Loc_UK = [-10.392627, 49.681847, 1.055039, 61.122019]
    WORDS = ['england', 'poland', 'qualifier', 'cup', 'football', 'premier', 'league', '2022', 'soccer', 'lions']

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    listener = MyStreamListener()
    streamer = tweepy.Stream(auth=api.auth, listener=listener)

    print('Tracking: ', WORDS)
    streamer.filter(track=WORDS, locations=Loc_UK, languages=['en'], is_async=True)
def run_sample_precessing():
    all_tweets = []
    count = 0
    cursor = pickle.load( open( 'sample.p', "rb" ))
    for tweet in tqdm(cursor):
        tweet_obj = Tweet(tweet)
        is_it = is_tweet_good_enough(tweet_obj)
        if is_it:
            all_tweets.append(Tweet(tweet))

    print('num of good tweets: ', len(all_tweets))
    twitter_data = TweetData(all_tweets, save_random_image=True)

if __name__ == '__main__':
    run_sample_precessing()