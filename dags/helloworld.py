from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def helloWorld():
    print('Hello World')


with DAG(dag_id="hello_world_dag",
         start_date=datetime(2023, 9, 29),
         schedule_interval="@hourly",
         catchup=False) as dag:
    PythonOperator(
        task_id="hello_world",
        python_callable=helloWorld)
