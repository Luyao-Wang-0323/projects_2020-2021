import urllib.request
from bs4 import BeautifulSoup
import urllib
import requests
import os
import pandas as pd
def getHtml(url):
    html = urllib.request.urlopen(url).read()
    return html
 
def saveHtml(file_name, file_content):
    with open('film_html/'+file_name.replace('/', '_') + ".html", "wb") as f:
        f.write(file_content)
        
#scraping 100 movies' links
def get_url():
    urls=[]# 100 movies' links
    url = "https://www.rottentomatoes.com/top/bestofrt/"
    html = urllib.request.urlopen(url).read() 
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup('td')# locate the position where can get the href and text
    for tag in tags:
        if not tag.get('class',None):
            if tag.a:
                title=tag.a.text
                url=tag.a.get('href',None)# href isn't the complete link
                item=(title.strip(),'https://www.rottentomatoes.com/'+url)# item is the link
                urls.append(item)
    return urls# return a list of tuples(title,link) 

#download html by the given links
def save_htmls():
    urls=get_url()# a list includes 100 tuples(title,link) 
    i=0
    for url in urls:
        i+=1
        html = getHtml(url[1])# url[1] is the link
        fname='film'+str(i)# file's names
        saveHtml(fname, html)#download html
        
#scraping movies' info
def get_data():
    unique_studio = pd.read_csv('unique_studio_score.csv', sep=',')# studios' info
    unique_studio_score=unique_studio['score']
    unique_studio_name=unique_studio['unique_s']
    # get movies' info
    df_list=[] # list of dictionaties, each dictionary contains the info of a movie
    folder = 'film_html'# the folder including html files
    for movie_html in os.listdir(folder):#get the webpage of html files from the folder
        if movie_html=='.ipynb_checkpoints':
            continue
        else:
            with open(os.path.join(folder, movie_html)) as file:
                soup=BeautifulSoup(file,'lxml')
                tags=soup('span')#the span inclus movies' scores
                score=[]
                info=[]
                for tag in tags:
                    if tag.get('class',None): 
                        if tag.get('class',None)[0]=='mop-ratings-wrap__percentage':
                            score.append(tag.text.strip())
                            
                tags=soup('h1')#the position inclus movies' info
                for tag in tags:             
                    title=tag.text.strip()
                    break
                tags=soup('div')
                for tag in tags:             
                    if tag.get('class',None): 
                        if tag.get('class',None)[0]=='meta-value':
                            info.append(tag.text.strip())
                #split info and save some useful
                genre=[]
                for g in info[1].split(','):
                    genre.append(g.strip())  
                try:
                    year=info[5].split(',')[1]
                except:
                    year=info[4].split(',')[1]
                
                runtime=info[-2].split(' ')[0]
                
                for j in range(len(unique_studio_name)):# change the studio's name in studios' score
                    if info[-1]==unique_studio_name[j]:
                        studio=int(unique_studio_score[j])
                df_list.append({'title': title,
                                'audience_score': score[1],
                                'fresh_score': score[0],
                               'genre':len(genre),# number of genres of each movie
                               'year': year,
                               'runtime':runtime,
                               'studio': studio})# studio's score
    df = pd.DataFrame(df_list, columns = ['title','audience_score','fresh_score','genre','year','runtime','studio'])# covert to a datafrome
    return df

if __name__ == "__main__":
    save_htmls()
    get_data()



