import json
import math
import numpy as np
from pyspark import SparkContext
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.linalg.distributed import RowMatrix
import os

os.environ['PYSPARK_PYTHON']='/usr/local/bin/python3.6'
os.environ['PYSPARK_DRIVER_PYTHON']='/usr/local/bin/python3.6'
sc=SparkContext("local","project")

rdd=sc.textFile('train_review.json').map(json.loads)
data=rdd.map(lambda x:(x['business_id'],(x['user_id'],x['stars']))).cache()
userList = data.map(lambda x:x[1][0]).collect()
itemList = data.map(lambda x:x[0]).collect()
users = list(set(userList))
items = list(set(itemList))
users_index = {users[i]: i for i in range(len(users))}
item_index={items[i]: i for i in range(len(items))}
item_avg_rating_dict=data.map(lambda x:(item_index[x[0]],(x[1][1],1))).reduceByKey(lambda a,b:(a[0]+b[0],a[1]+b[1])).mapValues(lambda v:v[0]/v[1]).collectAsMap()
user_avg_rating_dict=data.map(lambda x:(users_index[x[1][0]],(x[1][1],1))).reduceByKey(lambda a,b:(a[0]+b[0],a[1]+b[1])).mapValues(lambda v:v[0]/v[1]).collectAsMap()
# item_avg_rating_dict=sc.textFile('business_avg.json').map(json.loads).flatMap(lambda x: x.items())\
#     .filter(lambda x: x[0] in item_index).map(lambda x:(item_index[x[0]],x[1])).collectAsMap()
# user_avg_rating_dict=sc.textFile('user_avg.json').map(json.loads).flatMap(lambda x: x.items())\
#     .filter(lambda x: x[0] in users_index).map(lambda x:(users_index[x[0]],x[1])).collectAsMap()
user_item_dict = data.map(lambda x:(users_index[x[1][0]],(item_index[x[0]],x[1][1]-item_avg_rating_dict[item_index[x[0]]])))\
    .groupByKey().mapValues(list).mapValues(dict).sortByKey()
rows=user_item_dict.map(lambda x: Vectors.sparse(len(items), x[1]))

mat = RowMatrix(rows)

# Compute the top 5 singular values and corresponding singular vectors.
svd = mat.computeSVD(27, computeU=True)
U = svd.U.rows.collect()       # The U factor is a RowMatrix.
s = svd.s       # The singular values are stored in a local dense vector.
V = svd.V.toArray() # The V factor is a local dense matrix.
s_list=[]
for i in range(len(s)):
    vs=[0]*27
    vs[i]= math.sqrt(s[i])
    s_list.append(vs)
s_matrix=np.matrix(s_list)

with open('model.index','w') as f1:
    json_u = json.dumps(users_index)
    json_i = json.dumps(item_index)
    f1.write(json_u)
    f1.write('\n')
    f1.write(json_i)
f1.close()
with open('model_avg.rating','w') as f2:
    json_item_rating=json.dumps(item_avg_rating_dict)
    json_user_rating = json.dumps(user_avg_rating_dict)
    f2.write(json_item_rating)
    f2.write('\n')
    f2.write(json_user_rating)
f2.close()
with open('model_user.svd','w') as f3:
    for u in U:
        f3.write(str(u[0]))
        for k in u[1:]:
            f3.write(','+str(k))
        f3.write('\n')
f3.close()
with open('model_s.svd', 'w') as f4:
    for s in s_matrix.A:
        f4.write(str(s[0]))
        for k in s[1:]:
            f4.write(','+str(k))
        f4.write('\n')
f4.close()
with open('model_item.svd', 'w') as f5:
    for v in V:
        f5.write(str(v[0]))
        for k in v[1:]:
            f5.write(','+str(k))
        f5.write('\n')
f5.close()

# print('svd')
