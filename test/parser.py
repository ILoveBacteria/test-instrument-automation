import os
import json
import yaml
import jsonschema


def read_test_file(file_path: str) -> dict:
    """
    Read and parse a YAML test file.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        dict: The parsed test data.

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If the YAML content is invalid.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'test file not found: {file_path}')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data


def _read_schema_file(schema_path: str) -> dict:
    """
    Read and parse a JSON schema file.

    Args:
        schema_path (str): Path to the JSON schema file.

    Returns:
        dict: The loaded schema definition.

    Raises:
        FileNotFoundError: If the schema file does not exist.
        json.JSONDecodeError: If the JSON content is invalid.
    """
    if not os.path.isfile(schema_path):
        raise FileNotFoundError(f'Schema file not found: {schema_path}')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    return schema


def parse_test_file(file_path, schema_path) -> dict:
    """
    Load a test file and validate it against a JSON schema.

    Args:
        file_path (str): Path to the YAML test file.
        schema_path (str): Path to the JSON schema file.

    Returns:
        dict: The validated test data.

    Raises:
        FileNotFoundError: If either file does not exist.
        yaml.YAMLError: If the YAML content is invalid.
        json.JSONDecodeError: If the JSON schema is invalid.
        jsonschema.ValidationError: If the test does not match the schema.
    """
    data = read_test_file(file_path)
    schema = _read_schema_file(schema_path)
    jsonschema.validate(data, schema)
    return data