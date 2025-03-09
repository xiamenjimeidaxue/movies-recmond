from movie_recommend import RecommendationEngine
from pyspark import SparkContext,SparkConf


def start():
    conf = SparkConf()
    conf.set("spark.hadoop.fs.defaultFS", "file:///")
    sc = SparkContext.getOrCreate(conf)
    global movie_recommender
    global index_
    index_ = 0
    # 这个位置把导出的数据写入csv文件
    data1_path="ratings.csv"
    # data1=[]
    # # # data是数据源，filepath是要写入的路径，注意后面取文件的位置应该相同
    movie_recommender = RecommendationEngine(sc, data1_path)
    # movie_recommender.write_to_csv(data1, data1_path)

def home():
    movies_top10 = movie_recommender.top_10_popular_movies()
    print("top_10:")
    for values in movies_top10:
        print(values)

def train_and_prediction_model():
    usrId=10
    data2_path="data2.csv"
    data1=movie_recommender.ratings_RDD
    # movie_recommender.write_to_csv(data2,data2_path)
    # the path save data2
    data2 = movie_recommender.loadRating(data2_path)
    # movie_recommender.train_and_save_model(data1,data2)
    recommends = movie_recommender.model_prediction(data1,usrId)
    print("movieId:")
    for value in recommends:
        print(value)

if __name__ == "__main__":
    start()
    # home()
    train_and_prediction_model()

