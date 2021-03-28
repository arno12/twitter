import logging
import boto3
from botocore.exceptions import ClientError
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


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client("s3")
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == "__main__":
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    companies = ["blendle", "cafeyn", "milibris", "readly"]

    # 30 days ago - which is the maximum time Twitter allows you to go in the past.
    date_since = datetime.now() - timedelta(days=30)
    date_since = date_since.strftime("%Y-%m-%d")
    date_now = datetime.now().strftime("%Y_%m_%d")

    # create results folder if it doesn't exist yet
    Path("./results").mkdir(parents=True, exist_ok=True)

    # Load previous data if it exists
    last_31days_results_path = Path("./results/twitter_searches_last_31_days.tsv")
    new_results_path = Path("./results/twitter_searches_incremental.tsv")

    last_31days_results = (
        pd.read_csv(last_31days_results_path, sep="\t")
        if last_31days_results_path.is_file()
        else pd.DataFrame(columns=["id"])
    )

    # Create logs folder if it doesn't exist yet
    Path("./logs").mkdir(parents=True, exist_ok=True)

    logs_path = Path("./logs/logs.csv")

    logs = (
        pd.read_csv(logs_path)
        if logs_path.is_file()
        else pd.DataFrame(columns=["imported_at", "company", "total_rows"])
    )

    for company in companies:
        print("Starting with {}...".format(company))
        query = company + " -filter:retweets"
        tweets = limit_handled(
            tweepy.Cursor(
                api.search,
                q=query,
                # geocode="51.969685,4.051642,1000km",
                count=100,
                result_type="recent",
                include_entities=True,
                since=date_since,
            ).items(1000)
        )

        locs = [
            [
                tweet.id,
                tweet.metadata["iso_language_code"],
                tweet.created_at,
                tweet.user.screen_name,
                tweet.text,
                tweet.user.location,
                tweet.favorite_count,
                tweet.retweet_count,
                datetime.now(),
                company,
            ]
            for tweet in tweets
        ]

        # latest data
        df = pd.DataFrame(
            data=locs,
            columns=[
                "id",
                "iso_language_code",
                "created_at",
                "screen_name",
                "text",
                "location",
                "favorite_count",
                "retweet_count",
                "queried_at",
                "company",
            ],
        )

        # Identify what values are in last_results and not in df
        existing_ids = list(set(last_31days_results.id).intersection(df.id))

        # Exclude rows that contain id's that we already have from a previous iteration
        df = df[~df.id.isin(existing_ids)]

        # Append new rows to existing result set
        df.to_csv(
            new_results_path,
            mode="a",
            header=not Path(new_results_path).is_file(),
            index=False,
            sep="\t",
        )

        # Upload to s3
        upload_file(
            df, "arno12-tweets", "all-tweets/twitter_searches_incremental.tsv"
        )

        # Save a version with the last 31 days only
        df_last_31_days = df[
            df.created_at > datetime.datetime.now() - pd.to_timedelta("31day")
        ]

        df_last_31_days.to_csv(
            last_31days_results_path,
            header=not Path(last_31days_results_path).is_file(),
            index=False,
            sep="\t",
        )

        # Upload to s3
        upload_file(
            df_last_31_days,
            "arno12-tweets",
            "all-tweets/twitter_searches_last_31_days.tsv",
        )

        # Print logs
        print(
            "Done! Wrote a total of {} new row(s) for {}.".format(
                len(df.index), company
            )
        )

        # Generate logs
        logs = pd.DataFrame(
            data=[[datetime.now().timestamp(), company, len(df.index)]],
            columns=["imported_at", "company", "total_rows"],
        )

        logs.to_csv(
            logs_path, mode="a", header=not Path(logs_path).is_file(), index=False
        )
