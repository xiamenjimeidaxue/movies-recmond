import os
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.ml.recommendation import ALS
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark import SparkConf, SparkContext
from pyspark.ml.recommendation import ALSModel
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import csv

class RecommendationEngine:
    def __init__(self, sc, data_path):
        self.spark = SparkSession(sc)
        self.data_path = data_path
        self.alsExplicit = ALS(userCol="userId", itemCol="movieId", ratingCol="rating", coldStartStrategy="drop")
        self.alsImplicit = ALS(userCol="userId", itemCol="movieId", ratingCol="rating", implicitPrefs=True,
                               coldStartStrategy="drop")
        # Load ratings data for later use
        self.ratings_RDD = self.loadRating(data_path)
        # Pre-calculate movies ratings counts
        self.cal_Average_Rating()

    def cal_Average_Rating(self):
        self.rating_group = self.ratings_RDD.map(lambda x: (x[1], x[2])).groupByKey()
        self.movie_average_rating_count = self.rating_group.map(
            lambda x: (x[0], float(sum(w for w in x[1])) / len(x[1]), len(x[1])))

    def top_10_popular_movies(self, number=10):
        # 将 movie_average_rating_count 转换为 (movie_id, (average_rating, rating_count)) 形式
        a = self.movie_average_rating_count.map(lambda x: (x[0], (x[1], x[2])))
        # 提取 (movie_id, rating_count)
        c = a.map(lambda x: (x[0], x[1][1]))
        # 按 rating_count 降序排序并取前 number 个
        d = c.takeOrdered(number, key=lambda x: -x[1])
        # 提取电影 ID
        top_movie_ids = [x[0] for x in d]
        return top_movie_ids

    def loadRating(self, path):
        ratings_raw_RDD = self.spark.sparkContext.textFile(path)
        # 获取文件头
        ratings_raw_data_header = ratings_raw_RDD.take(1)[0]
        # 过滤掉文件头
        ratings_data_RDD = ratings_raw_RDD.filter(lambda line: line != ratings_raw_data_header)
        # 随机选取 5000 行数据
        sample_fraction = 5000.0 / ratings_data_RDD.count()
        sampled_RDD = ratings_data_RDD.sample(withReplacement=False, fraction=sample_fraction, seed=42)
        # 解析数据
        self.ratings_RDD = sampled_RDD.map(lambda line: line.split(",")).map(
            lambda tokens: (int(tokens[0]), int(tokens[1]), float(tokens[2]))
        ).cache()
        return self.ratings_RDD

    def train_and_save_model(self,training_RDD,user_RDD,ifoptimized=False):
        combined_RDD = training_RDD.union(user_RDD)
        training_df = self.spark.createDataFrame(combined_RDD, ["userId", "movieId", "rating"])
        train_df, prediction_df = training_df.randomSplit([0.9, 0.1], seed=42)
        if ifoptimized:
            # 创建参数网格
            paramGrid = ParamGridBuilder() \
                .addGrid(self.alsExplicit.maxIter, [5, 10]) \
                .addGrid(self.alsExplicit.regParam, [0.01, 0.1]) \
                .build()
            # 创建评估器
            evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
            # 创建交叉验证器
            cv = CrossValidator(estimator=self.alsExplicit, estimatorParamMaps=paramGrid, evaluator=evaluator,
                                numFolds=5)
            # 训练显式反馈模型
            cv_model = cv.fit(training_df)
            # 使用最佳模型进行预测
            modelExplicit = cv_model.bestModel
        else:
            # 训练显式反馈模型
            modelExplicit = self.alsExplicit.fit(training_df)
        predictionsExplicit = modelExplicit.transform(prediction_df)
        # 保存模型
        modelExplicit.write().overwrite().save("model/explicit")

    def model_prediction(self, training_RDD, usrId):
        training_df = self.spark.createDataFrame(training_RDD, ["userId", "movieId", "rating"])
        # 1. 替换 userId 为指定的 usrId
        prediction_df = training_df.withColumn("userId", F.lit(usrId))
        # 2. 去重 movieId
        prediction_df = prediction_df.dropDuplicates(["movieId"])
        # 3. 按 rating 降序排序并限制结果为 500 条
        # prediction_df = prediction_df.orderBy("rating", ascending=False).limit(500)
        prediction_df = prediction_df.limit(500)

        modelExplicit = ALSModel.load("model/explicit")
        predictionsExplicit = modelExplicit.transform(prediction_df)
        # 获取前 20 个预测结果
        userid_fixed = usrId
        # 过滤出特定用户的数据
        user_predictions = predictionsExplicit.filter(predictionsExplicit.userId == userid_fixed)
        # 按预测值降序排序并限制结果为前20条
        top_20_predictions = user_predictions.orderBy("prediction", ascending=False).limit(20)
        recommends = [row.movieId for row in top_20_predictions.collect()]
        return recommends

    def write_to_csv(self,data, file_path):
        headers = data[0].keys()
        # 打开文件，使用 'w' 模式写入
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            # 写入表头
            writer.writeheader()
            # 写入数据
            for row in data:
                writer.writerow(row)
