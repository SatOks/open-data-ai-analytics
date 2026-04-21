from __future__ import annotations

from pathlib import Path

from src.data_quality_analysis import generate_quality_report
from services.common import get_env, load_dataframe_from_sqlite, wait_for_file, write_json


def _serialize_quality_report(report: dict) -> dict:
    missing_values = report["missing_values"]
    data_types = report["data_types"]
    duplicates = report["duplicates"]

    data_types_serialized = data_types.copy()
    if "dtype" in data_types_serialized.columns:
        data_types_serialized["dtype"] = data_types_serialized["dtype"].astype(str)

    duplicate_rows_df = duplicates.get("duplicate_rows")
    duplicate_samples = []
    if duplicate_rows_df is not None and not duplicate_rows_df.empty:
        duplicate_samples = duplicate_rows_df.head(20).to_dict(orient="records")

    return {
        "basic_info": report["basic_info"],
        "missing_values": missing_values.to_dict(orient="records") if not missing_values.empty else [],
        "duplicates": {
            "total_duplicates": int(duplicates.get("total_duplicates", 0)),
            "duplicate_percentage": float(duplicates.get("duplicate_percentage", 0.0)),
            "sample_rows": duplicate_samples,
        },
        "data_types": data_types_serialized.to_dict(orient="records"),
        "outliers": report["outliers"],
    }


def main() -> None:
    sqlite_path = Path(get_env("SQLITE_PATH", "/app/runtime/db/life_expectancy.db"))
    table_name = get_env("DB_TABLE", "life_expectancy")
    quality_report_path = Path(get_env("QUALITY_REPORT_PATH", "/app/runtime/results/quality_report.json"))

    wait_for_file(sqlite_path, timeout=180, interval=2.0)
    df = load_dataframe_from_sqlite(sqlite_path, table_name)

    report = generate_quality_report(df)
    serialized = _serialize_quality_report(report)
    output = write_json(quality_report_path, serialized)

    print(f"Data quality analysis completed. Report saved to: {output}")


if __name__ == "__main__":
    main()
