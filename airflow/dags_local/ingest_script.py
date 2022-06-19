import os
import pyarrow.parquet as pq
import pandas as pd
from sqlalchemy import create_engine
from time import time


def ingest_callable(user, password, host, port, db, table_name, parquet_file, execution_date):
    print(table_name, parquet_file, execution_date)

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()

    print('connection established successfully, inserting data...')
    
    t_start = time()
    parquet_table = pq.read_table(parquet_file)
    df = parquet_table.to_pandas()

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    df.to_sql(name="yellow_taxi_data", con=engine, if_exists='append')
    t_end = time()
    print('inserted the data, took %.3f seconds' % (t_end - t_start))

