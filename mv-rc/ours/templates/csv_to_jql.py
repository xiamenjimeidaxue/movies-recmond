from sqlalchemy import create_engine
import pandas as pd
def save_csv(csv_file):
    engine=create_engine('mysql+pymysql://root:123456@192.168.187.128:3306/movies')
    data=pd.read_csv(csv_file)
    data.to_sql('tags',engine,chunksize=10000,index=None)
if __name__ == '__main__':
    save_csv('/home/hadoop/Desktop/ours/ml-latest-small/tags.csv')