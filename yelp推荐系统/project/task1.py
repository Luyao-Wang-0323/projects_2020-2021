import itertools
import math
import timeit
from pyspark import SparkContext, SparkConf
import random
import sys
import os
import json

os.environ['PYSPARK_PYTHON']='/usr/local/bin/python3.6'
os.environ['PYSPARK_DRIVER_PYTHON']='/usr/local/bin/python3.6'
conf = (SparkConf()
     .setAppName("hw2")
     .set("spark.driver.extraJavaOptions", "-Xss10M"))
sc=SparkContext("local","hw3",conf=conf)

# input=sys.argv[1]
# output=sys.argv[2]
input="train_review.json"
output="task1.res"

functions=[]
As = random.sample(range(1, 1000), 50)
Bs = random.sample(range(0, 1000), 50)
for a, b in zip(As, Bs):
    functions.append((a,b))

def hash_func_row(uid,m):
   return [(f[0]*uid+f[1])%m for f in iter(functions)]

def minhash(hashs_list,num):
    signatures_list=[]
    for h in range(num):
        min_list=[]
        for l in iter(hashs_list):
            min_list.append(l[h])
        min_value=min(min_list)
        signatures_list.append(min_value)
    return signatures_list

def LSH(bid,signature_list,bands,rows):
    band=0
    signatures=[0]
    result=[]
    for row in range(bands*rows):
        if band < math.floor(row / rows):
            result.append((hash(str(signatures)),bid))
            band += 1
            signatures = [band]
        signatures.append(signature_list[row])
    result.append((hash(str(signatures)),bid))
    return result

def get_combination_jaccard(cdd_list,bu_dic):
    l=sorted(cdd_list)
    comb=itertools.combinations(l,2)
    for x in iter(comb):
        bid1=x[0]
        bid2=x[1]
        b1=bu_dic[bid1]
        b2=bu_dic[bid2]
        Jaccard = len(b1.intersection(b2)) / float(len(b1.union(b2)))
        if Jaccard >= 0.05:
            yield ((bid1, bid2), Jaccard)


def task1(input_file,output_file):
    start_time = timeit.default_timer()
    bands = 50
    rows = 1
    RDD=sc.textFile(input_file).map(json.loads)

    # 1.from input file: get signature udict,bdict
    # get charicteristic matrix ub_dic,bu_dic
    bu_dataset = RDD.map(lambda x: (x["business_id"], x["user_id"])).collect() #rdd: [(b1,u1),(b1,u3)......]
    rdd_user_index = sc.parallelize(bu_dataset).values().distinct().zipWithIndex()#rdd: [(u1,uid1),......]

    # 2.MinHash
    m=rdd_user_index.count()
    uid_hash_matrix=rdd_user_index.mapValues(lambda uid: hash_func_row(uid,m)).collectAsMap()
    #[u1:[h1......hn],u2:[h1......hn]......]
    signatures_matrix= sc.parallelize(bu_dataset).mapValues(lambda u:uid_hash_matrix[u]).groupByKey().mapValues(lambda x:minhash(x,bands*rows))
    #[(b1,[signature_list]),(b2,[signature_list])......]


    # 3. LSH
    bu_dic = sc.parallelize(bu_dataset).groupByKey().mapValues(set).collectAsMap()

    # 4.cmopute JS of each candidate pair through sig matrix
    rdd_candidates = signatures_matrix.map(lambda x: LSH(x[0], x[1], bands, rows)) \
        .flatMap(lambda x: x) \
        .groupByKey() \
        .values() \
        .filter(lambda x: len(x) >= 2)
    rdd_similar_pair = rdd_candidates.flatMap(lambda x:get_combination_jaccard(x,bu_dic)).distinct().collect()

    # write to a file
    with open(output_file, "w") as f:
        for pair in rdd_similar_pair:
            b1=pair[0][0]
            b2=pair[0][1]
            similarity=pair[1]
            f.write('{"b1": "'+str(b1)+'", "b2": "'+str(b2)+'", "sim": '+str(similarity)+'}\n')
    f.close()

    end = timeit.default_timer()
    print(end - start_time)

# input=sys.argv[1]
# output=sys.argv[2]
task1(input,output)