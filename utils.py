from config import *
import re
from datetime import datetime
import io
from PIL import Image
import requests




def get_tweet_text(tweet):
    ''' Just the status text '''
    return tweet.text


def get_desc_weight(desc):
    ''' Weight for description: if english football fan it's a plus '''
    if desc != None and any([(word in english_clubs) for word in desc.split()]):
        return 1
    return 0.3
def get_account_age_weight(created_at):
    ''' Weight for account age '''
    created_at = datetime.strptime(created_at,'%a %b %d %H:%M:%S +0000 %Y')
    now = datetime.now()
    days_since = (now - created_at).days
    if days_since < 1:
        return 0.05
    elif days_since < 30:
        return 0.1
    elif days_since < 90:
        return 0.25
    return 1
def get_followers_weight(num_of_followers):
    ''' Weight for number of followers '''
    if num_of_followers < 50:
        return 0.5 / 3.0
    elif num_of_followers < 5000:
        return 1.0 / 3.0
    elif num_of_followers < 10000:
        return 1.5 / 3.0
    elif num_of_followers < 20000:
        return 2.0 / 3.0
    else:
        return 3.0 / 3.0
def get_verified_weight(verified):
    ''' Weight for verified user '''
    if verified:
        return 1
    return 2/3

def is_tweet_good_enough(tweet, threshold=0.6):
    ''' Calculates quality score and returns True if threshold (default = 0.6) is surpassed  '''
    if tweet.user != None:
        description_weight = get_desc_weight(tweet.user.description)
        account_age_weight = get_account_age_weight(tweet.user.created_at)
        followers_weight = get_followers_weight(tweet.user.followers)
        verified_weight = get_verified_weight(tweet.user.verified)
        profile_weight = 0.5 if tweet.user.is_default else 1.0  #get_profile_weight(tweet)

        quality_score = (description_weight + account_age_weight + followers_weight + verified_weight + profile_weight ) / 5
        # print(quality_score)
        # print(f"description_weight: {description_weight}")
        # print(f"account_age_weight: {account_age_weight}")
        # print(f"followers_weight: {followers_weight}")
        # print(f"verified_weight: {verified_weight}")
        # print(f"profile_weight: {profile_weight}")
        return quality_score > threshold
    else:
        return False


def preprocess_text(text):
    ''' Remove emojis and english stopwords '''
    text = deEmojify(text)
    words = text.split()
    out = []
    for word in words:
        if word not in en_stops:
            out.append(word)
    return " ".join(out)

def deEmojify(text):
    ''' Removes emojis from string '''
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)
def download_image(url, image_file_path='./random_img.jpg'):
    ''' Downloads image to target dir '''
    r = requests.get(url, timeout=4.0)
    if r.status_code != requests.codes.ok:
        assert False, 'Status code error: {}.'.format(r.status_code)

    with Image.open(io.BytesIO(r.content)) as im:
        im.save(image_file_path)

    print('Image downloaded from url: {} and saved to: {}.'.format(url, image_file_path))