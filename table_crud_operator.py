from mysql.connector import Error
from faker import Faker
import logging


class TableCRUDOperator:
    def __init__(self, connection, database, tables):
        self.connection = connection
        self.database = database
        self.tables = tables
        self.fake = Faker()
        self.primary_keys = {}
        self.last_inserted_ids = {}
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler("crud_operations.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def switch_database(self):
        """
        Switch to the specified database.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"USE `{self.database}`;")
            self.logger.info(f"Switched to database: {self.database}")
        except Error as e:
            self.logger.error(
                f"Failed to switch to database {self.database}: {e}")
            raise

    def fetch_table_columns(self, table):
        """
        Fetch column metadata for a table.
        """
        query = f"""
        SELECT COLUMN_NAME, COLUMN_KEY, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table}';
        """
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query)
            columns = cursor.fetchall()
            self.logger.info(f"Fetched columns for table {table}: {columns}")

            # Detect the primary key
            primary_key = next(
                (col['COLUMN_NAME'] for col in columns if col['COLUMN_KEY'] == 'PRI'), None)
            if not primary_key:
                self.logger.warning(
                    f"Table `{table}` does not have a primary key.")
            self.primary_keys[table] = primary_key

            return columns
        except Error as e:
            self.logger.error(
                f"Failed to fetch columns for table {table}: {e}")
            return []

    def generate_fake_data(self, columns):
        """
        Generate fake data based on column metadata.
        """
        fake_data = {}
        for column in columns:
            col_name = column["COLUMN_NAME"]
            data_type = column["DATA_TYPE"]
            is_nullable = column["IS_NULLABLE"]
            column_default = column["COLUMN_DEFAULT"]

            # Skip columns with explicit default values
            if column_default not in [None, '']:
                continue

            # Generate data based on type
            if data_type in ["varchar", "text", "char"]:
                fake_data[col_name] = self.fake.text(max_nb_chars=20)
            elif data_type in ["int", "bigint", "smallint", "mediumint", "tinyint"]:
                fake_data[col_name] = self.fake.random_int(min=1, max=100)
            elif data_type in ["decimal", "float", "double"]:
                fake_data[col_name] = self.fake.pyfloat(
                    left_digits=5, right_digits=2)
            elif data_type in ["date"]:
                fake_data[col_name] = self.fake.date()
            elif data_type in ["datetime", "timestamp"]:
                fake_data[col_name] = self.fake.date_time().strftime(
                    "%Y-%m-%d %H:%M:%S")
            elif data_type in ["boolean", "bit"]:
                fake_data[col_name] = self.fake.boolean()
            elif is_nullable == "YES":
                fake_data[col_name] = None
            else:
                fake_data[col_name] = "UNKNOWN"

        return fake_data

    def perform_crud_operations(self):
        """
        Perform CRUD operations for each table.
        """
        self.switch_database()
        for table in self.tables:
            self.logger.info(f"Processing table: {table}")
            try:
                columns = self.fetch_table_columns(table)
                if not columns:
                    self.logger.warning(
                        f"Skipping table {table}: No column metadata found.")
                    continue

                # Test SELECT
                self.select_table_data(table)

                # Test INSERT
                self.insert_fake_data(table, columns)

                # Test UPDATE
                self.update_table_data(table, columns)

                # Test DELETE
                self.delete_table_data(table)

            except Error as e:
                self.logger.error(
                    f"Error performing CRUD operations on table {table}: {e}")

    def select_table_data(self, table):
        """
        Test SELECT operation on the table.
        """
        query = f"SELECT * FROM `{table}` LIMIT 1;"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            self.logger.info(
                f"SELECT operation succeeded on table {table}. Rows: {rows}")
        except Error as e:
            self.logger.error(f"SELECT operation failed on table {table}: {e}")

    def insert_fake_data(self, table, columns):
        """
        Insert fake data into the table using column metadata.
        """
        try:
            primary_key = self.primary_keys.get(table)
            column_names = [col["COLUMN_NAME"]
                            for col in columns if col["COLUMN_NAME"] != primary_key and (col["COLUMN_DEFAULT"] in [None, ''])]
            data = self.generate_fake_data(columns)

            # Filter out primary key and default columns
            filtered_data = {key: data[key]
                             for key in column_names if key in data}
            placeholders = ", ".join(["%s"] * len(filtered_data))
            values = tuple(filtered_data.values())

            insert_query = f"INSERT INTO `{table}` ({', '.join(filtered_data.keys())}) VALUES ({placeholders})"

            cursor = self.connection.cursor()
            cursor.execute(insert_query, values)
            self.connection.commit()

            self.last_inserted_ids[table] = cursor.lastrowid

            self.logger.info(f"Inserted data into `{table}`: {filtered_data}")
        except Error as e:
            self.logger.error(f"INSERT operation failed on table {table}: {e}")

    def update_table_data(self, table, columns):
        """
        Test UPDATE operation using fake data.
        """
        try:
            primary_key = self.primary_keys.get(table)
            if not primary_key:
                raise ValueError(f"Primary key not found for table {table}.")

            # Generate data and pick a column to update
            data = self.generate_fake_data(columns)
            update_column = next(
                (col["COLUMN_NAME"] for col in columns if col["COLUMN_NAME"] != primary_key and (col["COLUMN_DEFAULT"] in [None, ''])), None)
            if not update_column:
                raise ValueError("No column available for update.")

            update_value = data[update_column]
            update_query = f"""
            UPDATE `{table}`
            SET {update_column} = %s
            WHERE {primary_key} = %s;
            """

            print(self.last_inserted_ids)

            cursor = self.connection.cursor()
            cursor.execute(update_query, (update_value,
                           self.last_inserted_ids[table]))
            self.connection.commit()

            self.logger.info(
                f"Updated last inserted row in `{table}`: {update_column} set to {update_value}")
        except Error as e:
            self.logger.error(f"UPDATE operation failed on table {table}: {e}")

    def delete_table_data(self, table):
        """
        Test DELETE operation.
        """
        try:
            primary_key = self.primary_keys.get(table)
            if not primary_key:
                raise ValueError(f"Primary key not found for table {table}.")

            delete_query = f"""
            DELETE FROM `{table}`
            WHERE {primary_key} = %s;
            """
            cursor = self.connection.cursor()
            cursor.execute(delete_query, (self.last_inserted_ids[table],))
            self.connection.commit()

            self.logger.info(f"Deleted last inserted row in `{table}`.")
        except Error as e:
            self.logger.error(f"DELETE operation failed on table {table}: {e}")
