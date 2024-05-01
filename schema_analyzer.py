import mysql.connector
from mysql.connector import Error
from datetime import datetime, date


class SchemaAnalyzer:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def identify_primary_datetime_column(self, database_name, table_name):
        """
        Identifies the primary datetime or date column from the given table.
        If multiple datetime columns are found, determine the earliest as the primary.
        Exclude columns likely to be update timestamps.
        """
        datetime_columns = self.fetch_datetime_columns(database_name, table_name)

        # Filter out columns that contain 'update' in their names, focusing on creation date
        creation_like_columns = [col for col in datetime_columns if 'update' not in col.lower()]

        if len(creation_like_columns) == 1:
            return creation_like_columns[0]  # If only one suitable column, return it
        elif creation_like_columns:
            return self.determine_earliest_column(database_name, table_name, creation_like_columns)
        else:
            return None  # No suitable datetime column found

    def fetch_datetime_columns(self, database_name, table_name):
        """
        Fetches all datetime or date columns from a specified table.
        """
        query = f"""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = '{database_name}' 
          AND TABLE_NAME = '{table_name}' 
          AND DATA_TYPE IN ('datetime', 'date');
        """
        try:
            columns = []
            cursor = self.db_connector.cursor()
            cursor.execute(query)
            for (column_name,) in cursor:
                columns.append(column_name)
            return columns
        except Error as e:
            print(f"Error fetching datetime columns from {database_name}.{table_name}: {e}")
            return []

    def determine_earliest_column(self, database_name, table_name, columns):
        """
        Determines the column with the earliest datetime value, assuming these represent creation dates.
        Handles None values and ensures that all comparisons are between datetime objects.
        """
        earliest_column = None
        earliest_date = None

        for column in columns:
            query = f"""
            SELECT MIN({column}) FROM {database_name}.{table_name} WHERE {column} IS NOT NULL;
            """
            try:
                cursor = self.db_connector.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()

                # Check if result is not None and convert date to datetime if necessary
                if result[0] is not None:
                    current_date = result[0]
                    # Ensure we are comparing datetime objects
                    if isinstance(current_date, date) and not isinstance(current_date, datetime):
                        current_date = datetime.combine(current_date, datetime.min.time())  # Convert date to datetime

                    if earliest_date is None or current_date < earliest_date:
                        earliest_date = current_date
                        earliest_column = column

            except Error as e:
                print(f"Error determining earliest date in {column} of {table_name}: {e}")

        return earliest_column
