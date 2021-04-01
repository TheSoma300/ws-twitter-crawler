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

all_tweets = []
count = 0
cursor = tweets.find({})
sample = []

for tweet in tqdm(cursor):
    if count < 1000:
        sample.append(tweet)
        count += 1
    tweet_obj = Tweet(tweet)
    is_it = is_tweet_good_enough(tweet_obj)
    if is_it:
        all_tweets.append(Tweet(tweet))
pickle.dump(sample, open("sample.p", "wb" ) )

print('num of good tweets: ', len(all_tweets))
twitter_data = TweetData(all_tweets, save_random_image=True)

