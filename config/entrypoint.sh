#!/bin/sh

echo "================ Initializing Airflow Database... ================"
airflow db init

airflow db migrate
echo "Your environment is ready."

airflow users create --username admin --firstname admin --lastname admin --role Admin --email admin@admin.com --password admin

# variables
echo "================ Importing variables... ================"
airflow variables import ./variables.json

# connections
echo "================ Importing connections... ================"
airflow connections import ./connections.json --overwrite

exec "${@}"