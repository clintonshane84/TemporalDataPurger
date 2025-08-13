# TemporalDataPurger

Generate **reviewable** MySQL `DELETE` statements to safely purge historical/temporal data across one or more databases—without executing any destructive SQL automatically.

> **Version:** v1.0.0
> **Status:** Tested (query generation only)

---

## Why this exists

Large MySQL databases often accumulate old rows that are no longer needed. Purging them can be risky if you pick the wrong timestamp column or touch audit/update fields. **TemporalDataPurger** analyzes table schemas to identify the **most likely creation timestamp** per table, then generates targeted `DELETE` statements up to a cut-off date for you to review and run yourself.

**This tool does *not* execute any DELETEs.** It only writes `.sql` files you can review, test, and apply using your own process.

---

## Features

* 🔎 **Column discovery:** finds `datetime`/`date` columns per table, ignoring fields that look like update timestamps (column name contains “update”).
* 🧠 **Preference for creation time:** when multiple candidates exist, chooses the column with the **earliest recorded value** (`MIN(column)`), assuming it tracks creation.
* 🧾 **Per-DB output files:** writes one SQL file per database into an output folder (default `./output`), named like `my_database_YYYY-MM-DD.sql`.
* 🧰 **Simple CLI:** specify databases, cut-off date, output directory, and config path.

---

## How it works (high level)

1. Connects to MySQL using your config file.
2. Lists tables for each database via `information_schema.tables`.
3. For each table:

   * Collects all `date`/`datetime` columns from `information_schema.columns`.
   * Excludes columns whose names contain `update`.
   * If multiple candidates remain, picks the one with the earliest `MIN(column)` value.
4. Builds `DELETE FROM \`table\` WHERE \`chosen\_column\` <= 'YYYY-MM-DD';\`.
5. Writes all table queries for the database to a dated `.sql` file.

---

## Repository layout

```
TemporalDataPurger/
├─ main.py                 # CLI entrypoint
├─ schema_analyzer.py      # Finds the most appropriate date/datetime column per table
├─ query_generator.py      # Builds DELETE statements
├─ file_writer.py          # Writes per-database SQL files
├─ db_config.json          # (example; you will create/maintain)
├─ db_connector.py         # (expected) wrapper around mysql-connector (see below)
├─ config_loader.py        # (expected) loads the JSON config (see below)
└─ output/                 # Generated .sql files (created at runtime)
```

> **Note:** The project expects `db_connector.py` and `config_loader.py` modules. They should provide:
>
> * `DatabaseConnector(config)` with `.connect()`, `.cursor()`, `.execute_query(sql)`, and `.close()`.
> * `ConfigLoader(path)` with `.load_config()` returning a dict of MySQL connection settings.

---

## Requirements

* Python 3.9+
* `mysql-connector-python` (for MySQL connectivity)

Install dependencies:

```bash
pip install mysql-connector-python
```

---

## Configuration

Create a `db_config.json` file (or use any path via `--config_file`). Example:

```json
{
  "host": "127.0.0.1",
  "port": 3306,
  "user": "readonly_user",
  "password": "******",
  "ssl_disabled": true
}
```

**Minimum MySQL privileges** (for the user in your config):

* `SELECT` on:

  * `information_schema.columns`
  * `information_schema.tables`
  * All target databases/tables you want analyzed (to compute `MIN(column)`)

> The tool never executes `DELETE` statements; it only needs `SELECT`.
> You will execute the generated SQL separately with an appropriately privileged account.

---

## Usage

Basic:

```bash
python main.py \
  --databases my_db_a my_db_b \
  --date 2024-12-31 \
  --output_dir ./output \
  --config_file ./db_config.json
```

Arguments:

| Flag            | Required | Description                                                                     |
| --------------- | :------: | ------------------------------------------------------------------------------- |
| `--databases`   |     ✅    | One or more database names to process.                                          |
| `--date`        |     ✅    | Cut-off date `YYYY-MM-DD`. Rows with timestamp `<=` this date will be targeted. |
| `--output_dir`  |     ❌    | Where to write `.sql` files (default: `./output`).                              |
| `--config_file` |     ❌    | Path to DB config JSON (default: `./db_config.json`).                           |

Example output file path:

```
./output/my_db_a_2025-08-13.sql
```

Example file contents:

```sql
-- Queries for table: orders
DELETE FROM `orders` WHERE `created_at` <= '2024-12-31';

-- Queries for table: audit_log
DELETE FROM `audit_log` WHERE `inserted_on` <= '2024-12-31';
```

> If no suitable datetime/date columns are found for a table, it will be skipped.

---

## Important safety notes

* 🧯 **Review before running.** Generated SQL uses `<= 'YYYY-MM-DD'`. Confirm timezone assumptions and whether you want `<` vs `<=`.
* 🗃️ **Backups first.** Always snapshot/backup before deleting data.
* 🏷️ **Schema qualification.** The generated queries reference only the **table name**, not the database. When executing, ensure your session’s `USE database;` is correct or prepend the schema yourself (e.g., ``DELETE FROM `my_db`.`orders` ...``).
* 🧱 **Indexes matter.** Deleting large volumes by a non-indexed timestamp can be slow/lock heavy. Consider adding appropriate indexes or deleting in batches.
* 🧪 **Stage it.** Test on a staging clone to validate row counts affected per table.

---

## Troubleshooting

* **No output file created for a DB**

  * Likely no eligible tables/columns were found, or all were excluded as “update” timestamps.
* **Performance is slow during analysis**

  * The tool runs `MIN(column)` on candidate columns. Very large tables can make this slow without supporting indexes.
* **Wrong column chosen**

  * The heuristic prefers columns *not* containing “update”, then chooses the earliest `MIN()`. If your schema uses a different naming convention (e.g., `created_on`, `insert_ts`), this usually works; otherwise, adjust the code or add a table allow/deny list (see Enhancements).

---

## Enhancements you may want

* Table include/exclude lists (`--include tables...`, `--exclude tables...`)
* Per-table overrides for the timestamp column
* Batch deletion generation (`DELETE ... LIMIT N` loops) for safer runtime execution
* Qualification with database name in generated SQL
* Dry-run counting (`SELECT COUNT(*) ...`) alongside each `DELETE`
* Parallel schema analysis for large environments
* Optional output as `.sql.gz`

---

## Development notes (modules)

* **`schema_analyzer.py`**

  * Gathers `date`/`datetime` columns from `information_schema`.
  * Excludes names containing “update”.
  * If multiple candidates, selects the column with the smallest `MIN(column)` value (after normalizing `date` to `datetime`).
* **`query_generator.py`**

  * Builds `DELETE FROM \`{table}\` WHERE \`{column}\` <= '{end\_date}';\`.
* **`file_writer.py`**

  * Ensures output directory exists.
  * Writes one file per database with per-table queries, dated by current system date.

---

## Example: running the generated SQL

```sql
-- In MySQL (ensure you’re on the correct database)
USE my_db_a;

-- Review row counts before:
SELECT COUNT(*) FROM orders WHERE created_at <= '2024-12-31';

-- Execute:
DELETE FROM `orders` WHERE `created_at` <= '2024-12-31';
```

Consider executing large purges in controlled batches and off-peak hours.

---

## Contributing

Issues and PRs are welcome—especially for:

* Column selection overrides
* Batch deletion helpers
* Better multi-schema qualification

---

## License

MIT (see `LICENSE` if included).
