FROM apache/airflow

ENV APP_HOME="/opt"

# Install Airflow
ENV AIRFLOW_HOME="${APP_HOME}/airflow"

COPY requirements.txt ${AIRFLOW_HOME}/requirements.txt

RUN python3 -m pip install --no-cache-dir --upgrade pip; \
    python3 -m pip install --no-cache-dir -r ${AIRFLOW_HOME}/requirements.txt

# Setup Airflow
WORKDIR ${AIRFLOW_HOME}

COPY config/entrypoint.sh ${APP_HOME}
COPY dags ${AIRFLOW_HOME}/dags
COPY plugins ${AIRFLOW_HOME}/plugins

RUN cp ${APP_HOME}/entrypoint.sh /entrypoint


# ENTRYPOINT [ "/opt/entrypoint.sh" ]