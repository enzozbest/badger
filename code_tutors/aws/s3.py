import typing
from .sts import assume_role
from .settings import get_client
from django.conf import settings as django_settings

ROLE_NAME = 's3-badger-access-role'
BUCKET = 'seg-sgp-badger-2024'
SESSION_COUNTER = 0
def upload(bucket: str, obj: typing.IO, key: str, extra_args: typing.Optional[dict]=None) -> None:
    """
    Function to upload an object to S3 """
    credentials = _get_credentials()
    s3_client = get_client('s3', credentials=credentials) if credentials else None
    try:
        s3_client.upload_fileobj(obj, Bucket=bucket, Key=key, ExtraArgs=extra_args)
    except Exception as e:
        print(f'Error uploading file: {e}')

def generate_access_url(bucket: str, key: str, expiration: int=3600) -> str:
    """Function to generate a pre-signed URL to access a file in S3"""
    credentials = _get_credentials()
    s3_client = get_client('s3', credentials=credentials) if credentials else None
    try:
        return s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=expiration)
    except Exception as e:
        print(f'Error generating pre-signed URL: {e}')

def list_objects(bucket: str, prefix: typing.Optional[str] = None, credentials:dict[str]=None) -> list[dict]:
    """Function to list objects in an S3 bucket"""
    s3_client = get_client('s3', credentials=credentials) if credentials else None
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return response.get('Contents', [])
    except Exception as e:
        print(f'Error listing objects in bucket: {e}')

def _get_credentials() -> dict[str, str]:
    return assume_role(f'arn:aws:iam::{django_settings.AWS_ACCOUNT_ID}:role/{ROLE_NAME}', 'badger')