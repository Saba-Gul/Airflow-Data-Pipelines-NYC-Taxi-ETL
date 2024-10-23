from airflow import DAG
from datetime import timedelta
from airflow.operators.python import PythonOperator
from airflow.models import variable
import os.path
import wget
import pandas as pd

import psycopg2
from sqlalchemy import create_engine

URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"
#URL=variable.get('taxi_url')

# Postgress sql database connection setting
DB_settings={
    'dbname':'airflow',
    'user':'airflow',
    'password':'airflow',
    'host':'db',
    'port':'5432'
}

default_args={
    'owner': 'Saba',
    'start_date': '2024-10-20',
    'retries': 2,
    'retry_delay': timedelta(minutes=10)
}

def extract_data(
    url:str,
    date:str   
)->bool:
    data_dir='/opt/airflow/data'
    file_path=f'{data_dir}/data_{date}.parquet'
    print(date)
    print(file_path)
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    if not os.path.exists(file_path):
        return False
    
    wget.download(url, file_path) 
    return True   

def transform_data(
    date:str
    
)->None:
   df=pd.read_parquet(f'/opt/airflow/data/data_{date}.parquet')
   
   # calculate the trip duration
   df['trip_duration']=(df['tpep_dropoff_datetime']-df['tpep_pickup_datetime']).dt.total_seconds()
   
   # calculate the average trip speed
   df['average_speed'] = df['trip_distance'] / (df['trip_duration'] /3600)
   
   # Filter Records
   df = df[(df['average_speed'] <= 60) & (df['average_speed'] >= 4*3600)] 
   
   # save as csv
   df.to_csv(f'/opt/airflow/data/data_{date}.csv', index=False)

def load_data(
    date:str)->None:
    
    conn = psycopg2.connect(**DB_settings)
    
    engine=create_engine(
        f"postgresql://{DB_settings['user']}:{DB_settings['password']}@{DB_settings['host']}:{DB_settings['port']}/{DB_settings['dbname']}"  
    )
    
    chnksize=50000
    for chunk in pd.read_csv(filepath_or_buffer=f'/opt/airflow/data/data_{date}.csv', chunksize=chnksize):
        chunk.to_sql("taxi_trips",engine, if_exists="append",index=False)
    engine.dispose()
    conn.close()

with DAG(dag_id="nyc_taxi_data_dump_dag",
         description="Extract NYC taxi data",
         default_args=default_args,
         schedule_interval="@monthly",
         dagrun_timeout=timedelta(minutes=15)
         ):
    PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
        op_kwargs={
            'url': URL,
            'date': "{{(execution_date).format('YYYY-MM')}}"
        }
    ) >>  PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
        op_kwargs={
            
            'date': "{{(execution_date).format('YYYY-MM')}}"
        }
    ) >>  PythonOperator(
        task_id="load_data",
        python_callable=load_data,
          op_kwargs={
            
            'date': "{{(execution_date).format('YYYY-MM')}}"
        }
    ) 
 