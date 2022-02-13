from secrets import (
    ACCESS_TOKEN,
    AWS_ID,
    AWS_S3_BUCKET,
    AWS_S3_TWEETS_BACKUP_LOCATION,
    AWS_SECRET,
    mysql_db,
    mysql_host,
    mysql_port,
    mysql_pwd,
    mysql_user,
)

import pandas as pd
from sqlalchemy import create_engine

if __name__ == "__main__":
    # Load connection settings to MySQL
    engine = create_engine(
        f"mysql+mysqldb://{mysql_user}:{mysql_pwd}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4&binary_prefix=true",
        encoding="utf-8",
        pool_recycle=3600,
        convert_unicode=True,
        echo=True,
    )

    # Load the Twitter df
    twitter = pd.read_sql(
        "SELECT * FROM tweets",
        con=engine,
        parse_dates=["created_at", "queried_at"],
    )

    # Upload to s3
    twitter.to_csv(
        f"s3://{AWS_S3_BUCKET}/{AWS_S3_TWEETS_BACKUP_LOCATION}",
        sep="\t",
        index=False,
        storage_options={
            "key": AWS_ID,
            "secret": AWS_SECRET,
            "token": ACCESS_TOKEN,
        },
    )
