import RottenTomatoes
import MyTwitter
import ProcessData
import Analyze
import sys

def main():
    #get movies' info from RottenTomatoes
    try:
        RottenTomatoes.save_htmls() 
    except:
        print("warning: can't download movies' websites")
        sys.exit()
    try:
        dataframe=RottenTomatoes.get_data()
        dataframe.to_csv(r'csv/RottenTomatoes.csv', index = False)
    except:
        print("warning: can't get data from RottenTomatoes")
        sys.exit()

#get movies' retweet number from twitter
    try:
        dataframe2=MyTwitter.films_data()
        dataframe2.to_csv(r'csv/tweet.csv', index = False)
    except:
        print("warning: can't get data from Twitter")
        sys.exit()

    #process data in RottenTomatoes.csv and tweet.csv, and merge them into data.csv
    try:
        ProcessData.process_data()
    except:
        print("warning: can't process data")
        sys.exit()

    #analyze data.csv by using PCA and visualization
    try:
        Analyze.visualization()
    except:
        print("warning: can't analyze data or can't visualize results")
        sys.exit()

if __name__ == "__main__":
    main()




