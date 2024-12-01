import typing

from django.conf import settings as django_settings

from .resources import yaml_loader as yaml
from .settings import get_client
from .sts import assume_role

ROLE_NAME = yaml.get_role_name('invoicer-s3')
BUCKET = yaml.get_bucket_name('invoicer')
__session_counter = -1


def upload(key: str, obj: typing.IO, bucket: str = BUCKET, extra_args: typing.Optional[dict] = None,
           credentials: dict[str, str] = None) -> None:
    """
    Function to upload an object to an S3 bucket
    :param key: The key of the object to upload, i.e. the "path" in the bucket where the file will be located.
    :param obj: The object to upload.
    :param bucket: The bucket to upload to. If not passed, the default bucket name will be used.
    :param extra_args: A dictionary of extra arguments to pass to the S3 upload function. Not normally needed.
    :param: credentials: A dictionary of temporary credentials to pass to the S3 upload function. Usually related to an assumed role.
    """
    credentials = __get_credentials() if not credentials else credentials
    s3_client = get_client('s3', credentials=credentials) if credentials else None
    s3_client.upload_fileobj(obj, Bucket=bucket, Key=key, ExtraArgs=extra_args)


def __delete(key: str, bucket: str = BUCKET, credentials: dict[str, str] = None) -> None:
    """Function to delete an object from an S3 bucket.

    :param key: The key of the object to delete, i.e. the "path" in the bucket where the file is.
    :param bucket: The bucket from which to delete. If not passed, the default bucket name will be used.
    :param credentials: A dictionary of temporary credentials to pass to the S3 delete function. Usually related to an assumed role.
    """
    credentials = __get_credentials() if not credentials else credentials
    s3_client = get_client('s3', credentials=credentials) if credentials else None
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
    except Exception as e:
        print(f'Error deleting file: {e}')


def generate_access_url(key: str, bucket: str = BUCKET, expiration: int = 3600,
                        credentials: dict[str, str] = None) -> str:
    """Function to generate a pre-signed URL to access a file in S3

    :param key: The key of the object for which to generate the pre-signed URL.
    :param bucket: The bucket to which the object belongs.
    :param expiration: The number of seconds that the pre-signed URL will be valid for.
    :param credentials: A dictionary of temporary credentials to pass to the S3 delete function. Usually related to an assumed role.
    """
    credentials = __get_credentials() if not credentials else credentials
    s3_client = get_client('s3', credentials=credentials) if credentials else None
    try:
        return s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key},
                                                ExpiresIn=expiration)
    except Exception as e:
        print(f'Error generating pre-signed URL: {e}')


def __get_credentials() -> dict[str, str]:
    """Function to retrieve the temporary credentials associated with an assumed role

    :return: a dictionary of temporary credentials.
    """
    global __session_counter
    __session_counter += 1
    return assume_role(f'arn:aws:iam::{django_settings.AWS_ACCOUNT_ID}:role/{ROLE_NAME}', f'badger-{__session_counter}')
