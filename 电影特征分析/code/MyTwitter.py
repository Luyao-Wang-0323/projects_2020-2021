import tweepy
import json
import csv
import pandas as pd

#get miovies' titles
def get_films_titles():
    titles=[]
    with open('csv/RottenTomatoes.csv','r') as file:
        reader = csv.reader(file, delimiter=',')
        column = [row[0] for row in reader]
        titles=column[1:]
        return titles#a list

#get one movie's retweet numbers
def get_one_filmdata(title):
    # fill out your keys and secrets provide by twitter
    consumer_key = 'g94oxa11u9t3LXGRLPKFnDFyv'
    consumer_secret = 'aI0iASOPf9R8QjqVhU0AgeN2YCmzHSWMAdmsDAs5uSWSJ0dsOE'
    access_token = '1182158379516452864-LF4I0w01kedpvF2TIBRQx2WqkRP193'
    access_token_secret = 'CmuLhEiJi25b0lYiKRW1LijZeS907v78aY6iVx6vv3gq9'
    #submit your Key and secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    #get your api
    api = tweepy.API(auth)
    #use a given keyword(title) to do a search in twitter 
    #and get the top 10 searching results
    retweet=[]
    for tweet in tweepy.Cursor(api.search,q=title).items(10):
        retweet.append(tweet.retweet_count)
    data={'title': title,
        'retweet': sum(retweet)}# save the sum of 10 retweet numbers
    return data


# get all movies' retweet numbers and store in a csv
def films_data():
    titles=get_films_titles()
    datas=[]
    for title in titles:
        data=get_one_filmdata(title)
        datas.append(data)
    df = pd.DataFrame(datas, columns = ['title', 'retweet'])
    return df

if __name__ == "__main__":
    films_data()
    