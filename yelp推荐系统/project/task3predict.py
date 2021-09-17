import json
import timeit
from pyspark import SparkContext,SparkConf
import sys
import os

os.environ['PYSPARK_PYTHON']='/usr/local/bin/python3.6'
os.environ['PYSPARK_DRIVER_PYTHON']='/usr/local/bin/python3.6'
conf = (SparkConf()
     .setAppName("hw2")
     .set("spark.driver.extraJavaOptions", "-Xss10M"))
sc=SparkContext("local","hw3",conf=conf)

def get_predict_rate(x,original_neighbors,rates):
    #x:(user,bus)//(bus,user)
    #model_dic: { b1:[(b6,sim)......], b2:[],...... }
    #bu_dic :{ b1:{u3,u7...}, b2:{},...... }
    #bu_rate_dic: {u:{b:rate,b2:rate...},....}
    #return: ((user,bus),star)
    user=x[0]
    item=x[1]
    weights =0
    products =0
    k=0
    for (item2,sim) in iter(original_neighbors):
        try:
            rate = rates[item2]
            products+=rate * sim
            weights+=sim
            k += 1
        except:
            continue
        if k==20:
            break
    if weights !=0:
        predict = products/ weights
        return ((user, item), predict)
    else:
        return

def convert_rdd_to_list(rdd,chunk_size=10000):
    indexed_rows = rdd.zipWithIndex().cache()
    count = indexed_rows.count()
    start = 0
    end = start + chunk_size
    while start < count:
        chunk = indexed_rows.filter(lambda r: r[1] >= start and r[1] < end).collect()
        for row in chunk:
            yield row[0]
        start = end
        end = start + chunk_size

def case_one(train_file,test_file,model_file,output_file):
    model_dic_rdd=sc.textFile(model_file).map(json.loads).flatMap(lambda x:[(x['b1'],(x['b2'],x['sim'])),(x['b2'],(x['b1'],x['sim']))])\
        .groupByKey()\
        .mapValues(lambda x: sorted(x,key=lambda a:a[1],reverse=True))
    model_dic=dict(convert_rdd_to_list(model_dic_rdd))

    bu_rate_dic_rdd = sc.textFile(train_file).map(json.loads).map(lambda x: (x['user_id'], (x['business_id'], x['stars'])))\
        .groupByKey()\
        .mapValues(dict)
    bu_rate_dic=dict(convert_rdd_to_list(bu_rate_dic_rdd))

    result = sc.textFile(test_file).map(json.loads).map(lambda x: (x['user_id'], x['business_id']))\
        .filter(lambda x: x[0] in bu_rate_dic and x[1] in model_dic)\
        .map(lambda x: get_predict_rate(x,model_dic[x[1]], bu_rate_dic[x[0]])) \
        .filter(lambda x: x != None)

    # write to a file ((user, item), predict)
    with open(output_file, 'w') as f:
        for l in iter(convert_rdd_to_list(result)):
            u=l[0][0]
            b=l[0][1]
            star=l[1]
            string = '{"user_id": "' + u + '", "business_is": "' + b + '", "stars": ' + str(star) + '}\n'
            f.write(string)
    f.close()

def case_two(train_file, test_file, model_file, output_file):
    model_dic_rdd = sc.textFile(model_file).map(json.loads).flatMap(lambda x: [(x['u1'], (x['u2'], x['sim'])), (x['u2'], (x['u1'], x['sim']))]) \
        .groupByKey() \
        .mapValues(lambda x: sorted(x, key=lambda a: a[1], reverse=True))
    model_dic = dict(convert_rdd_to_list(model_dic_rdd))

    bu_rate_dic_rdd = sc.textFile(train_file).map(json.loads).map(lambda x: (x['business_id'], (x['user_id'], x['stars']))) \
        .groupByKey() \
        .mapValues(dict)
    bu_rate_dic = dict(convert_rdd_to_list(bu_rate_dic_rdd))

    result = sc.textFile(test_file).map(json.loads).map(lambda x: (x['business_id'], x['user_id'])) \
        .filter(lambda x: x[0] in bu_rate_dic and x[1] in model_dic) \
        .map(lambda x: get_predict_rate(x, model_dic[x[1]], bu_rate_dic[x[0]])) \
        .filter(lambda x:x!= None)

    # write to a file ((user, item), predict)
    with open(output_file, 'w') as f:
        for l in iter(convert_rdd_to_list(result)):
            u = l[0][1]
            b = l[0][0]
            star = l[1]
            string = '{"user_id": "' + u + '", "business_is": "' + b + '", "stars": ' + str(star) + '}\n'
            f.write(string)
    f.close()

def predict(train_file,test_file,model_file,output_file,cf_type):
    if cf_type=="item_based":
        start_time = timeit.default_timer()
        case_one(train_file,test_file,model_file,output_file)
        end = timeit.default_timer()
        print(end - start_time)
    elif cf_type=="user_based":
        start_time = timeit.default_timer()
        case_two(train_file,test_file,model_file,output_file)
        end = timeit.default_timer()
        print(end - start_time)
# train_file="train_review.json"
# test_file="test_review.json"
# model_file="task3user.model"
# output_file="task3user_1.predict"
# cf_type="user_based"
train_file=sys.argv[1]
test_file=sys.argv[2]
model_file=sys.argv[3]
output_file=sys.argv[4]
cf_type=sys.argv[5]
predict(train_file,test_file,model_file,output_file,cf_type)