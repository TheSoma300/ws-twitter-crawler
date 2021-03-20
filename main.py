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

with open('twitter_keys.json', 'r') as myfile:
    auth_data = myfile.read()

twitter_auth = json.loads(auth_data)
auth = tweepy.OAuthHandler(twitter_auth['key'], twitter_auth['secret'] )
auth.set_access_token(twitter_auth['token'], twitter_auth['token_secret'])

Loc_UK = [-10.392627, 49.681847, 1.055039, 61.122019]

listener = MyStreamListener(
    api=tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
)
streamer = tweepy.Stream(auth=auth, listener=listener)
WORDS = ['covid','corona','covid19','coronavirus',
'facemask','sanitizer','social-distancing' ]
print('Tracking: ', WORDS)
# streamer.filter(track=WORDS, locations=Loc_UK, languages=['en'], is_async=True)
