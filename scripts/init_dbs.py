from pathlib import Path

import duckdb

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DBS = {
    "bronze": DATA_DIR / "bronze.duckdb",
    "silver": DATA_DIR / "silver.duckdb",
    "gold": DATA_DIR / "gold.duckdb",
}


def init_databases():
    """Create the 3-tier DuckDB databases if they don't exist."""
    DATA_DIR.mkdir(exist_ok=True)

    for name, db_path in DBS.items():
        if not db_path.exists():
            print(f"Creating {name} database at {db_path}")
            duckdb.connect(str(db_path)).close()
        else:
            print(f"The {name} database already exists at {db_path}")


if __name__ == "__main__":
    init_databases()
    print("All DuckDB databases have been initialized")
