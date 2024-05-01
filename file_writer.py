import os
from datetime import datetime

class FileWriter:
    def __init__(self, output_directory):
        """
        Initializes the FileWriter with the directory where SQL files will be saved.

        Args:
        - output_directory (str): The path to the directory where output files will be stored.
        """
        self.output_directory = output_directory
        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

    def write_queries_to_file(self, database_name, queries):
        """
        Writes a set of SQL queries to a file named with today's date and the database name.

        Args:
        - database_name (str): The name of the database for which the SQL file is generated.
        - queries (dict): A dictionary of table names to their respective SQL delete queries.
        """
        if not queries:
            print(f"No queries to write for database {database_name}.")
            return

        # Format the filename with today's date and the database name
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{database_name}_{date_str}.sql"
        file_path = os.path.join(self.output_directory, filename)

        try:
            with open(file_path, 'w') as file:
                for table, query in queries.items():
                    file.write(f"-- Queries for table: {table}\n")
                    file.write(query + "\n\n")
            print(f"Queries successfully written to {file_path}")
        except IOError as e:
            print(f"Failed to write file {file_path}: {e}")

