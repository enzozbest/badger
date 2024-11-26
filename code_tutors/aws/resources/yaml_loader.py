import yaml
from typing import Any
from django.conf import settings


_yaml_file = None
_yaml_path = None
_default_path = settings.AWS_YAML_CONFIG_PATH

def load_yaml(path: str = None) -> dict[str, Any]:
    """
    Loads a YAML file. If a path is provided and differs from the current cached path,
    the YAML file is reloaded.
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
    yaml_file = load_yaml(path=_yaml_path)
    return yaml_file["bucket_names"][service]

def get_role_name(service: str) -> str:
    yaml_file = load_yaml(path=_yaml_path)
    return yaml_file["roles"][service]

def get_logo_name():
    yaml_file = load_yaml(path=_yaml_path)
    return yaml_file["logo_name"]