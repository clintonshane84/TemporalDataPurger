import argparse
import mysql.connector
from db_connector import DatabaseConnector
from schema_analyzer import SchemaAnalyzer
from query_generator import QueryGenerator
from file_writer import FileWriter
from config_loader import ConfigLoader

def main():
    parser = argparse.ArgumentParser(description="Generate SQL deletion queries for specified databases up to a certain date.")
    parser.add_argument('--databases', nargs='+', required=True, help="List of databases to process")
    parser.add_argument('--date', required=True, help="The end date in 'YYYY-MM-DD' format for the DELETE operations.")
    parser.add_argument('--output_dir', default='./output', help="Directory where SQL files will be saved (default: ./output)")
    parser.add_argument('--config_file', default='./db_config.json', help="Path to the database configuration file (default: ./db_config.json)")

    args = parser.parse_args()

    # Load database configuration
    config_loader = ConfigLoader(args.config_file)
    db_config = config_loader.load_config()
    if not db_config:
        return

    db_connector = DatabaseConnector(db_config)
    db_connector.connect()

    # Initialize components
    schema_analyzer = SchemaAnalyzer(db_connector)
    query_generator = QueryGenerator()
    file_writer = FileWriter(args.output_dir)

    # Process each database
    for database_name in args.databases:
        # Use database connector to get a list of tables from the database
        tables_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{database_name}';"
        try:
            tables = db_connector.execute_query(tables_query)
        except Exception as e:
            print(f"Failed to fetch tables for database {database_name}: {e}")
            continue

        table_column_mapping = {}
        for (table_name,) in tables:
            primary_datetime_column = schema_analyzer.identify_primary_datetime_column(database_name, table_name)
            if primary_datetime_column:
                table_column_mapping[table_name] = primary_datetime_column

        queries = query_generator.generate_queries_for_database(table_column_mapping, args.date)
        file_writer.write_queries_to_file(database_name, queries)

    # Close the database connection
    db_connector.close()

if __name__ == "__main__":
    main()
