#!/bin/bash

echo "[`date +"%y-%m-%d %H:%I:%S"`] Sync started";

# Go to repo
cd /home/pi/Documents/repos/twitter

# Make sure we're not behind master
/usr/bin/git pull

# Download table containing last 30 days of tweets

# Execute main job to retrieve new tweets
/home/pi/miniconda3/envs/twitter/bin/python scripts/twitter_searches.py

# Create tsv version of csv that can be read from Athena


# Upload new output to s3
/home/pi/miniconda3/envs/twitter/bin/python scripts/upload_tsv_results_to_s3.py

# Versioning
HOME=/home/pi
/usr/bin/git add results/* logs/*
/usr/bin/git commit -m "latest changes" 
/usr/bin/git push origin master

echo "[`date +"%y-%m-%d %H:%I:%S"`] Sync ended";
