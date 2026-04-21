from __future__ import annotations

import json
import math
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

import pandas as pd


def get_env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise ValueError(f"Environment variable '{name}' is required")
    return str(value) if value is not None else ""


def ensure_parent(path: str | Path) -> Path:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path


def ensure_dir(path: str | Path) -> Path:
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def wait_for_file(path: str | Path, timeout: int = 120, interval: float = 2.0) -> Path:
    target = Path(path)
    start = time.time()
    while time.time() - start <= timeout:
        if target.exists():
            return target
        time.sleep(interval)
    raise TimeoutError(f"Timed out waiting for file: {target}")


def load_dataframe_from_sqlite(sqlite_path: str | Path, table_name: str) -> pd.DataFrame:
    db_path = Path(sqlite_path)
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite database was not found: {db_path}")

    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)


def _is_nan(value: Any) -> bool:
    return isinstance(value, float) and math.isnan(value)


def to_builtin(value: Any) -> Any:
    if value is None:
        return None

    if _is_nan(value):
        return None

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, dict):
        return {str(k): to_builtin(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [to_builtin(v) for v in value]

    if hasattr(value, "tolist"):
        try:
            return to_builtin(value.tolist())
        except Exception:
            pass

    if hasattr(value, "item"):
        try:
            return to_builtin(value.item())
        except Exception:
            pass

    return value


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    file_path = ensure_parent(path)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(to_builtin(payload), f, ensure_ascii=False, indent=2)
    return file_path
