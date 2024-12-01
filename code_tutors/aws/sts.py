from code_tutors.aws import settings


def assume_role(role_arn: str, session: str) -> dict[str, str]:
    """Function to assume at role from AWS IAM.

    :param role_arn: the Amazon Resource Name (ARN) of the role
    :param session: a string representing the name of the session.
    :return: A dictionary of temporary credentials for the assumed role.
    """
    sts_client = settings.get_client('sts')
    response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=session, DurationSeconds=3600)
    return response['Credentials']
