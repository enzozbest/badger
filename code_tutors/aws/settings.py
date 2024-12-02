import os

import boto3

__AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
__AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
__AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')


def get_client(service: str, credentials: dict[str, str] = None):
    """Function to get a boto3 client for a given AWS service.

    :param service: the name of the AWS service for which a boto3 client is requested.
    :param credentials: the credentials to use when making the request.
    :return: a boto3 client object for the requested service.
    """
    if not service:
        return None
    if credentials:
        return boto3.client(service, aws_access_key_id=credentials['AccessKeyId'],
                            aws_secret_access_key=credentials['SecretAccessKey'],
                            aws_session_token=credentials['SessionToken'],
                            region_name=__AWS_REGION_NAME
                            )

    return boto3.client(service, aws_access_key_id=__AWS_ACCESS_KEY_ID, aws_secret_access_key=__AWS_SECRET_ACCESS_KEY,
                        region_name=__AWS_REGION_NAME
                        )
