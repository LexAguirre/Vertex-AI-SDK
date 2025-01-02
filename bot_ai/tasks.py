import logging
import os
from pathlib import Path

from celery import shared_task

from app.bot_ai.bigquery import GCPBigQuery
from app.bot_ai.file_extractor import PDFExtractor
from app.bot_ai.gc_storage import GCSManager

logger = logging.getLogger(__name__)


def tasks_in_vertex(customer_name, customer_id):
    """
    Initializes the task to upload a CSV file to BigQuery in Vertex AI.

    Args:
        customer_name (str): The name of the customer.
        customer_id (int): The ID of the customer.
    """
    from_csv_to_bigquery_table.delay(customer_name, customer_id)


@shared_task
def from_csv_to_bigquery_table(customer_name, customer_id):
    """
    A Celery task that uploads CSV files to a Google Cloud Storage bucket, processes them, and uploads them to BigQuery.

    This function extracts customer data, splits a CSV file, uploads the split files to Google Cloud Storage (GCS), and then creates corresponding BigQuery tables. After processing, the temporary files are removed from GCS and BigQuery tables are fused together.

    Args:
        customer_name (str): The name of the customer.
        customer_id (int): The ID of the customer.

    Variables:
        file_name (str): The name of the CSV file being processed.
        bucket_name (str): The GCS bucket where the files are uploaded.
        gc_manager (GCSManager): Manages Google Cloud Storage operations.
        bq_manager (GCPBigQuery): Manages BigQuery operations.
        extract (PDFExtractor): Handles PDF extraction and data management.
        folder_name (str): The folder name created for the customer in GCS.
        ds_bq (bool): Indicates whether the BigQuery dataset creation was successful.
        files_list (list): A list of file paths to the split CSV files.
        files_name_list (list): A list of names for the split CSV files.
        fusion_query (str): The SQL query to fuse the split tables into a single BigQuery table.
        bucket_url (str): The GCS path for the uploaded CSV file.
        bucket_file_url (str): The full GCS URL for the uploaded CSV file.
    """  # noqa: E501
    file_name = "amazon_products"
    bucket_name = "dev_lumi_company_files"
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")

    gc_manager = GCSManager()
    bq_manager = GCPBigQuery()
    extract = PDFExtractor(customer_name, customer_id)

    # Manage the importation and create a folder in GCS
    extract.importation_manager()
    folder_name = extract.customer_folder()
    gc_manager.create_folder(bucket_name, folder_name)
    bq_manager.create_a_dataset(folder_name)

    # Split the CSV into multiple parts and process each file
    files_list, files_name_list = extract.split_csv(file_name)

    if len(files_list) == 1:
        bucket_url = f"{folder_name}/temporary/{files_name_list[0]}.csv"
        bucket_file_url = f"gs://{bucket_name}/{bucket_url}"

        gc_manager.upload_file(bucket_name, files_list[0], bucket_url)

        bq_manager.create_table_from_file(
            folder_name,
            bucket_file_url,
            files_name_list[0],
        )
        return

    fusion_query = f"CREATE TABLE {project_id}.{folder_name}.{file_name} AS"

    for file_url, file_name_in_list in zip(files_list, files_name_list, strict=False):
        logger.info(f"Uploading {file_name_in_list} to BigQuery")  # noqa: G004
        bucket_url = f"{folder_name}/temporary/{file_name_in_list}.csv"
        bucket_file_url = f"gs://{bucket_name}/{bucket_url}"

        # Upload file to GCS
        gc_manager.upload_file(bucket_name, file_url, bucket_url)

        # Remove the local file
        Path(file_url).unlink()

        # Create BigQuery table from the uploaded file
        bq_manager.create_table_from_file(
            folder_name,
            bucket_file_url,
            file_name_in_list,
        )

        # Delete the uploaded file from GCS after processing
        gc_manager.delete_file(bucket_name, bucket_url)

        # Append SQL for table fusion
        if file_name_in_list == files_name_list[-1]:
            fusion_query += f"""
            SELECT * FROM `{project_id}.{folder_name}.{file_name_in_list}`;"""  # noqa: S608
            break

        fusion_query += f"""
        SELECT * FROM `{project_id}.{folder_name}.{file_name_in_list}`
        UNION ALL"""  # noqa: S608

    # Fuse the table parts into one
    bq_manager.fuse_table_parts(fusion_query)

    # Delete temporary tables
    for file_name_in_list in files_name_list:
        bq_manager.delete_table(folder_name, file_name_in_list)
