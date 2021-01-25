# Go to repo
cd ~/Documents/repos/twitter

# Activate virtual environment
source activate twitter

# Make sure we're not behind master
/usr/bin/git pull

# Execute script
/home/pi/berryconda3/envs/twitter/bin/python twitter_searches_tmp.py

# Versioning
/usr/bin/git add results/* logs/*
/usr/bin/git commit -m "latest changes" 
/usr/bin/git push origin master
