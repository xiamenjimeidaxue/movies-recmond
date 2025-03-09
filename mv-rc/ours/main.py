from os import path
from pathlib import Path
from test import con_my_sql
from flask import Flask, jsonify, render_template,request
from flask_frozen import Freezer
from flask import redirect, url_for
from flask import  session
import time
from movie_recommend import RecommendationEngine
from pyspark import SparkContext,SparkConf
import random
import json
def start(data1):
    conf = SparkConf()
    conf.set("spark.hadoop.fs.defaultFS", "file:///")
    sc = SparkContext.getOrCreate(conf)
    global movie_recommender
    global index_
    index_ = 0
    # 这个位置把导出的数据写入csv文件
    data1_path="ml-latest-small/ratings.csv"
    # data1=[]

    # # data是数据源，filepath是要写入的路径，注意后面取文件的位置应该相同
    movie_recommender = RecommendationEngine(sc, data1_path)
    movie_recommender.write_to_csv(data1,data1_path)

def home():
    movies_top10 = movie_recommender.top_10_popular_movies()
    print("top_10:")
    for values in movies_top10:
        print(values)

def train_and_prediction_model(usrId,data2):
    data2_path="data/data2.csv"
    data1=movie_recommender.ratings_RDD
    movie_recommender.write_to_csv(data2,data2_path)
    # the path save data2
    data2 = movie_recommender.loadRating(data2_path)
    movie_recommender.train_and_save_model(data1,data2)
    recommends = movie_recommender.model_prediction(data1,usrId)
    print("movieId:")
    for value in recommends:
        print(value)
    return recommends

app = Flask(__name__)
app.secret_key = '112233'

@app.route("/")
def index_login():
    return render_template('index.html')

@app.route("/back_to_index")
def back_to_index():
    return render_template('index.html')

@app.route("/error1")
def error1():
    return render_template('error1.html')
@app.route("/error2")
def error2():
    return render_template('error2.html')
@app.route("/success")
def success():
    return render_template('success.html')

# @app.route("/register")
# def index_register():
#     return render_template('register.html')

# login_data = {
#     "张三": "123456"
# }

@app.route("/login", methods=["post"])
def login():
    # name = request.form.get("username")
    # pwd = request.form.get("password")
    #
    # return f"{name},{pwd}"
    name = request.form.get("username")
    pwd = request.form.get("password")
    code = "select * from users where username='%s'" % (name)
    cursor_ans = con_my_sql(code)
    cursor_select = cursor_ans.fetchall()
    if len(cursor_select)>0:
        if pwd == cursor_select[0]['password']:
            session['user_id'] = cursor_select[0]['userId']
            session['username']= cursor_select[0]['username']
            return redirect(url_for('zhanshi'))
        else:
            return render_template('error1.html')
    else:
        return render_template('error1.html')

@app.route("/register", methods=["post"])
def register():
    name = request.form.get("username")
    pwd = request.form.get("password")
    code = "select * from users where username='%s'" % (name)
    cursor_ans = con_my_sql(code)
    cursor_select = cursor_ans.fetchall()
    if len(cursor_select)>0:
        return render_template('error2.html')
    else:
        code = "insert into `users` (`username` , `password`) values ('%s' , '%s')" % (name, pwd)
        con_my_sql(code)
        return render_template('success.html')

@app.route("/vote",methods=["POST","GET"])
def vote():
    movies=[]
    usrid=session.get('user_id')
    temp=0
    while True:
        if temp==5:
            break
        query="select * from movie ORDER BY RAND() LIMIT 1"
        get1=con_my_sql(query)
        get2=get1.fetchall()
        query="select COUNT(*) from ratings where (userId,movieId) = (%s,%s)" % (usrid,get2[0]['movieId'])
        uu=con_my_sql(query)
        count=uu.fetchone()
        if count['COUNT(*)']>0:
            continue
        if temp==0:
            movies=movies+get2
            temp=temp+1
            continue
        judge=0
        for i in range(temp):
            if movies[i]['movieId']==get2[0]['movieId'] :
                judge=1
        if judge :
            continue
        temp=temp+1
        movies=movies+get2
    return render_template('vote.html',movies=movies)


@app.route("/submit_vote", methods=["POST"])
def submit_vote():
    card_id = request.form.get("card_id")  # 假设你有一个用户ID字段
    vote = request.form.get("vote")  # 获取vote值
    timestamp = int(time.time())
    user_id = session.get('user_id')
    code = "INSERT INTO ratings (`userId`,`movieId`, `rating`,`timestamp`) VALUES (%s, %s, %s,%s)" % (user_id,card_id,vote,timestamp)
    cursor_ans = con_my_sql(code)

    if cursor_ans:
        return '成功'
    else:
        return '失败'

@app.route("/submit_all_votes", methods=["POST"])
def submit_all_votes():
    # 直接从请求中获取JSON数据
    vote_data = request.get_json()
    print("Received vote data:", vote_data)  # 打印获取到的voteData以便调试

    if not vote_data:
        return jsonify({"error": "No vote data provided"}), 400

    user_id = session.get('user_id')
    timestamp = int(time.time())

    # 遍历vote_data列表并执行数据库插入操作
    for score, card_id in vote_data:
        code = "INSERT INTO `ratings` (`userId`, `movieId`, `rating`, `timestamp`) VALUES (%s, %s, %s, %s)"%(user_id, card_id, score, timestamp)
        cursor_ans = con_my_sql(code)

        if not cursor_ans:
            return '失败', 500

    return '成功', 200
# @app.route("/movie_recommend")
# def movie_recommend():
#     connection = con_my_sql("SELECT * FROM movie_recommend")
#     movies = connection.fetchall() if connection else []
#     print(1)

#     # print(connection.fetchall())
#     return render_template('movie_recommend.html', movies=movies)

@app.route("/test")
def test():
     return render_template('test.html')
@app.route("/zhanshi")
def zhanshi():
    judge=1
    user_id = session.get('user_id')
    username=session.get('username')
    if user_id is None:
        judge=0
    query = "SELECT COUNT(*) FROM ratings WHERE userId = %s" % (user_id)
    cursor = con_my_sql(query)
    count_result = cursor.fetchone()
    print(count_result['COUNT(*)'])
    if count_result['COUNT(*)'] > 0 & judge:
        the_data = "SELECT * FROM ratings WHERE userId != %s  ORDER BY RAND() LIMIT 5000" % (user_id)
        rating1 = con_my_sql(the_data)
        rs1=rating1.fetchall()
        user_data="SELECT * FROM ratings WHERE userId = %s" % user_id
        rating2=con_my_sql(user_data)
        rs2=rating2.fetchall()
        start(rs1)
        values=train_and_prediction_model(user_id,rs2)
        print(values)
        if len(values) >= 5:
            results = random.sample(values, 5)
        else:
            print("列表中的元素数量不足以抽取5个样本。")
        movies_a=[]
        for result in results:
            words="SELECT * FROM movie WHERE movieId = %s" % (result)
            check_num=con_my_sql(words)
            check=check_num.fetchall()
            movies_a=movies_a+check
        return render_template('zhanshi.html', movies_a=movies_a,username=username)


    else:
        connection_a = con_my_sql("SELECT * FROM movie WHERE movieId BETWEEN 1 AND 5")
        movies_a = connection_a.fetchall() if connection_a else []
        print(movies_a)
        # 渲染模板并传递两个类别的电影数据
        #return redirect(url_for('lunbo'))
        #return render_template('lunbo.html', movies_a=movies_a)
        return render_template('zhanshi.html', movies_a=movies_a,username=username)
if __name__ == '__main__':
    app.run(debug=True)
    # username = "张三"
    # code = "SELECT * FROM login_user"
    # cursor_ans = con_my_sql(code)
    # print(cursor_ans.fetchall())

