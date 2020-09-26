import tweepy
import time
import csv
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

    with open('blendle_searches.csv', 'w', newline='') as csvfile:

        csvfile = csv.writer(csvfile, delimiter=',',quotechar='"')
        csvfile.writerow(["created_at","screen_name","text","location","favorite_count","retweet_count"])

        for tweet in limit_handled(tweepy.Cursor(api.search,
            q=query,
            geocode="51.969685,4.051642,1000km",
            lang="nl", 
            rpp=100,
            result_type="recent",
            include_entities=True,
            since=date_since).items(10000)):

            if tweet.user.screen_name != 'BlendleNL':
                csvfile.writerow([tweet.created_at.strftime("%Y-%m-%d"), 
                                        tweet.user.screen_name, 
                                        tweet.text, 
                                        tweet.user.location, 
                                        str(tweet.favorite_count), 
                                        str(tweet.retweet_count)])
                print("created_at: {}\nuser: {}\ntweet text: {}\ngeo_location: {}\nfavorite_count: {}\nretweet_count: {}".format(tweet.created_at, tweet.user.screen_name, tweet.text, tweet.user.location, tweet.favorite_count, tweet.retweet_count))
                print("\n")
