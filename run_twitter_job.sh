#!/bin/bash

echo "[`date +"%y-%m-%d %H:%I:%S"`] Sync started";

# Go to repo
cd ~/Documents/repos/twitter

# Activate virtual environment
source /home/pi/berryconda3/envs/twitter/bin/activate twitter

# Make sure we're not behind master
/usr/bin/git pull

# Execute script
/home/pi/berryconda3/envs/twitter/bin/python twitter_searches_tmp.py

# Versioning
HOME=/home/pi
/usr/bin/git add results/* logs/*
/usr/bin/git commit -m "latest changes" 
/usr/bin/git push origin master

echo "[`date +"%y-%m-%d %H:%I:%S"`] Sync ended";
