# pymysql用connect方法进行连接
import pymysql

conn = pymysql.connect(
    host="localhost",  # 数据库主机地址
    port=3306,         # 数据库端口号
    user="root",       # 数据库用户名
    password="123456", # 数据库密码
    database="movies", # 要连接的数据库名称
    charset="utf8mb4"  # 指定字符集
)

def con_my_sql(sql_code):
    try:
        conn.ping(reconnect=True)  # 保证数据库连接正常
        print(sql_code)
        # 通过游标对象对数据库服务器发出sql语句
        cursor = conn.cursor(pymysql.cursors.DictCursor)  # 返回数据是字典形式，而不是数组
        cursor.execute(sql_code)
        # 提交
        conn.commit()
        # 关闭连接
        conn.close()
        return cursor  # 普通执行返回cursor就是执行成功

    except pymysql.MySQLError as err_message:
        # 回滚
        conn.rollback()
        # 关闭连接
        conn.close()
        return type(err_message), err_message

# username = "张三"
# pwd = 'APTX4869'
# code = "INSERT INTO `login_user` (`username`, `password`) VALUES ('%s', '%s')" % (username, pwd)
# print(con_my_sql(code))
# username = "张三"
# code = "SELECT * FROM login_user"
# cursor_ans = con_my_sql(code)
# print(cursor_ans.fetchall())  # 查询测试
