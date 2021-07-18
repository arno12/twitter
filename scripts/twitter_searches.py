import logging
import boto3
from botocore.exceptions import ClientError
import tweepy
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from settings import consumer_key, consumer_secret, access_token, access_token_secret


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

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

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
        pd.read_csv(
            last_31days_results_path, sep="\t", parse_dates=["queried_at", "created_at"]
        )
        if last_31days_results_path.is_file()
        else pd.DataFrame(columns=["id"])
    )

    print(f"The loading size of the file is: {len(last_31days_results)}")
    print(f"Located at {last_31days_results_path}")

    last_31days_results = last_31days_results[last_31days_results["created_at"] > date_since]

    print(f"the length of the last 31 days file after filtering is {len(last_31days_results)}")

    # Create logs folder if it doesn't exist yet
    Path("./logs").mkdir(parents=True, exist_ok=True)

    logs_path = Path("./logs/logs.csv")

    logs = (
        pd.read_csv(logs_path)
        if logs_path.is_file()
        else pd.DataFrame(columns=["imported_at", "company", "total_rows"])
    )

    # intialize empty df for last 31 days - so we can add each company tweet id's to it in the loop
    col_names = [
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
    ]

    for company in companies:
        print("Starting with {}...".format(company))
        query = company + " -filter:retweets"

        tweets = tweepy.Cursor(
            api.search,
            q=query,
            # geocode="51.969685,4.051642,1000km",
            count=100,
            result_type="recent",
            include_entities=True,
            since=date_since,
            tweet_mode="extended",
        ).items(1000)
        locs = [
            [
                tweet.id,
                tweet.metadata["iso_language_code"],
                tweet.created_at,
                tweet.user.screen_name,
                tweet.full_text,
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
            columns=col_names,
        )
        print(f"original size of new df for {company}: {len(df)}")

        # Identify what values are in last_results and not in df
        existing_ids = list(set(last_31days_results.id).intersection(df.id))
        print(f"existing id's of {company} in last 31 days: {len(existing_ids)}")
        # Exclude rows that contain id's that we already have from a previous iteration
        new_ids = df[~df.id.isin(existing_ids)]

        # Append new rows to existing result set
        new_ids.to_csv(
            new_results_path,
            mode="a",
            header=not Path(new_results_path).is_file(),
            index=False,
            sep="\t",
        )

        # Print logs
        print(f"Done! Wrote a total of {len(new_ids)} new row(s) for {company}")

        # Upload to s3
        upload_file(
            "./results/twitter_searches_incremental.tsv",
            "arno12-tweets",
            "all-tweets/twitter_searches_incremental.tsv",
        )

        last_31days_results = pd.concat([last_31days_results, new_ids])
        print(
            f"The new length of the last 31 days file is {len(last_31days_results)}"
        )

        # Generate logs
        logs = pd.DataFrame(
            data=[[datetime.now().timestamp(), company, len(df.index)]],
            columns=["imported_at", "company", "total_rows"],
        )

        logs.to_csv(
            logs_path, mode="a", header=not Path(logs_path).is_file(), index=False
        )

    last_31days_results.to_csv(
        last_31days_results_path,
        index=False,
        sep="\t",
    )
