import boto3


class S3ConnectionChecker:
    @staticmethod
    def check_s3_conn(aws_access_key, aws_secret_key):
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key,
                          aws_secret_access_key=aws_secret_key)
        try:
            response = s3.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            return True
        except Exception as e:
            return False
