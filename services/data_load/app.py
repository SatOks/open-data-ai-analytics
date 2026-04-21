from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from services.common import get_env, ensure_parent, write_json


def main() -> None:
    csv_file = Path(get_env("CSV_FILE", "/app/data/raw/Life Expectancy Data.csv"))
    sqlite_path = Path(get_env("SQLITE_PATH", "/app/runtime/db/life_expectancy.db"))
    table_name = get_env("DB_TABLE", "life_expectancy")
    summary_path = Path(get_env("LOAD_SUMMARY_PATH", "/app/runtime/results/load_summary.json"))

    if not csv_file.exists():
        raise FileNotFoundError(
            f"CSV file was not found at {csv_file}. "
            "Mount your dataset into the container and update CSV_FILE if needed."
        )

    df = pd.read_csv(csv_file)
    ensure_parent(sqlite_path)

    with sqlite3.connect(sqlite_path) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    summary = {
        "status": "completed",
        "csv_file": str(csv_file),
        "sqlite_path": str(sqlite_path),
        "table_name": table_name,
        "rows_loaded": int(len(df)),
        "columns_count": int(len(df.columns)),
        "columns": list(df.columns),
    }

    output = write_json(summary_path, summary)
    print(f"Data load completed. Rows loaded: {len(df)}. Summary: {output}")


if __name__ == "__main__":
    main()
