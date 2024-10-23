from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

default_args ={
    'owner': 'Saba',
    'start_date':"2024-09-17"
}

dag = DAG(
    dag_id="my_first_dag",
    description="This is my first dag",
    default_args=default_args,
    schedule_interval="@daily",
    dagrun_timeout=timedelta(minutes=5)
)

start_task = EmptyOperator(task_id='start_task',dag=dag)
hello_task = EmptyOperator(task_id='hello_task',dag=dag)
end_task = EmptyOperator(task_id='end_task',dag=dag)

start_task >> hello_task >> end_task