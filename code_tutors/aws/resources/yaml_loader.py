import yaml
from typing import Any

_yaml_file = None

def load_yaml(path: str) -> dict[str, Any]:
    global _yaml_file
    if _yaml_file is not None:
        return _yaml_file

    with open(path) as file:
        _yaml_file = yaml.safe_load(file)
        return _yaml_file

def get_bucket_name(service: str) -> str:
    yaml_file = load_yaml(path="code_tutors/aws/resources/config.yml")
    return yaml_file["bucket_names"][service]

def get_role_name(service: str) -> str:
    yaml_file = load_yaml(path="code_tutors/aws/resources/config.yml")
    return yaml_file["roles"][service]

def get_logo_name():
    yaml_file = load_yaml(path="code_tutors/aws/resources/config.yml")
    return yaml_file["logo_name"]