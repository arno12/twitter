import os
from dotenv import load_dotenv
# Load .env secret variables
load_dotenv()

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
aws_id = os.getenv("AWS_ID")
aws_secret = os.getenv("AWS_TOKEN")