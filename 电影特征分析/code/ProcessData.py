import pandas as pd

def processdata_twitter():
    data = pd.read_csv('csv/tweet.csv', sep=',')# import info
    retweet= data['retweet']#get data
    dvd=int(max(retweet)/1000)+1#dividing boundary
    level=[]
    for index in range(len(retweet)):
        for i in range(1000):
            i=i+1
            if retweet[index]<dvd*i:# divided into 1000 levels
                level.append(round(i*0.1,3))
                break      
    data['level'] = level  #add a new coumn
    data=data.drop(['retweet'], axis=1)#delete a column
    data.to_csv(r'csv/popularity.csv', index = False)
    
def processdata_RT():
    data = pd.read_csv('csv/RottenTomatoes.csv', sep=',')# import info
    #get data, and convert percentage to float
    audience= data['audience_score'].str.strip('%').astype(float)/100 
    fresh= data['fresh_score'].str.strip('%').astype(float)/100 
    #add two new columns
    data['professional_lable'] = fresh
    data['audience_lable'] = audience
    #delete two columns
    data=data.drop(['audience_score', 'fresh_score'], axis=1)
    data.to_csv(r'csv/score.csv', index = False)

def mergedata():
    # import info
    data1 = pd.read_csv('csv/popularity.csv', sep=',')
    data2 = pd.read_csv('csv/score.csv', sep=',')
    #get data
    title=data1['title']
    popularity= data1['level']
    #merge together
    data3={'title':title,
           'genre':data2['genre'],
           'year':data2['year'],
           'runtime':data2['runtime'],
           'studio':data2['studio'],
           'popularity':popularity,
           'professional_lable':data2['professional_lable'],
           'audience_lable':data2['audience_lable']}
    df = pd.DataFrame(data3, columns = ['title','genre','year','runtime','studio','popularity','professional_lable', 'audience_lable'])
    df.to_csv(r'csv/data.csv', index = False)


def process_data():
    processdata_twitter()
    processdata_RT()
    mergedata()

if __name__ == "__main__":
    process_data()



