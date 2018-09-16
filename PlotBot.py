
# coding: utf-8

# In[13]:


# Dependencies
import json
import time
import tweepy
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import pandas as pd
import os


# In[14]:


# Import Twitter API Keys
# from config import consumer_key, consumer_secret, access_token, access_token_secret
consumer_key = os.environ.get(CONSUMER_KEY)
consumer_secret = os.environ.get(CONSUMER_SECRET)
access_token = os.environ.get(ACCESS_TOKEN)
access_token_secret = os.environ.get(ACCESS_TOKEN_SECRET)

# In[15]:


# Function to setup TweepyAPI

def TweepyAPI():

    # Setup Tweepy API Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

    return api


# In[16]:


# Function that pythonize's time

def PythonTime(time):

    # converted time of tweet
    conv_time_lt = datetime.strptime(time, "%a %b %d %H:%M:%S %z %Y")

    # current time
    current_time = datetime.now(timezone.utc)

    # calculate difference between now and tweet
    difftime = current_time - conv_time_lt

    return difftime


# In[17]:


# Function that checks my home page for which tweets are less than 5 minutes old, and returns those tweets

def CheckTweetTimes():

    # Setup authentication
    api = TweepyAPI()

    # Pull recent tweets from home page
    home_tweets = api.home_timeline()

    # tweets to check
    check_tweets = []

    # check which tweets are less than 5 minutes

    for each_tweet in home_tweets:

        # find tweet time
        last_tweet_time = each_tweet['created_at']

        # call PythonTime function
        difftime = PythonTime(last_tweet_time)

        # conditional to check if the time difference is less than 5 minutes:
        # if less than 5 minutes, add the tweet to check_tweets, else do nothing
        if difftime.seconds < 300:

            check_tweets.append(each_tweet)

    # return check_tweets
    return check_tweets

# this function should return a list of tweets that are less than 5 minutes from current time, with all information


# In[18]:


# create a function that filters the tweets relevant only to our analysis, tweets that begin with following syntax:
# "@haroonahmad06 Analyze: @______"

def FilterTweets(array):

    # tweets to analyze
    tweets_to_analyze = []

    # loop through array of tweets
    for each in array:

        # if "@haroonahmad06 Analyze: " is in the text of the tweet
        if "@haroonahmad06 Analyze: " in each['text']:
            tweets_to_analyze.append(each)

    return tweets_to_analyze

# This function should return a list of tweets to analyze


# In[19]:


# Function to organize tweets; returns a dataframe
def OrganizeTweets(user,dates,texts):

        # Push all information into a DataFrame
        combined = [[user],dates,texts]
        user_df = pd.DataFrame(combined, ['Tweet Author','Tweet Date','Tweet Text']).T

        # Replace NaNs with target_user (needed due to unequal list length b/w tweet dates/texts and author)
        user_df = user_df.fillna(value=user)

        return user_df



# In[20]:


# Function to perform Vader Analysis
def VaderAnalysis(dataframe):

    # Import dependencies
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()

    # List to store Vader Values
    vader_values = []

    # Iterate through each row of column "Tweet Text"
    for each in zip(dataframe['Tweet Text']):

        # Run Vader on each text, and store in vader_values
        vader_values.append(analyzer.polarity_scores(each[0]))

    # convert vader_values into DataFrame
    vader_values_df = pd.DataFrame(vader_values)

    # combine DataFrames
    user_vader_df = dataframe.join(vader_values_df)

    # Save tweet Author to save file name
    target_user = user_vader_df['Tweet Author'][0]

    # save final dataframe as csv with user identifying file name
    user_vader_df.to_csv("User Dataframes/%s.csv" % target_user)

    # return DataFrame for Plot function
    return user_vader_df


# In[21]:


# plot the compound score using a scatter plot, publish PNG
# x range will be tweets ago, number of tweets, x range from -1 to -500, range is 'compound'

def PlotUserSentiment(dataframe):

    # plot the scatter plot
    tweet_author = dataframe['Tweet Author'][0]
    current_date = datetime.now()
    x = np.arange(-1,-501,-1)
    y = dataframe['compound']

    f,ax = plt.subplots(figsize=(16,12))
    ax.plot(x,y,marker='o')
    plt.title('%s Sentiment Analysis on %s' % (tweet_author, current_date),fontsize=20)
    plt.xlabel('Tweets Ago',fontsize=16)
    plt.ylabel('Tweet Polarity',fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid()
    leg = ax.legend(fontsize = 'large')
    leg.get_texts()[0].set_text('Compound Score')
    leg.set_title("%s" % tweet_author, prop = {'size':'x-large'})
    plt.savefig('User Graphs/%s.png' % tweet_author)

    return f


# In[22]:


# publish plot/tweet with user mention

def PublishTweet(user_analyzed,requestor):

    # Setup authentication
    api = TweepyAPI()

    # Publish to Home Page and mention requestor of Tweet
    api.update_with_media("User Graphs/%s.png" % user_analyzed,
                      "Here is your analysis on %s. Thank you %s, please come again!" % (user_analyzed,requestor))



# In[23]:


def AnalyzeTweets(array):

    # If array is empty, say "There are no new tweets to analyze"
    # else Analyze the Tweet

    if not array:

        print("There are no new tweets to analyze")

    else:

        # Setup authentication
        api = TweepyAPI()

        for each_tweet in array:

            # Identify requestor of tweet
            requestor = each_tweet['user']['screen_name']
            requestor = '@%s' % requestor

            # Identify the user to perform analysis on (split the text string, get the last word)
            split_tweet_text = each_tweet['text'].split()
            target_user = split_tweet_text[-1]

            # Check to see how many statuses there are
            # If less than 500 tweet message to user
            # If not less than 500 run analysis
            if api.get_user(target_user)['statuses_count'] < 500:

                api.update_status("Sorry %s! I require at least 500 tweets to perform my analysis. It appears that %s                 does not have 500 tweets :(" % (requestor,target_user))

            else:

                # Pull 500 Tweets from user by using loop through pages
                tweets_text = []
                tweets_date = []

                for x in range(1, 26):

                    target_user_tweets = api.user_timeline(target_user, page=x)

                    #Loop through all tweets and save the text and date
                    for tweet in target_user_tweets:

                        tweets_text.append(tweet['text'])
                        tweets_date.append(tweet['created_at'])

                # Call OrganizeTweets function to dataframe the results
                user_df = OrganizeTweets(target_user,tweets_date,tweets_text)

                # Call VaderAnalysis function on dataframe
                df_to_plot = VaderAnalysis(user_df)

                # Call PlotUserSentiment function to plot the dataframe
                figure = PlotUserSentiment(df_to_plot)

                # Call PublishTweet to send out the tweet w/ analysis
                PublishTweet(target_user,requestor)


# In[24]:


# Steps to successfully analyze and plot a tweet:
    # Create an infinite loop that runs every five minutes
    # Call CheckTweetTimes to pull all tweets from the home page and check their times if posted < 5 min from now
    # Call FilterTweets to filter tweet_list for tweets relevant for analysis
    # Call AnalyzeTweets on analyze_this to either: analyze and plot tweets, or return an error message if:
        # a) there are less than 500 tweets to analyze
        # b) there are no items in the array (analyze_this)

counter = 0

# Infinite loop
while(True):

    # Call the CheckTweets function and store result
    tweet_list = CheckTweetTimes()

    # Call the FilterTweets function and store result
    analyze_this = FilterTweets(tweet_list)

    # Call the AnalyzeTweets function to do the analysis
    AnalyzeTweets(analyze_this)

    # Once checked, wait 5 minutes then check again
    time.sleep(300)

    # Add 1 to the counter prior to re-running the loop, Counter used to check how many times ran?
    counter = counter + 1
