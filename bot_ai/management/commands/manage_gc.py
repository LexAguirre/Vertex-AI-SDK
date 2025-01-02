import sys

from django.core.management import BaseCommand

from app.bot_ai.gc_storage import GCSManager


class Command(BaseCommand):
    """
    This class provides a Django management command to interact with Google Cloud Storage (GCS).
    It allows users to manage GCS resources, such as creating/deleting buckets, listing files/folders,
    and uploading files, all through an interactive menu.
    """  # noqa: E501

    help = "Ejecuta el asistente para el manejo del bucket en Google Cloud Storage"

    def handle(self, *args, **options):
        """
        The main entry point for the command. It initializes the GCSManager and runs an interactive loop
        where the user can select various GCS actions like listing, deleting, creating resources,
        or uploading files.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.
        """  # noqa: E501
        gc_manager = GCSManager()
        bucket_name = "dev_lumi_company_files"
        status = True

        # Interactive loop to choose actions for GCS management
        while status:
            self.print_menu(bucket_name)

            try:
                action = int(input("Enter the number of the action: "))
            except ValueError:
                print("Invalid input. Please enter a number.")  # noqa: T201
                continue

            if action == 0:
                bucket_name = input("Enter the name of the bucket: ")
            elif action == 1:
                self.handle_delete_options(gc_manager, bucket_name)
            elif action == 2:  # noqa: PLR2004
                self.handle_list_options(gc_manager, bucket_name)
            elif action == 3:  # noqa: PLR2004
                self.handle_creation_options(gc_manager, bucket_name)
            elif action == 4:  # noqa: PLR2004
                file_url = input("Enter the file URL: ")
                url = input("Enter the folder and file name in the bucket: ")
                gc_manager.upload_file(bucket_name, file_url, url)
            elif action == 9:  # noqa: PLR2004
                break
            else:
                print("Invalid action. Please choose a valid option.")  # noqa: T201

    def print_menu(self, bucket_name):
        """
        Displays the main menu for the user to choose actions such as changing the bucket,
        deleting files/folders, listing files/folders, creating resources, or uploading files.

        Args:
            bucket_name (str): The current bucket name.
        """  # noqa: E501
        print(  # noqa: T201
            f"""Input the number of the action you want to perform:
            -- Your bucket name is {bucket_name} --

            0. Change bucket
            1. Delete options
            2. List options
            3. Creation options
            4. Upload file
            9. Exit
            """,
        )

    def handle_delete_options(self, gc_manager, bucket_name):
        """
        Displays the delete options for the user to choose, such as deleting a file, folder,
        all files, or all folders in the bucket.

        Args:
            gc_manager (GCSManager): An instance of the GCSManager class to perform the delete operations.
            bucket_name (str): The current bucket name.
        """  # noqa: E501
        print(  # noqa: T201
            f"""Input the number of the action you want to perform:
            -- Your bucket name is {bucket_name} --

            1. Delete a file
            2. Delete a folder
            3. Delete all files
            4. Delete all folders
            5. Delete all
            8. Return
            9. Exit
            """,
        )

        try:
            action = int(input("Enter the number of the action: "))
        except ValueError:
            print("Invalid input. Please enter a number.")  # noqa: T201
            return

        if action == 1:
            file_name = input("Enter the URL of the file: ")
            gc_manager.delete_file(bucket_name, file_name)
        elif action == 2:  # noqa: PLR2004
            folder_name = input("Enter the URL of the folder: ")
            gc_manager.delete_folder(bucket_name, folder_name)
        elif action == 3:  # noqa: PLR2004
            gc_manager.delete_all_files(bucket_name)
        elif action == 4:  # noqa: PLR2004
            gc_manager.delete_all_folders(bucket_name)
        elif action == 5:  # noqa: PLR2004
            gc_manager.delete_all_files(bucket_name)
            gc_manager.delete_all_folders(bucket_name)
        elif action == 8:  # noqa: PLR2004
            return
        elif action == 9:  # noqa: PLR2004
            sys.exit()  # Terminates the script if exit is selected
        else:
            print("Invalid action. Please choose a valid option.")  # noqa: T201

    def handle_list_options(self, gc_manager, bucket_name):
        """
        Displays options for listing files and folders in the specified bucket.

        Args:
            gc_manager (GCSManager): An instance of the GCSManager class to perform listing operations.
            bucket_name (str): The current bucket name.
        """  # noqa: E501
        print(  # noqa: T201
            f"""Input the number of the action you want to perform:
            -- Your bucket name is {bucket_name} --

            1. List files in folder
            2. List folders
            8. Return
            9. Exit
            """,
        )

        try:
            action = int(input("Enter the number of the action: "))
        except ValueError:
            print("Invalid input. Please enter a number.")  # noqa: T201
            return

        if action == 1:
            gc_manager.list_files_in_folder(bucket_name)
        elif action == 2:  # noqa: PLR2004
            gc_manager.list_folders(bucket_name)
        elif action == 8:  # noqa: PLR2004
            return
        elif action == 9:  # noqa: PLR2004
            sys.exit()  # Terminates the script if exit is selected
        else:
            print("Invalid action. Please choose a valid option.")  # noqa: T201

    def handle_creation_options(self, gc_manager, bucket_name):
        """
        Displays options for creating resources such as a new bucket or folder.

        Args:
            gc_manager (GCSManager): An instance of the GCSManager class to perform creation operations.
            bucket_name (str): The current bucket name.
        """  # noqa: E501
        print(  # noqa: T201
            f"""Input the number of the action you want to perform:
            -- Your bucket name is {bucket_name} --

            1. Create bucket hierarchical namespace
            2. Create folder
            8. Return
            9. Exit
            """,
        )

        try:
            action = int(input("Enter the number of the action: "))
        except ValueError:
            print("Invalid input. Please enter a number.")  # noqa: T201
            return

        if action == 1:
            new_bucket_name = input("Enter the name of the new bucket: ")
            gc_manager.create_bucket_hierarchical_namespace(new_bucket_name)
        elif action == 2:  # noqa: PLR2004
            folder_name = input("Enter the name of the folder: ")
            gc_manager.create_folder(bucket_name, folder_name)
        elif action == 8:  # noqa: PLR2004
            return
        elif action == 9:  # noqa: PLR2004
            sys.exit()  # Terminates the script if exit is selected
        else:
            print("Invalid action. Please choose a valid option.")  # noqa: T201
