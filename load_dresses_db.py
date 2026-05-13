import argparse
import csv
import sqlite3
from pathlib import Path
from typing import Dict, List


def normalize_column_name(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
    )


def create_designers_table(conn: sqlite3.Connection, table_name: str = "designers") -> None:
    conn.execute(
        f"""
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY,
            brand TEXT UNIQUE NOT NULL,
            founded_year TEXT,
            creative_director TEXT,
            ceo TEXT,
            city TEXT,
            country TEXT,
            headquarters TEXT,
            website TEXT,
            notes TEXT
        )
        """
    )


def load_designers_csv_to_sqlite(csv_path: Path, conn: sqlite3.Connection, table_name: str = "designers") -> int:
    if not csv_path.exists():
        raise FileNotFoundError(f"Designer CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_fieldnames = reader.fieldnames or []
        if not raw_fieldnames:
            raise ValueError("Designer CSV contains no columns")

        normalized_names = [normalize_column_name(name) for name in raw_fieldnames]
        headers_map: Dict[str, str] = {
            normalize_column_name(name): name for name in raw_fieldnames
        }
        if "brand" not in normalized_names:
            raise ValueError("Designer CSV must include a 'brand' column")

        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        create_designers_table(conn, table_name)

        allowed_columns = [
            "brand",
            "founded_year",
            "creative_director",
            "ceo",
            "city",
            "country",
            "headquarters",
            "website",
            "notes",
        ]
        insert_columns = [col for col in allowed_columns if col in headers_map]
        insert_sql = f"INSERT INTO {table_name} ({', '.join(insert_columns)}) VALUES ({', '.join('?' for _ in insert_columns)})"

        rows: List[tuple] = []
        for row in reader:
            values = []
            for column in insert_columns:
                raw_name = headers_map[column]
                value = row.get(raw_name, "")
                values.append(value.strip() if isinstance(value, str) else value)
            rows.append(tuple(values))

        if rows:
            conn.executemany(insert_sql, rows)
        return len(rows)


def seed_designers_table_from_dresses(
    conn: sqlite3.Connection,
    dresses_table: str = "dresses",
    designers_table: str = "designers",
) -> int:
    conn.execute(f"DROP TABLE IF EXISTS {designers_table}")
    create_designers_table(conn, designers_table)
    conn.execute(
        f"INSERT INTO {designers_table} (brand) SELECT DISTINCT brand FROM {dresses_table} ORDER BY brand"
    )
    cursor = conn.execute(f"SELECT COUNT(*) FROM {designers_table}")
    return cursor.fetchone()[0] or 0


def load_csv_to_sqlite(
    csv_path: Path,
    db_path: Path,
    table_name: str = "dresses",
    designers_csv: Path | None = None,
    create_designers: bool = False,
    designers_table: str = "designers",
) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = [normalize_column_name(name) for name in reader.fieldnames or []]
        if not fieldnames:
            raise ValueError("CSV contains no columns")

        columns_sql = [f"{col} TEXT" for col in fieldnames]
        rows = [tuple((row.get(name) or "").strip() for name in reader.fieldnames) for row in reader]

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(f"CREATE TABLE {table_name} ({', '.join(columns_sql)})")
        if rows:
            insert_sql = f"INSERT INTO {table_name} ({', '.join(fieldnames)}) VALUES ({', '.join('?' for _ in fieldnames)})"
            conn.executemany(insert_sql, rows)

        designers_count = 0
        if designers_csv:
            designers_count = load_designers_csv_to_sqlite(designers_csv, conn, designers_table)
        elif create_designers:
            designers_count = seed_designers_table_from_dresses(conn, table_name, designers_table)

        conn.commit()

    print(f"Created database '{db_path}' with table '{table_name}' containing {len(rows)} rows.")
    if designers_csv:
        print(f"Created designers table '{designers_table}' with {designers_count} rows from {designers_csv}.")
    elif create_designers:
        print(f"Created designers table '{designers_table}' with {designers_count} brands seeded from dresses.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load a CSV file into a SQLite database as a dresses table and optionally create a designers table."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("dresses.csv"),
        help="Path to the source CSV file.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("dresses.db"),
        help="Path to the output SQLite database file.",
    )
    parser.add_argument(
        "--table",
        type=str,
        default="dresses",
        help="Name of the SQLite table to create.",
    )
    parser.add_argument(
        "--designers-csv",
        type=Path,
        help="Optional designers CSV file containing columns like brand, creative_director, founded_year, country_of_origin, headquarters, website, notes.",
    )
    parser.add_argument(
        "--create-designers-table",
        action="store_true",
        help="Create a designers table seeded with unique brands from the dresses table.",
    )
    parser.add_argument(
        "--designers-table",
        type=str,
        default="designers",
        help="Name of the designers table to create.",
    )

    args = parser.parse_args()
    load_csv_to_sqlite(
        args.csv,
        args.db,
        args.table,
        designers_csv=args.designers_csv,
        create_designers=args.create_designers_table,
        designers_table=args.designers_table,
    )


if __name__ == "__main__":
    main()
