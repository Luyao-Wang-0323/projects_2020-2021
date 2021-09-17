import collections
import json
import math
import re
from string import digits, punctuation
from pyspark import SparkContext,SparkConf
import sys
import timeit
import os

os.environ['PYSPARK_PYTHON']='/usr/local/bin/python3.6'
os.environ['PYSPARK_DRIVER_PYTHON']='/usr/local/bin/python3.6'

sc=SparkContext("local","hw3")

def process(text,stopword):
    # to remove numeric digits from string
    text=text.lower()
    remove_digits = str.maketrans('', '', digits)
    remove_punctuations=str.maketrans('', '', punctuation)
    res = text.translate(remove_digits)
    words=res.split(' ')
    words_list1=[word.strip().translate(remove_punctuations) for word in iter(words)]
    words_list2=[word for word in iter(words_list1) if word not in stopword and len(word)>=1]
    word_dict=collections.Counter(words_list2)
    return list(word_dict.items())

def remove_rare(dic,rarewords):
    for word in iter(rarewords):
        if word in dic:
            del dic[word]
    return dic

def get_TF_IDF(docu_words,rarewords,IDF_dic):
    #(b1,[(w1,123),(w2,45),......(wn,56)])
    #return [(w1,(d1,tf11)),(w2,(d1,tf21))......]
    document=docu_words[0]
    max_num=max({x[1] for x in iter(docu_words[1])})
    result=[]
    # result=[(word[0],word[1]/max_num*IDF_dic[word[0]]) for word in iter(docu_words[1]) if word[0] not in rarewords]
    for word in iter(docu_words[1]):
        if word[0] not in rarewords:
            tf= word[1]/max_num
            idf=IDF_dic[word[0]]
            result.append((word[0],tf*idf))
    ordered_result=sorted(result,key=lambda x:x[1])
    return (document,ordered_result[:200])
    # return (document,result)

def get_user_vectors(user_bus,item_vectors):
    #[(u1,[b1,b3......]),......]
    #{b1:{v1,v2......},......}
    user=user_bus[0]
    bus_list=user_bus[1]
    all_vectors=[list(item_vectors[bus]) for bus in iter(bus_list)]
    treshold=len(all_vectors)*0.3
    aggaregate_vectors=collections.Counter(sum(all_vectors,[]))
    user_vector={vector for (vector,num) in aggaregate_vectors.items() if num > treshold}
    result=(user,user_vector)
    return result



def task2(input_file,model_file,stopwords):
    start_time = timeit.default_timer()
    #get text
    RDD=sc.textFile(input_file).map(json.loads)
    rdd_text=RDD.map(lambda x: (x['business_id'],x['text'])).reduceByKey(lambda a,b:a+' '+b)

    #get words' count for each document (for TF)
    stopword=set(sc.textFile(stopwords).collect())
    bus_words=rdd_text.mapValues(lambda text: process(text,stopword)).collect()
    #[(b1,[(w1,123),(w2,45),......(wn,56)]),......(bm,[])]
    end1 = timeit.default_timer()
    print(end1-start_time)#170s

    # find rare words
    all_words=sc.parallelize(bus_words).flatMap(lambda x:x[1])\
        .reduceByKey(lambda a,b:a+b) #[(w1:353),(w2:435)......]
    total_num=all_words.values().reduce(lambda a,b:a+b)
    frequency=int(total_num)*0.000001
    rare_words=all_words.filter(lambda x: x[1] < frequency).map(lambda x:x[0]).collect()
    rarewords=set(rare_words)
    end1 = timeit.default_timer()
    print(end1 - start_time)#219s

    # get document counts for each word (for IDF)
    N = RDD.map(lambda x: x["business_id"]).distinct().count()
    IDF_words_numbus=sc.parallelize(bus_words)\
        .flatMap(lambda x: [(w[0],1) for w in iter(x[1])])\
        .reduceByKey(lambda a,b:a+b)\
        .mapValues(lambda x: math.log(N / x, 2)) #[(w1,78),(w2,7)......]
    IDF = dict(IDF_words_numbus.collect())
    end1 = timeit.default_timer()
    print(end1 - start_time)#287s

    # 1.construct item vectors
    #computer TF*IDF foe each word each document in non_rare_words
    TF_IDF=sc.parallelize(bus_words,50).map(lambda x:get_TF_IDF(x,rarewords,IDF))
    #get vector
    item_vectors=TF_IDF.map(lambda x:(x[0],{w[0] for w in iter(x[1])})).collect()
    #[(b1,{v1,v2......}),......]
    item_vectors_dic = dict(item_vectors)
    end1 = timeit.default_timer()
    print(end1 - start_time)
    #2.construct user vectors & 3.compute cosine distance
    rdd_user=RDD.map(lambda x: (x['user_id'],x['business_id'])).groupByKey()
    user_vectors=rdd_user.map(lambda x: get_user_vectors(x,item_vectors_dic)).collect()
    # [(u1,{v1,v2......}),......]
    end1 = timeit.default_timer()
    print(end1 - start_time)

    with open(model_file,'w') as f:
        for x in item_vectors:
            item=x[0]
            vector=x[1]
            string='{"bid":"'+str(item)+'", '+'"vectors":"'+str(vector)+'"}\n'
            f.write(string)
        for x in user_vectors:
            user=x[0]
            vector=x[1]
            string='{"uid":"'+str(user)+'", '+'"vectors":"'+str(vector)+'"}\n'
            f.write(string)
    f.close()
    end1 = timeit.default_timer()
    print(end1 - start_time)



# input_file=sys.argv[1]
# model_file=sys.argv[2]
# stopwords=sys.argv[3]
input_file= 'train_review.json'
model_file= 'task2_model.json'
stopwords='stopwords'
task2(input_file, model_file,stopwords)