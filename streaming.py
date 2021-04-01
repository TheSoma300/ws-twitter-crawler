import tweepy
from tweepy import StreamListener
import json
from pymongo import MongoClient

client = MongoClient()
db = client.db_twitter
tweets = db.tweets

class MyStreamListener(StreamListener):
    def on_data(self, raw_data):
        data = json.loads(raw_data)
        tweets.insert_one(data)
    # def on_status(self, status):
    #     print(status.text)
    def on_error(self, status_code):
        print(status_code)


with open('twitter_keys.json', 'r') as myfile:
    auth_data = myfile.read()

twitter_auth = json.loads(auth_data)
auth = tweepy.OAuthHandler(twitter_auth['key'], twitter_auth['secret'] )
auth.set_access_token(twitter_auth['token'], twitter_auth['token_secret'])

Loc_UK = [-10.392627, 49.681847, 1.055039, 61.122019]
WORDS = ['england', 'poland', 'qualifier', 'world', 'cup', 'football', 'premier', 'league', '2022', 'soccer', 'lions']

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

listener = MyStreamListener()
streamer = tweepy.Stream(auth=api.auth, listener=listener)

print('Tracking: ', WORDS)
streamer.filter(track=WORDS, locations=Loc_UK, languages=['en'], is_async=True)
