# projects_2020-2021

# 电影特征分析
(1) Using Python which I have learned in class to scrape information from websites

(2) Learning how to use official API to extract data from websites.

(3) Processing data types and values, and merge data together.

(4) Analyzing processed data to find which features have greater effect on audiences’ score or professional score
and to get new components and their information values by using PCA algorithm.

(5) Visualizing the results in some graphs.

# 课程图谱
Freshmen who have just entered the university do not know very well about the course, skill and occupation. So we want to develop an app to help them.

If they input their favorite occupations, the web app can automatically show the course resources they need to learn, the order of course learning, and course-related skills. 

If they input the skills they want to learn, the app can display relevant course resources and jobs that require these skills. Finally, the app can display all courses and their studying orders.

# 信用卡预测模型
We apply the decision tree algorithm to the problem of credit card approval prediction. The problem of credit card approval is a common problem in banks. The bank staff always need to evaluate customers' credit and our model helps them assess. 

In the prediction model, there are two steps to achieve. In the first step, the preprocessing step analysis depends on each variable’s characteristics rather than complete reunification. The preprocessing includes dropping some outliers and cutting some unrelated factors to analyze factors one by one.

Due to our data being discrete in categorical, we divide them into some categories to decide the branches easily so that it is convenient to build a decision tree. Based on related research and personal experience, the decision tree is a good choice for these data.

# yelp推荐系统
Programming Requirements

a. You must use Python & Spark to implement all tasks. You can only use the standard Python libraries (i.e., external libraries like numpy or pandas are not allowed).

b. You are required to only use Spark RDD, i.e. no point if using Spark DataFrame or DataSet.

task1: you will implement the Min-Hash and Locality Sensitive Hashing algorithms with Jaccard similarity to find similar business pairs in the train_review.json file. We focus on 0/1 ratings rather than the actual rating values in the reviews. In other words, if a user has rated a business, the user’s contribution in the characteristic matrix is 1; otherwise, the contribution is 0 (Table 1). Your task is to identify business pairs whose Jaccard similarity is >= 0.05.

task2: you will build a content-based recommendation system by generating profiles from review texts for users and businesses in the train_review.json file. Then you will use the model to predict if a user prefers to review a given business by computing the cosine similarity between the user and item profile vectors.

task3: you will build collaborative filtering (CF) recommendation systems using the train_review.json file. After building the systems, you will use the systems to predict the ratings for a user and business pair. You are required to implement 2 cases:

• Case 1: Item-based CF recommendation system

• Case 2: User-based CF recommendation system with Min-Hash LSH 
