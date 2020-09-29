import tweepy
import time
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from settings import consumer_key, consumer_secret, access_token, access_token_secret

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)

if __name__ == '__main__':
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    query = "blendle -filter:retweets"

    # 7 days ago - which is the maximum time Twitter allows you to go in the past.
    date_since = datetime.now() - timedelta(days=7) 
    date_since = date_since.strftime("%Y-%m-%d")
    date_now = datetime.now().strftime("%Y_%m_%d")

    tweets = limit_handled(tweepy.Cursor(api.search,
        q=query,
        # geocode="51.969685,4.051642,1000km",
        count=100,
        result_type="recent",
        include_entities=True,
        since=date_since).items(1000))
            
    locs = [[tweet.id,tweet.metadata['iso_language_code'],tweet.created_at,tweet.user.screen_name,tweet.text,tweet.user.location,tweet.favorite_count,tweet.retweet_count,datetime.now()] for tweet in tweets]

    # create results folder if it doesn't exist yet
    Path('./results').mkdir(parents=True, exist_ok=True)

    # latest data
    df = pd.DataFrame(
        data = locs,
        columns=["id","iso_language_code","created_at","screen_name","text","location","favorite_count","retweet_count","queried_at"])

    # Load previous data if it exists
    last_results_path = Path("./results/blendle_searches_incremental.csv")
    
    last_results = pd.read_csv(last_results_path) if last_results_path.is_file() else pd.DataFrame(columns=["id"])
    
    # Identify what values are in last_results and not in df
    existing_ids = list(set(last_results.id).intersection(df.id))
    
    df = df[~df.id.isin(existing_ids)]

    df.to_csv(last_results_path, mode='a', header=not Path(last_results_path).is_file())