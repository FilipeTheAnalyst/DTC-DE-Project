from airflow import DAG
import logging
import os
from datetime import datetime
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from google.cloud import storage
from googleapiclient.discovery import build
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator, BigQueryInsertJobOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq

from pricetracker import check_target_price

# AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
AIRFLOW_DAGS = os.environ.get("AIRFLOW_DAGS", "/opt/airflow/dags/boardgamescraper")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'boardgame_data')
DATE_TEMPLATE = '{{ execution_date.strftime(\'%Y-%m-%d\') }}'
INGEST_ITEMS = ['boardgames', 'gamesprices']
# parquet_file = OUTPUT_GAMES_TEMPLATE.replace('.csv', '.parquet')
INPUT_PART = "raw"
INPUT_FILETYPE = 'csv'
OUTPUT_FILETYPE = 'parquet'

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

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

    for item in INGEST_ITEMS:
        ingest_items_task = BashOperator(
            task_id=f"ingest_{item}_task",
            bash_command=f'cd {AIRFLOW_DAGS} && scrapy crawl {item} -O {item}_{DATE_TEMPLATE}.{INPUT_FILETYPE}'
        )

        format_to_parquet_task = PythonOperator(
            task_id=f"format_{item}_to_parquet_task",
            python_callable=format_to_parquet,
            op_kwargs={
                "src_file": f"{AIRFLOW_DAGS}/{item}_{DATE_TEMPLATE}.{INPUT_FILETYPE}",
            },
        )

        local_to_gcs_task = PythonOperator(
            task_id=f"local_{item}_to_gcs_task",
            python_callable=upload_to_gcs,
            op_kwargs={
                "bucket": BUCKET,
                "object_name": f"{item}/{item}_{DATE_TEMPLATE}.{OUTPUT_FILETYPE}",
                "local_file": f"{AIRFLOW_DAGS}/{item}_{DATE_TEMPLATE}.{OUTPUT_FILETYPE}",
            },
        )

        bigquery_external_table_task = BigQueryCreateExternalTableOperator(
            task_id=f"bq_{item}_external_table_task",
            table_resource={
                "tableReference": {
                    "projectId": PROJECT_ID,
                    "datasetId": BIGQUERY_DATASET,
                    "tableId": f"{item}_external_table",
                },
                "externalDataConfiguration": {
                    "autodetect": "True",
                    "sourceFormat": f"{OUTPUT_FILETYPE.upper()}",
                    "sourceUris": [f"gs://{BUCKET}/{item}/*"],
                },
            },
        )

        CREATE_BQ_TBL_QUERY = (
            f'CREATE OR REPLACE TABLE {BIGQUERY_DATASET}.{item} \
            PARTITION BY date \
            AS \
            SELECT * FROM {BIGQUERY_DATASET}.{item}_external_table;'
        )

        # Create a partitioned table from external table
        bq_create_partitioned_table_job = BigQueryInsertJobOperator(
            task_id=f"bq_create_{item}_partitioned_table_task",
            configuration={
                "query": {
                    "query": CREATE_BQ_TBL_QUERY,
                    "useLegacySql": False,
                }
            }
        )

        ingest_items_task >> format_to_parquet_task >> local_to_gcs_task >> bigquery_external_table_task >> bq_create_partitioned_table_job

    check_price_task = PythonOperator(
        task_id=f"check_price_task",
        python_callable=check_target_price,
        op_kwargs=dict(
            email_user=EMAIL_USER,
            email_password=EMAIL_PASSWORD,
            prices_file=f"{AIRFLOW_DAGS}/{INGEST_ITEMS[1]}_{DATE_TEMPLATE}.{INPUT_FILETYPE}",
            wishlist_file=f"{AIRFLOW_DAGS}/boardgames_wishlist.{INPUT_FILETYPE}",
            execution_date=DATE_TEMPLATE
        )
    )

    bq_create_partitioned_table_job >> check_price_task
    