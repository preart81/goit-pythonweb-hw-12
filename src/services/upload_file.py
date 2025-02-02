""" 
This module provides a service for uploading files to Cloudinary.
"""

import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    UploadFileService is a service class for uploading files to Cloudinary.
    Attributes:
    Methods:
        __init__(cloud_name, api_key, api_secret):
            Initializes the UploadFileService with the provided Cloudinary configuration.
        upload_file(file, username) -> str:
            Uploads the given file to Cloudinary and returns the URL of the uploaded file.
    """

    def __init__(self, cloud_name, api_key, api_secret):
        """
        Initializes the UploadFileService with the provided cloudinary configuration.

        Args:
            cloud_name (str): Cloudinary cloud name.
            api_key (str): Cloudinary API key.
            api_secret (str): Cloudinary API secret.
        """

        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Uploads the given file to Cloudinary.

        Args:
            file (UploadFile): The file to upload.
            username (str): The username to associate with the uploaded file.

        Returns:
            str: The URL of the uploaded file.
        """

        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
