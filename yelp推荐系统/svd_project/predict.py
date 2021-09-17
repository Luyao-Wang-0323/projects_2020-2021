import json
import sys
import numpy as np
from pyspark import SparkContext
from pyspark.mllib.linalg import Vectors
import os

os.environ['PYSPARK_PYTHON']='/usr/local/bin/python3.6'
os.environ['PYSPARK_DRIVER_PYTHON']='/usr/local/bin/python3.6'
sc=SparkContext("local","project")

test_file= 'data/test_review.json'
output_file='output.txt'

user_index=sc.textFile('model.index').map(json.loads).take(1)[0]
item_index=sc.textFile('model.index').map(json.loads).take(2)[1]
item_avg_rating=sc.textFile('model_avg.rating').map(json.loads).take(1)[0]
user_avg_rating=sc.textFile('model_avg.rating').map(json.loads).take(2)[1]
item_matrix=sc.textFile('model_item.svd').map(lambda x: [float(i) for i in x.split(',')]).map(lambda x: Vectors.dense(x)).collect()
s=sc.textFile('model_s.svd').map(lambda x: [float(i) for i in x.split(',')]).collect()
s_matrix=np.matrix(s)
user_matrix=sc.textFile('model_user.svd').map(lambda x: [float(i) for i in x.split(',')]).map(lambda x: Vectors.dense(x)).collect()
print('data')

test_data=sc.textFile(test_file).map(json.loads).map(lambda x:(x['user_id'],x['business_id'])).collect()
predictions=[]
for (uid,iid) in iter(test_data):
    if uid not in user_index and iid not in item_index:
        rating=0
    elif uid not in user_index and iid in item_index:
        rating=item_avg_rating[str(item_index[iid])]
    elif uid in user_index and iid not in item_index:
        rating = user_avg_rating[str(user_index[uid])]
    else:
        u=user_index[uid]
        i=item_index[iid]
        us = np.dot(user_matrix[u], s_matrix)
        sv = np.dot(s_matrix, item_matrix[i])
        rating=np.dot(us,sv.T)+item_avg_rating[str(i)]
        rating=rating.A[0][0]
    predictions.append((uid,iid,rating))
print('predict')

result=sc.parallelize(predictions).map(lambda x: {"user_id": x[0], "business_id":x[1] ,"stars": x[2]}).sortBy(lambda x:x['stars']).sortBy(lambda x: x['user_id'],ascending=False).collect()
with open(output_file,'w') as f:
    for i in result:
        output=json.dumps(i)
        f.write(output)
        f.write('\n')
