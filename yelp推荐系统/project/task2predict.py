import json
import math
import timeit
from pyspark import SparkContext,SparkConf
import sys
import os

os.environ['PYSPARK_PYTHON']='/usr/local/bin/python3.6'
os.environ['PYSPARK_DRIVER_PYTHON']='/usr/local/bin/python3.6'

sc=SparkContext("local","hw3")

def process(type,id_vector_dic):
    if type=="bid":
        id = id_vector_dic["bid"]
    else:
        id = id_vector_dic["uid"]
    vector=id_vector_dic["vectors"].strip(' "{}').split(',')
    vectors={v.strip(" '") for v in vector}
    return (id,vectors)


def get_Cosine(user,bus,user_vector,bus_vector):
    dot_product= len(user_vector.intersection(bus_vector))
    distance_product=math.sqrt(len(user_vector)) * math.sqrt(len(bus_vector))
    cos_distance=dot_product/distance_product
    if cos_distance>=0.01:
       return ((user,bus),cos_distance)
    else:
        return ()

def predict(test_file,model_file,output_file):
    start_time = timeit.default_timer()

    RDD_test=sc.textFile(test_file).map(json.loads)
    test_data=RDD_test.map(lambda x: (x["user_id"],x["business_id"]))
    RDD_model=sc.textFile(model_file).map(json.loads)
    model_bus_data=RDD_model.filter(lambda x: "bid" in x).map(lambda x: process("bid",x)).collect()
    model_user_data = RDD_model.filter(lambda x: "uid" in x).map(lambda x: process("uid", x)).collect()
    bus_vector_dic=dict(model_bus_data)
    user_vector_dic=dict(model_user_data)
    end1 = timeit.default_timer()
    print(end1 - start_time)

    valid_data=test_data.map(lambda x: get_Cosine(x[0],x[1],user_vector_dic[x[0]],bus_vector_dic[x[1]]) if x[0] in user_vector_dic and x[1] in bus_vector_dic else ())\
        .filter(lambda x:len(x)>0).collect()
    end1 = timeit.default_timer()
    print(end1 - start_time)

    with open(output_file, 'w') as f:
        #((user,bus),cos_distance)
        for x in valid_data:
            cos=x[1]
            user=x[0][0]
            bus=x[0][1]
            string='{"user_id": "'+user+'", "business_id": "'+bus+'", "sim": '+str(cos)+'}\n'
            f.write(string)
    f.close()

    end1 = timeit.default_timer()
    print(end1 - start_time)

# item_vectors_dic=dict(item_vectors)
# rdd_cos=rdd_user.map(lambda x: get_Cosine(x,item_vectors_dic)).collect()

test_file= "test_review.json"
model_file= 'task2_model.json'
output_file= 'task2.predict'

predict(test_file, model_file, output_file)