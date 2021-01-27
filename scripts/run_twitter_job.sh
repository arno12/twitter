#!/bin/bash

echo "[`date +"%y-%m-%d %H:%I:%S"`] Sync started";

# Add directories to PATH so that user root can use GIT LFS
export PATH=$PATH:/home/pi/berryconda3/bin:/usr/local/go/bin

# Go to repo
cd /home/pi/Documents/repos/twitter

# Make sure we're not behind master
/usr/bin/git pull

# Execute script
/home/pi/berryconda3/envs/twitter/bin/python scripts/twitter_searches.py

# Versioning
HOME=/home/pi
/usr/bin/git add results/* logs/*
/usr/bin/git commit -m "latest changes" 
/usr/bin/git push origin master

echo "[`date +"%y-%m-%d %H:%I:%S"`] Sync ended";
