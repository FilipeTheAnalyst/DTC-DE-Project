from airflow import DAG

import os
from datetime import datetime
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from google.cloud import storage
from googleapiclient.discovery import build
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator

AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
AIRFLOW_DAGS = os.environ.get("AIRFLOW_DAGS", "/opt/airflow/dags/")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'youtube_data')
FILES = {'channels': 'channels_' + datetime.now().strftime('%Y-%m-%d')+'.parquet', 
        'videos': 'videos_' + datetime.now().strftime('%Y-%m-%d')+'.parquet'}


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
    dag_id="youtube_ingestion_dag",
    schedule_interval="@daily",
    start_date = datetime(2022, 6, 6)
)

with local_workflow:

    ingest_api_task = BashOperator(
        task_id="ingest_api_task",
        bash_command=f'python {AIRFLOW_DAGS}ingest_youtube.py'
    )
    for bq_table, file in FILES.items():
        channel_to_gcs_task = PythonOperator(
            task_id=f"channel_to_gcs_task_{bq_table}",
            python_callable=upload_to_gcs,
            op_kwargs={
                "bucket": BUCKET,
                "object_name": f"youtube/{file}",
                "local_file": f"{AIRFLOW_HOME}/{file}",
            },
        )

        bigquery_youtube_table_task = BigQueryCreateExternalTableOperator(
            task_id=f"bigquery_youtube_table_task_{bq_table}",
            table_resource={
                "tableReference": {
                    "projectId": PROJECT_ID,
                    "datasetId": BIGQUERY_DATASET,
                    "tableId": bq_table,
                },
                "externalDataConfiguration": {
                    "sourceFormat": "PARQUET",
                    "sourceUris": [f"gs://{BUCKET}/youtube/{file}"],
                },
            },
        )

        ingest_api_task >> channel_to_gcs_task >> bigquery_youtube_table_task