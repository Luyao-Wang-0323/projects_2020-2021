import itertools
import json
import math
import timeit
import random
from pyspark import SparkContext,SparkConf
import sys
import os

os.environ['PYSPARK_PYTHON']='/usr/local/bin/python3.6'
os.environ['PYSPARK_DRIVER_PYTHON']='/usr/local/bin/python3.6'
conf = (SparkConf()
     .setAppName("hw2")
     .set("spark.driver.extraJavaOptions", "-Xss10M"))
sc=SparkContext("local","hw3",conf=conf)

def get_neighbors_withJS(input_file):
    functions = []
    As = random.sample(range(1, 1000), 50)
    Bs = random.sample(range(0, 1000), 50)
    for a, b in zip(As, Bs):
        functions.append((a, b))

    def hash_func_row(uid, m):
        return [(f[0] * uid + f[1]) % m for f in iter(functions)]

    def minhash(hashs_list, num):
        signatures_list = []
        for h in range(num):
            min_list = []
            for l in iter(hashs_list):
                min_list.append(l[h])
            min_value = min(min_list)
            signatures_list.append(min_value)
        return signatures_list

    def LSH(bid, signature_list, bands, rows):
        band = 0
        signatures = [0]
        result = []
        for row in range(bands * rows):
            if band < math.floor(row / rows):
                result.append((hash(str(signatures)), bid))
                band += 1
                signatures = [band]
            signatures.append(signature_list[row])
        result.append((hash(str(signatures)), bid))
        return result

    def get_combination_jaccard(cdd_list, bu_dic):
        l = sorted(cdd_list)
        comb = itertools.combinations(l, 2)
        for x in iter(comb):
            bid1 = x[0]
            bid2 = x[1]
            b1 = bu_dic[bid1]
            b2 = bu_dic[bid2]
            if len(b1.intersection(b2)) >= 3:
                Jaccard = len(b1.intersection(b2)) / float(len(b1.union(b2)))
                if Jaccard >= 0.01:
                    yield (bid1, bid2)

    def task(input_file):
        start_time = timeit.default_timer()
        bands = 50
        rows = 1
        RDD = sc.textFile(input_file).map(json.loads)

        # 1.from input file: get signature udict,bdict
        # get charicteristic matrix ub_dic,bu_dic
        bu_dataset = RDD.map(lambda x: (x["user_id"], x["business_id"])).collect()  # rdd: [(b1,u1),(b1,u3)......]
        # bu_dataset = RDD.map(lambda x: (x["business_id"], x["user_id"])).collect() #rdd: [(b1,u1),(b1,u3)......]
        rdd_user_index = sc.parallelize(bu_dataset).values().distinct().zipWithIndex()  # rdd: [(u1,uid1),......]

        # 2.MinHash
        m = rdd_user_index.count()
        uid_hash_matrix = rdd_user_index.mapValues(lambda uid: hash_func_row(uid, m)).collectAsMap()
        # [u1:[h1......hn],u2:[h1......hn]......]
        signatures_matrix = sc.parallelize(bu_dataset).mapValues(lambda u: uid_hash_matrix[u]).groupByKey().mapValues(
            lambda x: minhash(x, bands * rows))
        # [(b1,[signature_list]),(b2,[signature_list])......]

        # 3. LSH
        bu_dic = sc.parallelize(bu_dataset).groupByKey().mapValues(set).collectAsMap()

        # 4.cmopute JS of each candidate pair through sig matrix
        rdd_candidates = signatures_matrix.map(lambda x: LSH(x[0], x[1], bands, rows)) \
            .flatMap(lambda x: x) \
            .groupByKey() \
            .values() \
            .filter(lambda x: len(x) >= 2).collect()
        rdd_similar_pair = sc.parallelize(rdd_candidates, 50).flatMap(
            lambda x: get_combination_jaccard(x, bu_dic)).distinct().collect()
        return rdd_similar_pair

    results=task(input_file)
    return results

def get_pearson(neighbors,data_dic):
    #(item,[items...])
    #{item:{(user,star),...},......}
    item1=neighbors[0]
    item1_star=data_dic[item1]
    item1_users=dict(item1_star)
    result=[]
    for item2 in iter(neighbors[1]):
        item2_star=data_dic[item2]
        item2_users = dict(item2_star)
        co_users=set(item1_users.keys()).intersection(set(item2_users.keys()))
        r1 = sum([item1_users[user] for user in co_users])/len(co_users)
        r2 = sum([item2_users[user] for user in co_users])/len(co_users)
        w1=sum([(item1_users[user]-r1)*(item2_users[user]-r2) for user in co_users])
        w2=math.sqrt(sum([(item1_users[user]-r1)**2 for user in co_users]))
        w3 = math.sqrt(sum([(item2_users[user] - r2) ** 2 for user in co_users]))
        if w2*w3==0:
            weight_ij=0
        else:
            weight_ij=w1/(w2*w3)
        if weight_ij>=0:
            result.append(((item1,item2),weight_ij))
    return result

def get_neighbor(neighbors,item_users):
    #input: [(i,i+1)...]
    #{item:{user...}......}
    result=[]
    for x in iter(neighbors):
        index1=x[0]
        index2=x[1]
        items1=item_users[index1][0]
        users1=item_users[index1][1]
        items2 = item_users[index2][0]
        users2 = item_users[index2][1]
        if len(users1.intersection(users2)) >= 3:
            result.append(items2)
    return (items1,result)

def case_one(train_file,model_file):
    start_time = timeit.default_timer()
    RDD=sc.textFile(train_file).map(json.loads)
    #1.get data from train_file: [(item,{(user,star),...})......]
    data_rdd=RDD.map(lambda x:(x["business_id"],(x["user_id"],x["stars"]))).groupByKey().mapValues(set)
    data_dic=dict(data_rdd.collect())
    #2.find neighbor:
    item_users = RDD.map(lambda x: (x["business_id"], x["user_id"])).groupByKey().mapValues(set).collect()
    #corelated user>=3 ------- input:[(item,{user...})......] ---loop---> output:[(item,[items...])......]
    neighbors=sc.parallelize([i for i in range(len(item_users)-1)],50)\
        .map(lambda i: [(i,j) for j in range(i+1,len(item_users))])\
        .map(lambda x: get_neighbor(x,item_users) )\
        .collect()
    #3.compute pearson weight for each pair of items in a neighbor
    pearson_neighbors=sc.parallelize(neighbors).map(lambda x:get_pearson(x,data_dic)).collect()
    #write to a file
    with open(model_file,'w') as f:
        for l in iter(pearson_neighbors):
            for i in iter(l):
                b1=i[0][0]
                b2=i[0][1]
                sim=i[1]
                string='{"b1": "'+b1+'", "b2": "'+b2+'", "sim": '+str(sim)+'}\n'
                f.write(string)
    f.close()
    end = timeit.default_timer()
    print(end - start_time)

def case_two(train_file,model_file):
    start_time = timeit.default_timer()
    neighbors=get_neighbors_withJS(train_file)
    # end = timeit.default_timer()
    # print(end - start_time)
    #3. compute pearson weight for each pair of user in a
    RDD = sc.textFile(train_file).map(json.loads)
    data_rdd = RDD.map(lambda x: (x["user_id"], (x["business_id"], x["stars"]))).groupByKey().mapValues(set)
    data_dic = dict(data_rdd.collect())
    pearson_neighbors = sc.parallelize(neighbors,50)\
        .groupByKey()\
        .mapValues(list)\
        .map(lambda x: get_pearson(x, data_dic)).collect()
    # end = timeit.default_timer()
    # print(end - start_time)
    # write to a file
    with open(model_file, 'w') as f:
        for l in iter(pearson_neighbors):
            for i in iter(l):
                u1 = i[0][0]
                u2 = i[0][1]
                sim = i[1]
                string = '{"u1": "' + u1 + '", "u2": "' + u2 + '", "sim": ' + str(sim) + '}\n'
                f.write(string)
    f.close()
    end = timeit.default_timer()
    print(end - start_time)



def train(train_file,model_file,cf_type):
    if cf_type=="item_based":
        case_one(train_file,model_file)
    elif cf_type=="user_based":
        case_two(train_file,model_file)


train_file=sys.argv[1]
model_file=sys.argv[2]
cf_type=sys.argv[3]
# train_file="train_review.json"
# model_file="task3item.model"
# cf_type="user_based"
# cf_type="item_based"
train(train_file,model_file,cf_type)
