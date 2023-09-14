from utils.Env import Env
import os
import json
from utils.DremioHelper import DremioHelper
from database import DataSourceConfiguration
from utils.s3Connection import S3ConnectionChecker
env = Env.instance()

DEFAULT_LIMITS = env.get_or_default("limiter.limits", "['1 per minute']")
X_CUSTOM_PASSCODE = env.get_or_default("limiter.passcode", "passcode")

S3_PATH = env.get_or_default("aws.s3.bucket.path", "s3://monocle/csv")
S3_ACCESS_KEY = env.get_or_default("aws.s3.access.key", "access-key")
S3_ACCESS_SECRET_KEY = env.get_or_default(
    "aws.s3.access.key.secret", "access-key-secret")

RAW_FILE_PATH = env.get_or_default("storage.path.raw", "raw")
TRANSFORM_FILE_PATH = env.get_or_default("storage.path.transform", "transform")
BASE_FOLDER_NAME = env.get_or_default("storage.name", "storage")
DREMIO_VDS_PATH = env.get_or_default("dremio.vds.path", "monocle")
DREMIO_S3_PATH = env.get_or_default("dremio.dataset.path", "dataset path")
DREMIO_CATALOG_PATH = env.get_or_default("dremio.catalog.path", "catalog path")

DREMIO_URL = env.get_or_default("dremio.url", "localhost:9047")
DREMIO_USERNAME = env.get_or_default("dremio.username", "dremio")
DREMIO_PASSWORD = env.get_or_default("dremio.password", "password")


def create_directories():
    dir_list = [RAW_FILE_PATH, TRANSFORM_FILE_PATH, BASE_FOLDER_NAME]
    for each_dir in dir_list:
        os.makedirs(each_dir, exist_ok=True)


def check_configuration():
    # directory check
    create_directories()
    data = {
        "database": DataSourceConfiguration.check_connection(),
        "dremio": DremioHelper(DREMIO_URL, DREMIO_USERNAME, DREMIO_PASSWORD).check_dremio_conn(),
        "s3": S3ConnectionChecker.check_s3_conn(S3_ACCESS_KEY, S3_ACCESS_SECRET_KEY)

    }
    return data
