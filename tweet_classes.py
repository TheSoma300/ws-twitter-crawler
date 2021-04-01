
from utils import *
from config import *
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from collections import Counter



class Tweet:
    def __init__(self, tweet_data):
        if 'text' in tweet_data.keys():
            self.text = preprocess_text(tweet_data['text'])
        self.tweet_type = self.get_type(tweet_data)

        if 'user' in tweet_data.keys():
            self.user = TwitterUser(tweet_data['user'])
        else:
            self.user = None
        self.get_geo_data(tweet_data)
        
    def set_vector(self, vec):
        self.vector = vec
    def get_type(self, data):
        if 'extended_tweet' in data.keys():
            self.is_extended = True
            self.extended_tweet = data['extended_tweet']
            if 'entities' in self.extended_tweet.keys():
                self.entities = self.extended_tweet['entities']
        else: self.is_extended = False
        if 'user' in data.keys():  
            if data['user']['screen_name'] == "Retweeter":
                return 'retweet'
            if data['user']['screen_name'] == "TweetQuoter":
                self.text = f"{self.text} {preprocess_text(data['quoted_status'])}"
                return 'quote'
        return 'normal'
    def get_geo_data(self, data):
        self.geo_locations = {}

        if "geo" in data.keys():
            self.geo_locations['geo'] = data["geo"]
        elif "coordinates" in data.keys():
            self.geo_locations['coordinates'] = data["coordinates"]
        elif "place" in data.keys():
            self.geo_locations['place'] = data["place"]
            
    def __str__(self):
        return f"Tweet object: type: {self.tweet_type}"




class TwitterUser:
    def __init__(self, user_data):
        self.id = user_data['id']
        self.name = user_data['name']
        self.screen_name = user_data['screen_name']
        self.location = user_data['location']
        self.description = user_data['description']
        self.verified = user_data['verified']
        self.statuses_count = user_data['statuses_count']
        self.created_at = user_data['created_at']
        self.followers = user_data['followers_count']
        self.is_default = json.dumps(user_data).find('default_profile_image') != -1



class TweetData:
    def __init__(self, tweets, save_random_image=False):
        self.tweets = tweets
        self.cluster_counter = 0
        self.clusters = []
        self.metrics_counts = {
            'retweets': 0,
            'quotes': 0,
            'media': 0,
            'verified': 0,
            'geo_tagged': 0,
            'loc_or_place': 0
        }
        self.process_tweets()
        self.group_tweets()
        self.report()

    def process_tweets(self):
        print('Processing tweets started....')
        corpus = list(map(get_tweet_text, self.tweets))
        self.vectorizer = TfidfVectorizer(strip_accents='ascii', lowercase=True, stop_words='english')
        vector = self.vectorizer.fit_transform(corpus)
        images_downlaoded = 0
        for tweet in tqdm(self.tweets):
            tweet.set_vector(
                self.vectorizer.transform([tweet.text])
            )
            if tweet.tweet_type != 'normal':
                if tweet.tweet_type == 'retweet': self.metrics_counts['retweets'] += 1
                if tweet.tweet_type == 'quote': self.metrics_counts['quotes'] += 1
            if tweet.is_extended:
                if 'media' in tweet.entities:
                    for image in tweet.entities['media']:
                        if images_downlaoded == 0:
                            print(image['media_url'])
                            download_image(image['media_url'])
                            images_downlaoded = 1
                        self.metrics_counts['media'] += 1
                if len(tweet.geo_locations.keys()) > 0:
                    if 'geo' in tweet.geo_locations.keys(): self.metrics_counts['geo_tagged'] += 1
                    if any([(x in tweet.geo_locations.keys()) for x in ['coordinates', 'place']]): self.metrics_counts['loc_or_place'] += 1
            if tweet.user != None:
                if tweet.user.verified: self.metrics_counts['verified'] += 1
            
    def group_tweets(self):
        print('Grouping tweets started....')
        for tweet in tqdm(self.tweets):
            max_sim = 0
            if self.cluster_counter == 0:
                self.clusters.append(Cluster(0, tweet))
                self.cluster_counter += 1
            else:
                cluster_id = 0
                # try all clusters
                for cluster in self.clusters:
                    cos_sim = cosine_similarity(cluster.vector, tweet.vector)
                    
                    if cos_sim > max_sim:
                        max_sim = cos_sim
                        cluster_id = cluster.id
                    
                    if self.cluster_counter < 10 and max_sim < 0.0005:
                        self.clusters.append(Cluster(self.cluster_counter, tweet))
                        self.cluster_counter += 1
                    else:
                        self.clusters[cluster_id].add_tweet(tweet)
            # print(f"currently num of clusters: {self.cluster_counter}")
    
    def report(self):
        print('Grouping finished!')
        print(f"Num of clusters: {self.cluster_counter}")
        print(f"Num of tweets: {len(self.tweets)}")
        tweet_lens = []
        for cluster in self.clusters:
            out = cluster.get_most_used_word()
            print(f"most used word in cluster {cluster.id} is {out}")
            tweet_lens.append(len(cluster.tweets))
            print(f"num of tweets {len(cluster.tweets)}")
        print("Groups formed: 10")
        print(f"Min size: {min(tweet_lens)}")
        print(f"Max size: {max(tweet_lens)}")
        print(f"Avg size: {sum(tweet_lens) / 10}")

        print('Metrics')
        for key in self.metrics_counts:
            print(f"{key}: {self.metrics_counts[key]}")
        


class Cluster:
    def __init__(self, id, tweet):
        self.id = id
        self.vector = tweet.vector
        self.tweets = [tweet]
        self.users = [tweet.user]
    def update_vector(self, new_vec):
        self.vector = (self.vector + new_vec) / 2
    def add_tweet(self, tweet):
        self.tweets.append(tweet)
        self.update_vector(tweet.vector)
    def get_most_used_word(self):
        given_string = ""
        for tweet in self.tweets:
            given_string += tweet.text
        words = given_string.split()
        return Counter(words).most_common(3)
        
