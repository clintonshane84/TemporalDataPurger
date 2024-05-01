class QueryGenerator:
    def __init__(self):
        pass

    def generate_delete_query(self, table_name, datetime_column, end_date):
        """
        Generates an SQL DELETE query for the specified table using the datetime column
        to delete records older than the specified end date.

        Args:
        - table_name (str): The name of the table.
        - datetime_column (str): The datetime or date column to filter on.
        - end_date (str): The end date in 'YYYY-MM-DD' format, up to which records will be deleted.

        Returns:
        - str: The SQL DELETE query string.
        """
        if datetime_column is None:
            return None

        query = f"DELETE FROM `{table_name}` WHERE `{datetime_column}` <= '{end_date}';"
        return query

    def generate_queries_for_database(self, table_column_mapping, end_date):
        """
        Generates DELETE queries for all tables in a database based on the mappings of
        tables to their primary datetime/date columns.

        Args:
        - table_column_mapping (dict): A dictionary mapping table names to their primary datetime/date columns.
        - end_date (str): The end date in 'YYYY-MM-DD' format for the DELETE operations.

        Returns:
        - dict: A dictionary of table names to their respective DELETE query strings.
        """
        queries = {}
        for table_name, datetime_column in table_column_mapping.items():
            delete_query = self.generate_delete_query(table_name, datetime_column, end_date)
            if delete_query:
                queries[table_name] = delete_query
        return queries
