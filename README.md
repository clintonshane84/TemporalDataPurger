# TableCRUDOperator

The **TableCRUDOperator** is a Python-based utility for automating CRUD (Create, Read, Update, Delete) operations on database tables. It simplifies interactions with MySQL databases by leveraging metadata from table schemas. This tool dynamically generates fake data for testing purposes, accounts for columns with explicit and implicit defaults, and ensures seamless operations without manual intervention.

## Features
- **Dynamic CRUD Operations**: Perform Create, Read, Update, and Delete operations on specified tables.
- **Fake Data Generation**: Automatically generates fake data for required columns, considering explicit defaults (`NULL`, empty string) and implicit constraints.
- **Configurable**: Supports easy configuration of database credentials and tables to target.
- **Testing and Validation**: Great for stress testing and data validation during development.

## Benefits
- Reduces manual effort in creating test data.
- Ensures schema compliance by respecting explicit and implicit column defaults.
- Simplifies database testing and prototyping workflows.
- Facilitates quick debugging of table interactions.

## Requirements
To run the **TableCRUDOperator**, the following are required:
- Python 3.8+
- MySQL database server

### Python Dependencies
Install the required dependencies using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

# Configuration
### 1. Database Configuration (`db_config.json`)
Create a `db_config.json` file in the project root to define database connection details:

```json
{
    "host": "db_host",
    "user": "root",
    "password": "root"
}
```

## 2. Database and Table Selection (`load_db_tables.json`)
Prototype this file from `load_db_tables.json.sample` to specify the database and tables:

```json
{
    "database": "my_database",
    "tables": [
        "table_1",
        "table_2",
        "table_3"
    ]
}
```
Rename the `.sample` file to `load_db_tables.json` before use.

# Usage
## Activate the Virtual Environment
To run the TableCRUDOperator, activate the virtual environment:

```bash
source .venv/bin/activate   # On Linux/MacOS
.\.venv\Scripts\activate    # On Windows
```

# Run CRUD Operations
## Execute the script to perform CRUD operations on the tables listed in `load_db_tables.json`:

```bash
python main.py --crud
```
This command performs the following:

1. **Insert Operation**: Generates and inserts fake data for each table, respecting column constraints and defaults.
2. **Read Operation:** Reads the inserted data for verification.
3. **Update Operation:** Updates one or more rows with new fake data.
4. **Delete Operation:** Deletes rows based on predefined logic.

# Logging and Debugging
Logs for operations are output to the console and a log file in the project directory.

# Example Workflow
1. Clone the repository and navigate to the project directory.
2. Create a Python virtual environment:
```bash
python -m venv .venv
```
3. Activate the virtual environment:
```bash
source .venv/bin/activate
``
4. Install requirements:
```bash
pip install -r requirements.txt
```
5. Configure `db_config.json` and `load_db_tables.json` as per your database and table setup.
6. Run the CRUD operations:
```bash
python main.py --crud
```
# Project Structure
```bash
.
├── README.md
├── main.py                  # Entry point for running the tool
├── requirements.txt         # Python dependencies
├── db_config.json           # Database connection details
├── db_config.json.sample    # Sample database configuration
├── load_db_tables.json      # Database and table selection
├── load_db_tables.json.sample # Sample database and table selection
└── logs/                    # Directory for log files
```
# Notes
- Ensure the database is accessible with the provided credentials.
- The tool respects explicit and implicit defaults, generating data only for columns without explicit defaults (`NULL`, empty string).
- Customize `main.py` to add new functionality or refine logging as needed.
