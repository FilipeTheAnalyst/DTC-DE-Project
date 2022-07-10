from airflow import DAG
import logging
import os
from datetime import datetime
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from google.cloud import storage
from googleapiclient.discovery import build
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq

# AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
AIRFLOW_DAGS = os.environ.get("AIRFLOW_DAGS", "/opt/airflow/dags/boardgamescraper/")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'boardgame_data')
OUTPUT_FILE_TEMPLATE = 'boardgames_{{ execution_date.strftime(\'%Y-%m-%d\') }}.csv'
parquet_file = OUTPUT_FILE_TEMPLATE.replace('.csv', '.parquet')

def format_to_parquet(src_file):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    table = pv.read_csv(src_file)
    pq.write_table(table, src_file.replace('.csv', '.parquet'))

def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)

local_workflow = DAG(
    dag_id="boardgame_ingestion_dag",
    schedule_interval="@daily",
    start_date = datetime(2022, 7, 9),
     max_active_runs=1,
    tags=['de-project']
)

with local_workflow:

    ingest_api_task = BashOperator(
        task_id="ingest_boardgame_task",
        bash_command=f'cd {AIRFLOW_DAGS} && scrapy crawl boardgames -O {OUTPUT_FILE_TEMPLATE}'
    )

    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet_task",
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": f"{AIRFLOW_DAGS}/{OUTPUT_FILE_TEMPLATE}",
        },
    )

    local_to_gcs_task = PythonOperator(
        task_id="local_to_gcs_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw/{parquet_file}",
            "local_file": f"{AIRFLOW_DAGS}/{parquet_file}",
        },
    )

    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/raw/{parquet_file}"],
            },
        },
    )


    ingest_api_task >> format_to_parquet_task >> local_to_gcs_task >> bigquery_external_table_task