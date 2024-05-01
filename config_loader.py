import json


class ConfigLoader:
    def __init__(self, config_file_path="db_config.json"):
        self.config_file_path = config_file_path

    def load_config(self):
        """
        Loads and returns the database configuration from a JSON file.
        """
        try:
            with open(self.config_file_path, 'r') as file:
                config = json.load(file)
                return config
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {self.config_file_path}")
            return None
        except json.JSONDecodeError:
            print("Error: Invalid JSON in configuration file.")
            return None
