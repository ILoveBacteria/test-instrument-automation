import os
import yaml
import json
from jsonschema import validate


class ScenarioValidationError(Exception):
    """Custom exception for scenario validation errors."""
    pass


class ScenarioParser:
    """
    Parses and validates YAML scenario files using a JSON schema.
    """

    def __init__(self, filepath: str, schema_path: str):
        """
        Initialize the parser with the scenario file and schema path.

        Args:
            filepath (str): Path to the YAML scenario file.
            schema_path (str): Path to the JSON schema file.
        """
        self.filepath = filepath
        self.schema_path = schema_path
        self.data = None
        self.schema = None

    def load(self) -> dict:
        """
        Loads the YAML scenario file into a Python dictionary.

        Returns:
            dict: Parsed scenario data.

        Raises:
            FileNotFoundError: If the file is not found.
            yaml.YAMLError: If YAML is invalid.
        """
        if not os.path.isfile(self.filepath):
            raise FileNotFoundError(f'Scenario file not found: {self.filepath}')
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
        return self.data

    def load_schema(self) -> dict:
        """
        Loads the JSON schema file.

        Returns:
            dict: Loaded schema definition.

        Raises:
            FileNotFoundError: If the schema file is not found.
            json.JSONDecodeError: If the JSON is invalid.
        """
        if not os.path.isfile(self.schema_path):
            raise FileNotFoundError(f'Schema file not found: {self.schema_path}')
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        return self.schema

    def validate(self) -> None:
        """
        Validates the loaded scenario against the loaded schema.

        Raises:
            ScenarioValidationError: If validation fails.
        """
        if self.data is None:
            raise ScenarioValidationError('Scenario not loaded. Call load() first.')
        if self.schema is None:
            raise ScenarioValidationError('Schema not loaded. Call load_schema() first.')
        validate(instance=self.data, schema=self.schema)        

    def parse(self) -> dict:
        """
        Loads and validates the scenario file using the schema.

        Returns:
            dict: Validated scenario data.
        """
        self.load()
        self.load_schema()
        self.validate()
        return self.data
