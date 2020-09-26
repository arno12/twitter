import tweepy
import time 
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

    #public_tweets = api.home_timeline()
    #for tweet in public_tweets:
    #    print(tweet.text) 

    for follower in limit_handled(tweepy.Cursor(api.followers).items()):
        if follower.friends_count < 300:
            print(follower.screen_name)
