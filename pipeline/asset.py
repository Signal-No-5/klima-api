from functools import wraps
from time import sleep, time
import logging

import duckdb, pandas as pd

from pipeline.config import db
from pipeline.utils.timestamp import right_now


class AssetContext:
    """Shared context injected into every asset."""
    def __init__(self, name, stage, logger):
        self.name = name
        self.stage = stage
        self.right_now = right_now
        self.log = logger.info
        self.warn = logger.warning
        self.error = logger.error


def run_with_retries(task, retry, backoff, ctx):
    """Retry wrapper for any callable."""
    for attempt in range(1, retry + 1):
        try:
            return task()
        except Exception as e:
            ctx.error(f"Attempt {attempt}/{retry} failed: {e}")
            if attempt < retry:
                ctx.warn(f"Retrying in {backoff}s...")
                sleep(backoff)
            else:
                ctx.error(f"❌ {ctx.name} failed after {retry} retries.")
                raise


def load(records, name, stage, schema, dedupe_key, parents):
    """Handles schema creation, deduplication, and lineage tracking."""
    if isinstance(records, list):
        df = pd.DataFrame(records)
    elif isinstance(records, pd.DataFrame):
        df = records
    else:
        raise TypeError(
            "Asset must return a DataFrame or list of dicts, got"
            + type(records)
        )

    db_path = getattr(db, stage.upper(), None)
    if not db_path:
        raise ValueError(f"No database configured for stage '{stage}'")

    with duckdb.connect(db_path) as con:
        con.execute(f"CREATE TABLE IF NOT EXISTS {name} ({schema})")
        
        # Automatic timestamps
        df['inserted_at'] = right_now()

        con.register("df", df)

        if dedupe_key:
            con.execute(f"""
                INSERT INTO {name}
                SELECT d.*
                FROM df d
                LEFT JOIN {name} t
                ON d.{dedupe_key} = t.{dedupe_key}
                WHERE t.{dedupe_key} IS NULL
            """)
        else:
            con.execute(f"INSERT INTO {name} SELECT * FROM df")

        if parents:
            print("to-do") # to-do
            
    return len(df)


def asset(
    name: str,
    stage: str,
    schema: str,
    dedupe_key: str | None = None,
    retry: int = 3,
    backoff: int = 5,
    parents: list[str] | None = None,
    log_level: str = "INFO",
):
    """
    General-purpose decorator for all pipeline assets.

    Handles:
      • Table creation
      • Deduplication (if key provided)
      • Retries with backoff
      • Lineage metadata
      • Logging

    Usage:
        @asset(
            name="pagasa_warnings",
            stage="bronze",
            schema=\"\"\"
                source_id VARCHAR PRIMARY KEY,
                inserted_at TIMESTAMP,
                hazard VARCHAR,
                payload JSON
            \"\"\",
            dedupe_key="source_id",
        )
        def pagasa_warnings(ctx):
            ...
            return records
    """

    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    if not logger.hasHandlers():
        logger.addHandler(handler)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx = AssetContext(name, stage, logger)

            def task():
                ctx.log(f"🏗️ Running asset {name} (stage={stage})")
                start = time()
                records = func(ctx, *args, **kwargs)
                rows = load(records, name, stage, schema, dedupe_key, parents)
                ctx.log(f"✅ {name} done: {rows} rows in {time() - start}s")

            return run_with_retries(task, retry, backoff, ctx)
        return wrapper
    return decorator
