from code_tutors.aws import settings

def assume_role(role_arn: str, session: str) -> dict[str, str]:
    sts_client = settings.get_client('sts')
    response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=session, DurationSeconds=3600)
    return response['Credentials']