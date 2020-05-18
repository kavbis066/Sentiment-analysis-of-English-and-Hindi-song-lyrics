# Sentiment-analysis-of-English-and-Hindi-song-lyrics

This is a project for sentiment analysis done on English and hindi song lyrics. For English songs the data has been taken from kaggle. For Hindi song lyrics the data has been scraped from Genius.com.

To scrape the lyrics from genius.com, run the file "scrape.py"
To run type: python scrape.py -a 'artist name' -c 'credentials.json' -o 'output-artist.txt'

For English Song lyrics following analysis have been done:
1. Exploratory Data Analysis: to understand the data
2. Classifiers
2.1. Naive Bayes
2.2. Logistic Regression
2.3. Random Forest
2.4. Support Vector Machine
  
For Hindi Song lyrics "Resource Based Sentiment Analysis" is done using Hindi Sentiwordnet as resource.
