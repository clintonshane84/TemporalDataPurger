import mysql.connector
from mysql.connector import Error

class DatabaseConnector:
    def __init__(self, config):
        """
        Initialize the DatabaseConnector with database configuration.

        Args:
        - config (dict): Database configuration parameters (host, user, password, etc.).
        """
        self.config = config
        self.connection = None

    def connect(self):
        """
        Establishes a database connection using the provided configuration.

        Returns:
        - connection: a MySQL connection object if successful, None otherwise.
        """
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print(f"Database connection established successfully.")
                return self.connection
        except Error as e:
            print(f"Failed to connect to database: {e}")
            return None

    def cursor(self):
        """
        Returns a cursor object using the current database connection, handling cases where the connection is not available.

        Returns:
        - cursor: a cursor object if connection is active, None otherwise.
        """
        if self.connection and self.connection.is_connected():
            return self.connection.cursor()
        else:
            print("No active database connection. Please connect to the database first.")
            return None

    def execute_query(self, query, params=None):
        """
        Executes a SQL query and returns the results.

        Args:
        - query (str): The SQL query to execute.
        - params (tuple, optional): Parameters for parameterized queries.

        Returns:
        - list: A list of tuples containing the query results.
        """
        cursor = self.cursor()
        if cursor is None:
            return []

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Error executing query '{query}': {e}")
            return []

    def close(self):
        """
        Closes the database connection.
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")
