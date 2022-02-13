import logging
from datetime import datetime, timedelta
from pathlib import Path
from secrets import (ACCESS_TOKEN, ACCESS_TOKEN_SECRET, AWS_ID, AWS_S3_BUCKET,
                     AWS_S3_TWEETS_BACKUP_LOCATION, AWS_SECRET, CONSUMER_KEY, CONSUMER_SECRET, mysql_db,
                     mysql_host, mysql_port, mysql_pwd, mysql_user)

import pandas as pd
import tweepy
from sqlalchemy import create_engine

if __name__ == "__main__":
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    companies = ["blendle", "cafeyn", "milibris", "readly"]

    # 30 days ago - which is the maximum time Twitter allows you to go in the past.
    date_since = datetime.now() - timedelta(days=30)
    date_since = date_since.strftime("%Y-%m-%d")
    date_now = datetime.now().strftime("%Y_%m_%d")

    # create results folder if it doesn't exist yet
    Path("./results").mkdir(parents=True, exist_ok=True)

    # Load connection settings to MySQL
    engine = create_engine(
        f"mysql+mysqldb://{mysql_user}:{mysql_pwd}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4&binary_prefix=true",
        encoding="utf-8",
        pool_recycle=3600,
        convert_unicode=True,
        echo=True,
    )

    # Load last 31 days data
    last_31days_results = pd.read_sql(
        "SELECT * FROM tweets WHERE queried_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 31 DAY)",
        con=engine,
        parse_dates=["created_at", "queried_at"],
    )

    print(f"The loading size of the file is: {len(last_31days_results)}")

    # intialize empty df for last 31 days - so we can add each company tweet id's to it in the loop
    col_names = last_31days_results.columns.values.tolist()

    for company in companies:
        print("Starting with {}...".format(company))
        query = company + " -filter:retweets"

        tweets = tweepy.Cursor(
            api.search,
            q=query,
            count=100,
            result_type="recent",
            include_entities=True,
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
        new_ids.to_sql(
            con=engine,
            name="tweets",
            if_exists="append",
            index=False,
            chunksize=50,
        )

        # Print logs
        print(f"Done! Wrote a total of {len(new_ids)} new row(s) for {company}")

        # Generate logs
        logs = pd.DataFrame(
            data=[[datetime.now().timestamp(), company, len(df.index)]],
            columns=["timestamp", "company", "total_rows"],
        )

        # Save logs to DB table
        logs.to_sql(
            con=engine,
            name="tweet_logs",
            if_exists="append",
            index=False,
            chunksize=50,
        )
