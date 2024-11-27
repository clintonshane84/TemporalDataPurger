import json


class ConfigLoader:
    def __init__(self, config_file_path="db_config.json", tables_file_path="load_db_tables.json"):
        self.config_file_path = config_file_path
        self.tables_file_path = tables_file_path

    def load_config(self):
        """
        Loads and returns the database configuration from a JSON file.
        """
        try:
            with open(self.config_file_path, 'r') as file:
                config = json.load(file)
                return config
        except FileNotFoundError:
            print(
                f"Error: Configuration file not found at {self.config_file_path}")
            return None
        except json.JSONDecodeError:
            print("Error: Invalid JSON in configuration file.")
            return None

    def load_tables(self):
        """
        Loads and returns a list of tables for CRUD operations from a JSON file.
        """
        try:
            with open(self.tables_file_path, 'r') as file:
                tables_config = json.load(file)
                return tables_config
        except FileNotFoundError:
            print(f"Error: Tables file not found at {self.tables_file_path}")
            return None
        except json.JSONDecodeError:
            print("Error: Invalid JSON in tables file.")
            return None
