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


def upload_parquet_to_s3(s3_path, dataframe, s3_access_key, s3_secret_key, mode="append"):
    return wr.s3.to_parquet(
        df=dataframe,
        path=s3_path,
        dataset=True,
        mode=mode,
        boto3_session=boto3.Session(
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        )
    )


def delete_object_from_s3(s3_paths, s3_access_key, s3_secret_key):
    return wr.s3.delete_objects(
        path=s3_paths,
        boto3_session=boto3.Session(
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        )
    )
