import awswrangler as wr
import boto3


def upload_csv_to_s3(s3_path, dataframe, s3_access_key, s3_secret_key, sep=",", mode="append"):
    return wr.s3.to_csv(
        dataframe,
        path=s3_path,
        sep=sep,
        index=False,
        mode=mode,
        dataset=True,
        boto3_session=boto3.Session(
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        )
    )


# def upload_parquet_to_s3(s3_path, dataframe, s3_access_key, s3_secret_key, mode="append"):
#     return wr.s3.to_parquet(
#         df=dataframe,
#         path=s3_path,
#         dataset=True,
#         mode=mode,
#         boto3_session=boto3.Session(
#             aws_access_key_id=s3_access_key,
#             aws_secret_access_key=s3_secret_key
#         )
#     )

import boto3
from io import BytesIO
import pandas as pd

def upload_parquet_to_s3(s3_path, dataframe, s3_access_key, s3_secret_key, mode="append"):
    # Extract the bucket name and object key from the S3 path
    s3_bucket, s3_key = s3_path.replace("s3://", "").split("/", 1)

    # Create an S3 client with the specified endpoint
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        endpoint_url='http://172.21.0.3:9001'  # MinIO API endpoint
    )

    # Convert the Pandas DataFrame to bytes
    dataframe_bytes = BytesIO()
    dataframe.to_parquet(dataframe_bytes, index=False)
    dataframe_bytes.seek(0)

    # Upload the DataFrame bytes to MinIO
    s3_client.upload_fileobj(
        dataframe_bytes,
        s3_bucket,
        f"{s3_key}/your_file_name.parquet",  # Specify a unique file name
        ExtraArgs={'ContentType': 'application/octet-stream'}
    )

    return f"Data has been uploaded to {s3_path}"

def delete_object_from_s3(s3_paths, s3_access_key, s3_secret_key):
    return wr.s3.delete_objects(
        path=s3_paths,
        boto3_session=boto3.Session(
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        )
    )
