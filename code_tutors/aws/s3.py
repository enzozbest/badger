import typing
from .sts import assume_role
from .settings import get_client
from django.conf import settings as django_settings
from .resources import yaml_loader as yaml

ROLE_NAME = yaml.get_role_name('invoicer-s3')
BUCKET = yaml.get_bucket_name('invoicer')
_session_counter = -1

def upload(key: str, obj: typing.IO, bucket: str=BUCKET, extra_args: typing.Optional[dict]=None, credentials: dict[str, str]=None) -> None:
    """
    Function to upload an object to S3 """
    credentials =  _get_credentials() if not credentials else credentials
    s3_client = get_client('s3', credentials=credentials) if credentials else None
    s3_client.upload_fileobj(obj, Bucket=bucket, Key=key, ExtraArgs=extra_args)


def _delete(key: str, bucket: str=BUCKET, credentials: dict[str, str]=None) -> None:
    credentials =  _get_credentials() if not credentials else credentials
    s3_client = get_client('s3', credentials=credentials) if credentials else None
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
    except Exception as e:
        print(f'Error deleting file: {e}')


def generate_access_url(key: str, bucket: str=BUCKET,expiration: int=3600, credentials: dict[str, str]=None) -> str:
    """Function to generate a pre-signed URL to access a file in S3"""
    credentials =  _get_credentials() if not credentials else credentials
    s3_client = get_client('s3', credentials=credentials) if credentials else None
    try:
        return s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=expiration)
    except Exception as e:
        print(f'Error generating pre-signed URL: {e}')

def list_objects(bucket: str=BUCKET, prefix: typing.Optional[str] = None, credentials:dict[str, str]=None) -> list[dict]:
    """Function to list objects in an S3 bucket"""
    credentials = _get_credentials() if not credentials else credentials
    s3_client = get_client('s3', credentials=credentials) if credentials else None
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return response.get('Contents', [])
    except Exception as e:
        print(f'Error listing objects in bucket: {e}')

def _get_credentials() -> dict[str, str]:
    global _session_counter
    _session_counter += 1
    return assume_role(f'arn:aws:iam::{django_settings.AWS_ACCOUNT_ID}:role/{ROLE_NAME}', f'badger-{_session_counter}')