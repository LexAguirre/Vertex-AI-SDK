import logging
import os

from django.conf import settings
from google.api_core.exceptions import Conflict
from google.cloud import bigquery
from google.oauth2 import service_account

from app.common.models import ErrorLogModel

logger = logging.getLogger(__name__)


class GCPBigQuery:
    """
    A class to manage operations related to Google Cloud BigQuery.
    It provides functionality to create datasets, models, tables, and manage BigQuery queries and jobs.
    """  # noqa: E501

    def __init__(self):
        """
        Initializes the GCPBigQuery class with a BigQuery client and some default configurations for dataset, connection, and table IDs.
        """  # noqa: E501
        self.location = LOCATION
        self.client = bigquery.Client()

        # Default dataset, connection, and table settings
        self.project_id = PROJECT_ID
        self.connection_id = f"{self.project_id}.us.emb_conn_lumi"
        self.model_type = "multimodalembedding"
        self.table_id = "store_embeddings"

    def create_a_dataset(self, dataset_name):
        """
        Creates a BigQuery dataset with the specified dataset name.

        Args:
            dataset_name (str): The name of the dataset to create.

        Returns:
            bool or str: Returns True if the dataset was created successfully, 'exists' if it already exists, and False if an error occurred.
        """  # noqa: E501
        dataset_id = f"{self.client.project}.{dataset_name}"
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"

        try:
            dataset = self.client.create_dataset(
                dataset,
                timeout=30,
            )  # Request to create the dataset.
        except Conflict as e:
            ErrorLogModel.objects.create(
                app="bigquery",
                function="create_a_dataset",
                error=f"Error: {e}",
            )
            return "exists"
        except Exception as e:  # noqa: BLE001
            ErrorLogModel.objects.create(
                app="bigquery",
                function="create_a_dataset",
                error=f"Error: {e}",
            )
            return False
        return True

    def create_a_model_in_dataset(self, dataset_name):
        """
        Creates or replaces a model within the dataset using a predefined connection. This model is of type 'multimodalembedding'.
        """  # noqa: E501
        query = f"""
            CREATE OR REPLACE MODEL `{self.project_id}.{dataset_name}.{self.model_type}`
            REMOTE WITH CONNECTION `{self.connection_id}`
            OPTIONS(ENDPOINT = 'multimodalembedding@001');
        """
        self.client.query_and_wait(query)  # Execute the query to create the model.

    def create_external_table(self, dataset_name, files_list, files_table_name):
        """
        Creates or replaces an external table in BigQuery from a list of files.

        Args:
            files_list (list): A list of file URIs to use as external table sources.
            image_table_name (str): The name of the external table to create.
        """
        files_table_name = f"{files_table_name}_files"
        query = f"""
            CREATE OR REPLACE EXTERNAL TABLE `{self.project_id}.{dataset_name}.{files_table_name}`
            WITH CONNECTION `{self.connection_id}`
            OPTIONS(
            object_metadata = `SIMPLE`,
            uris = {files_list}
            );
        """  # noqa: E501
        self.client.query_and_wait(
            query,
        )  # Execute the query to create the external table.

        return files_table_name

    def generate_embeddings(self, dataset_name, image_table_name, embb_table_name):
        """
        Generates embeddings from an external table using a machine learning model in BigQuery.

        Args:
            image_table_name (str): The external table containing images.
            embb_table_name (str): The name of the table where the embeddings will be stored.
        """  # noqa: E501
        # TODO: FIX POSSIBLE SQL INJECTION S608
        embb_table_name = f"{embb_table_name}_embeddings"
        query = rf"""
            CREATE OR REPLACE TABLE `{self.project_id}.{dataset_name}.{embb_table_name}` AS (
                SELECT *,
                    REGEXP_EXTRACT(uri, r'[^/]+$') AS obj_name,
                    REGEXP_REPLACE(
                        REGEXP_EXTRACT(uri, r'[^/]+$'),
                        r'\\.png$', ''
                    ) AS sku_id,
                    '' AS product_name
                FROM ML.GENERATE_EMBEDDING(
                    MODEL `{self.project_id}.{dataset_name}.{self.model_type}`,
                    TABLE `{self.project_id}.{dataset_name}.{image_table_name}`
                )
            );
        """  # noqa: S608 , E501

        self.client.query_and_wait(query)  # Execute the query to generate embeddings.
        return embb_table_name

    def create_table_from_file(self, folder_name, bucket_url, file_name):
        """
        Creates a BigQuery table by loading data from a file in Google Cloud Storage.

        Args:
            folder_name (str): The name of the folder in BigQuery.
            bucket_url (str): The URL of the file in Google Cloud Storage.
            file_name (str): The name of the file (table) in BigQuery.
        """
        table_id = f"{self.project_id}.{folder_name}.{file_name}"

        job_config = bigquery.LoadJobConfig(
            autodetect=True,
            skip_leading_rows=1,
            source_format=bigquery.SourceFormat.CSV,
        )

        load_job = self.client.load_table_from_uri(
            bucket_url,
            table_id,
            job_config=job_config,
        )
        load_job.result()  # Wait for the job to complete.

    def delete_table(self, folder_name, file_name):
        """
        Deletes a table in BigQuery.

        Args:
            folder_name (str): The name of the folder containing the table.
            file_name (str): The name of the table to delete.
        """
        table_id = f"{self.project_id}.{folder_name}.{file_name}"
        self.client.delete_table(
            table_id,
            not_found_ok=True,
        )  # Delete the table if it exists.

    def fuse_table_parts(self, fuse_query):
        """
        Executes a query to fuse (combine) multiple table parts into a single table in BigQuery.

        Args:
            fuse_query (str): The SQL query to fuse the table parts.
        """  # noqa: E501
        query = rf"""
            {fuse_query}
        """
        self.client.query_and_wait(query)  # Execute the query to fuse tables.


# Credentials and project configuration
DIR_CREDENTIALS = settings.BASE_DIR / "clave.json"
CREDENTIALS = service_account.Credentials.from_service_account_file(DIR_CREDENTIALS)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = "us-central1"
