import logging
import os

from google.api_core.exceptions import AlreadyExists
from google.api_core.exceptions import BadRequest
from google.api_core.exceptions import Conflict
from google.api_core.exceptions import FailedPrecondition
from google.api_core.exceptions import NotFound
from google.cloud import storage
from google.cloud import storage_control_v2

from app.bot_ai.utils import extract_text_after_folders
from app.common.models import ErrorLogModel


class GCSManager:
    """
    Manages interactions with Google Cloud Storage (GCS), including creating buckets, folders, and uploading files.
    Also handles deletion and listing of files and folders in GCS.

    Attributes:
        storage_client (storage.Client): Google Cloud Storage client.
        storage_control_client (storage_control_v2.StorageControlClient): Google Cloud Storage control client for folder operations.

    Methods:
        create_bucket_hierarchical_namespace(bucket_name):
            Creates a bucket with hierarchical namespace enabled.
        create_folder(bucket_name, folder_name):
            Creates a folder inside the specified bucket.
        aditional_folders_for_company(bucket_name, company_folder, bucket_path):
            Creates additional folders such as "temporary" and "permanent" inside a company's folder.
        list_folders(bucket_name):
            Lists all folders inside a bucket.
        delete_folder(bucket_name, folder_name):
            Deletes a folder inside a bucket.
        delete_all_folders(bucket_name):
            Deletes all folders in a bucket.
        upload_file(bucket_name, source_file_name, destination_blob_name):
            Uploads a file to the specified bucket.
        list_files_in_folder(bucket_name):
            Lists all files inside a bucket.
        get_files_in_folder(bucket_name, company_folder, folder_type):
            Retrieves files inside a specified folder, optionally filtered by folder type.
        delete_file(bucket_name, file_url):
            Deletes a specified file (blob) from a bucket.
        delete_all_files(bucket_name):
            Deletes all files inside a bucket.
    """  # noqa: E501

    def __init__(self):
        """Initializes the GCSManager with Google Cloud Storage clients."""
        self.storage_client = storage.Client()
        self.storage_control_client = storage_control_v2.StorageControlClient()
        self.project_id = PROJECT_ID

    def create_bucket_hierarchical_namespace(self, bucket_name: str) -> None:
        """
        Creates a bucket with hierarchical namespace enabled.

        Args:
            bucket_name (str): The name of the GCS bucket to create.
        """
        bucket = self.storage_client.bucket(bucket_name)
        bucket.iam_configuration.uniform_bucket_level_access_enabled = True
        bucket.hierarchical_namespace_enabled = True
        try:
            bucket.create()
        except Conflict as e:
            ErrorLogModel.objects.create(
                app="bot_ai",
                function="create_bucket_hierarchical_namespace",
                error=f"Bucket error: {e}",
            )
        except BadRequest as e:
            ErrorLogModel.objects.create(
                app="bot_ai",
                function="create_bucket_hierarchical_namespace",
                error=f"Bucket name error: {e}",
            )
        except Exception as e:  # noqa: BLE001
            ErrorLogModel.objects.create(
                app="bot_ai",
                function="create_bucket_hierarchical_namespace",
                error=f"Bucket name error: {e}",
            )

    def create_folder(self, bucket_name: str, folder_name: str) -> None:
        """
        Creates a folder inside the specified GCS bucket.

        Args:
            bucket_name (str): The name of the GCS bucket.
            folder_name (str): The name of the folder to create.
        """
        storage_control_client = storage_control_v2.StorageControlClient()
        project_path = storage_control_client.common_project_path("_")
        bucket_path = f"{project_path}/buckets/{bucket_name}"

        request = storage_control_v2.CreateFolderRequest(
            parent=bucket_path,
            folder_id=folder_name,
        )

        try:
            storage_control_client.create_folder(request=request)
            self.aditional_folders_for_company(bucket_name, folder_name, bucket_path)
        except FailedPrecondition as e:
            ErrorLogModel.objects.create(
                app="bot_ai",
                function="create_folder",
                error=f"Error: {e}",
            )
        except AlreadyExists:
            logger.info("Folder already exists:")

    def aditional_folders_for_company(
        self,
        bucket_name: str,
        company_folder: str,
        bucket_path: str,
    ) -> None:
        """
        Creates additional folders for the company, such as "temporary" and "permanent".

        Args:
            bucket_name (str): The name of the GCS bucket.
            company_folder (str): The name of the company's folder.
            bucket_path (str): The path to the bucket.
        """
        storage_control_client = storage_control_v2.StorageControlClient()

        # Create "temporary" folder
        request = storage_control_v2.CreateFolderRequest(
            parent=bucket_path,
            folder_id=f"{company_folder}/temporary",
        )
        storage_control_client.create_folder(request=request)

        # Create "permanent" folder
        request = storage_control_v2.CreateFolderRequest(
            parent=bucket_path,
            folder_id=f"{company_folder}/permanent",
        )
        storage_control_client.create_folder(request=request)

    def list_folders(self, bucket_name: str) -> list:
        """
        Lists all folders inside a GCS bucket.

        Args:
            bucket_name (str): The name of the GCS bucket.

        Returns:
            list: A list of folder names in the bucket.
        """
        storage_control_client = storage_control_v2.StorageControlClient()
        project_path = storage_control_client.common_project_path("_")
        bucket_path = f"{project_path}/buckets/{bucket_name}"

        request = storage_control_v2.ListFoldersRequest(
            parent=bucket_path,
        )

        folders = []
        page_result = storage_control_client.list_folders(request=request)
        for folder in page_result:
            folder_name = extract_text_after_folders(folder.name)
            folders.append(folder_name)

        return folders

    def delete_folder(self, bucket_name: str, folder_name: str) -> None:
        """
        Deletes a folder inside a GCS bucket.

        Args:
            bucket_name (str): The name of the GCS bucket.
            folder_name (str): The name of the folder to delete.
        """
        storage_control_client = storage_control_v2.StorageControlClient()
        folder_path = storage_control_client.folder_path(
            project="_",
            bucket=bucket_name,
            folder=folder_name,
        )

        request = storage_control_v2.DeleteFolderRequest(
            name=folder_path,
        )

        try:
            storage_control_client.delete_folder(request=request)
        except NotFound as e:
            ErrorLogModel.objects.create(
                app="bot_ai",
                function="delete_folder",
                error=f"Error: {e}",
            )
        except FailedPrecondition as e:
            ErrorLogModel.objects.create(
                app="bot_ai",
                function="delete_folder",
                error=f"Error: {e}",
            )

    def delete_all_folders(self, bucket_name: str) -> None:
        """
        Deletes all folders inside a GCS bucket.

        Args:
            bucket_name (str): The name of the GCS bucket.
        """
        folders = self.list_folders(bucket_name)
        reversed_folders = folders[::-1]  # Reverse the list to delete sub-folders first

        for folder in reversed_folders:
            self.delete_folder(bucket_name, folder)

    def upload_file(
        self,
        bucket_name: str,
        source_file_name: str,
        destination_blob_name: str,
    ) -> None:
        """
        Uploads a file to the specified GCS bucket.

        Args:
            bucket_name (str): The name of the GCS bucket.
            source_file_name (str): The path to the file to upload.
            destination_blob_name (str): The name of the file in GCS.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Set generation-match precondition to avoid potential race condition
        generation_match_precondition = 0

        return blob.upload_from_filename(
            source_file_name,
            if_generation_match=generation_match_precondition,
        )

    def list_files_in_folder(self, bucket_name: str) -> list:
        """
        Lists all the files inside the folders of a bucket.

        Args:
            bucket_name (str): The name of the GCS bucket.

        Returns:
            list: A list of file names in the bucket.
        """
        files = self.storage_client.list_blobs(bucket_name)
        return [obj.name for obj in files]

    def get_files_in_folder(
        self,
        bucket_name: str,
        company_folder: str,
        folder_type="t",
    ) -> list:
        """
        Retrieves files inside a specified folder, optionally filtered by folder type.

        Args:
            bucket_name (str): The name of the GCS bucket.
            company_folder (str): The name of the company's folder.
            folder_type (str): The folder type to filter files ("t" for temporary, "p" for permanent).

        Returns:
            list: A list of file URLs in the folder.
        """  # noqa: E501
        files_list = self.list_files_in_folder(bucket_name)

        if folder_type == "t":
            folder_name = f"{company_folder}/temporary"
            files_list = [file for file in files_list if folder_name in file]
        elif folder_type == "p":
            folder_name = f"{company_folder}/permanent"
            files_list = [file for file in files_list if folder_name in file]
        else:
            files_list = [file for file in files_list if company_folder in file]

        prefix = f"gs://{self.project_id}/"
        return [prefix + file for file in files_list]

    def delete_file(self, bucket_name: str, file_url: str) -> None:
        """
        Deletes a blob (file) from the specified GCS bucket.

        Args:
            bucket_name (str): The name of the GCS bucket.
            file_url (str): The URL of the file to delete.

        Returns:
            None
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(file_url)

        # Reload blob to ensure we have up-to-date metadata for generation matching
        blob.reload()
        generation_match_precondition = blob.generation

        # Delete the file from the bucket, using generation match to avoid race conditions  # noqa: E501
        blob.delete(if_generation_match=generation_match_precondition)

    def delete_all_files(self, bucket_name: str) -> None:
        """
        Deletes all files inside the specified GCS bucket.

        Args:
            bucket_name (str): The name of the GCS bucket.

        Returns:
            None
        """
        files = self.list_files_in_folder(bucket_name)

        # Iterate over each file and delete it
        for file in files:
            self.delete_file(bucket_name, file)


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
