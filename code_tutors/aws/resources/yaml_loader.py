from typing import Any

import yaml
from django.conf import settings

_yaml_file = None
_yaml_path = None
_default_path = settings.AWS_YAML_CONFIG_PATH


def load_yaml(path: str = None) -> dict[str, Any]:
    """ Loads a YAML file.

    Load a YAML file from a given path.
    If no path is provided, it is assumed to be the default path.
    If a path is provided, but it differs from the current cached path,the YAML file is reloaded.

    :param path: Path to the YAML file.
    :return: a dictionary representation of the YAML file.
    """
    global _yaml_file, _yaml_path

    if path is None:
        path = _default_path

    if _yaml_file is not None and _yaml_path == path:
        return _yaml_file

    with open(path, 'r') as file:
        _yaml_file = yaml.safe_load(file)
        _yaml_path = path
        return _yaml_file


def get_bucket_name(service: str) -> str:
    """
    Retrieves the name of the S3 bucket set in the config.yml file
    :param service:
    :return: the name of the bucket set in the config.yml file
    """
    yaml_file = load_yaml(path=_yaml_path)
    return yaml_file["bucket_names"][service]


def get_role_name(service: str) -> str:
    """
    Retrieves the name of the role associated with the given service, set in the config.yml file
    :param service: The AWS Service for which an access role will be retrieved
    :return: the name of the role associated with the given service
    """
    yaml_file = load_yaml(path=_yaml_path)
    return yaml_file["roles"][service]


def get_logo_name():
    """
    Retrieves the name of the logo set in the config.yml file
    :return: the name of the logo set in the config.yml file
    """
    yaml_file = load_yaml(path=_yaml_path)
    return yaml_file["logo_name"]
