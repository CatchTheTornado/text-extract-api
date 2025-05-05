import os
from enum import Enum

import yaml

from text_extract_api.files.storage_strategies.aws_s3 import AWSS3StorageStrategy
from text_extract_api.files.storage_strategies.google_drive import (
    GoogleDriveStorageStrategy,
)
from text_extract_api.files.storage_strategies.local_filesystem import (
    LocalFilesystemStorageStrategy,
)


class StorageStrategy(Enum):
    LOCAL_FILESYSTEM = "local_filesystem"
    GOOGLE_DRIVE = "google_drive"
    AWS_S3 = "aws_s3"


class StorageManager:
    def __init__(self, profile_name):
        profile_path = os.path.join(
            os.getenv("STORAGE_PROFILE_PATH", "/storage_profiles"),
            f"{profile_name}.yaml",
        )
        with open(profile_path, "r") as file:
            self.profile = yaml.safe_load(file)

        strategy = StorageStrategy(self.profile["strategy"])
        if strategy == StorageStrategy.LOCAL_FILESYSTEM:
            self.strategy = LocalFilesystemStorageStrategy(self.profile)
        elif strategy == StorageStrategy.GOOGLE_DRIVE:
            self.strategy = GoogleDriveStorageStrategy(self.profile)
        elif strategy == StorageStrategy.AWS_S3:
            self.strategy = AWSS3StorageStrategy(self.profile)
        else:
            raise ValueError(f"Unknown storage strategy '{strategy}'")

    def save(self, file_name, dest_file_name, content):
        self.strategy.save(file_name, dest_file_name, content)

    def load(self, file_name):
        return self.strategy.load(file_name)

    def list(self):
        return self.strategy.list()

    def delete(self, file_name):
        self.strategy.delete(file_name)
