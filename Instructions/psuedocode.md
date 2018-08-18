Build a twitter plot that sends out visualized sentiment analysis of a twitter
account's recent Tweets

1. bot receives tweet via mention
  a. in format "@haroonahmad06 Analyze: @______"
2. performs sentiment analysis on twitter account mentioned
3. plots the sentiment and tweets back results

rules:
1. bot should scan account every five minutes for mentions
2. pull 500 most recent tweets (to analyze from)
3. check if account has already been analyzed, if so do not re-analyze.

steps:

CheckTweet():
  1. scan account every five minutes for any mentions
    a. if last tweet is older than five minutes of current time, ignore
    b. if last tweet is not older than five minutes of current time, do PlotBot
       analysis
       1. to carry this function, convert the "created at" key in the tweet
       to a python time, subtract that from the current time, and see if it's less
       than 5 min (if so, run PlotBot analysis)
       2. convert tweet_time to a datetime object (strptime())
        a. datetime.now() = 2018-08-15 18:31:38.877261
  2. If last tweet occurred less than five minutes ago:
    a. check the contents of tweet
      1. if tweet says "@haroonahmad06 Analyze: @______" then do PlotBot function
      2. else do nothing

FilterTweets(array):
  1. for the each tweet, check the tweet text
    a. if the tweet begins with "@haroonahmad06 Analyze: @______"
      add that tweet to a new list

AnalyzeTweets(array):
  1. for each tweet in array:
    a. identify the user (split the text string, get the last word)
    b. pull 500 Tweets from user
    c. compute VADER scores
    d. put into DataFrame including tweet text, date, and account into CSV
    e. plot the compound score using a scatter plot, publish PNG
    f. publish plot/tweet with user mention
  2. How am I controlling for duplicate requests? I think it's OK because
     sentiments can change over time. but if I do control for duplicates,
     how would I check? is the user mentioned already in my home feed?
      a. If user mentioned in home tweets:
        1. do not run analysis, refer user to specific post
        2. else run analysis

PlotUserSentiment(DataFrame):
  1. 
