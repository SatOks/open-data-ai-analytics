from __future__ import annotations

from pathlib import Path

from src.data_research import (
    calculate_correlation_with_target,
    compare_models,
    get_feature_importance,
    prepare_data_for_modeling,
    train_linear_regression,
    train_random_forest,
)
from services.common import get_env, load_dataframe_from_sqlite, wait_for_file, write_json


def _extract_metrics(results: dict) -> dict:
    return {
        "train": results["train_metrics"],
        "test": results["test_metrics"],
    }


def main() -> None:
    sqlite_path = Path(get_env("SQLITE_PATH", "/app/runtime/db/life_expectancy.db"))
    table_name = get_env("DB_TABLE", "life_expectancy")
    target_column = get_env("TARGET_COLUMN", "Life expectancy ")
    report_path = Path(get_env("RESEARCH_REPORT_PATH", "/app/runtime/results/research_report.json"))

    wait_for_file(sqlite_path, timeout=180, interval=2.0)
    df = load_dataframe_from_sqlite(sqlite_path, table_name)

    if target_column not in df.columns:
        normalized_map = {col.strip(): col for col in df.columns}
        fallback = normalized_map.get(target_column.strip())
        if fallback:
            target_column = fallback
        else:
            raise ValueError(f"Target column '{target_column}' was not found in table '{table_name}'")

    X_train, X_test, y_train, y_test, features = prepare_data_for_modeling(df, target=target_column)

    linear_results = train_linear_regression(X_train, y_train, X_test, y_test)
    forest_results = train_random_forest(X_train, y_train, X_test, y_test)

    model_results = {
        "Linear Regression": linear_results,
        "Random Forest": forest_results,
    }

    comparison_df = compare_models(model_results)
    best_model = comparison_df.sort_values("Test R²", ascending=False).iloc[0]["Model"]

    correlation_df = calculate_correlation_with_target(df, target=target_column, top_n=10)
    importance_df = get_feature_importance(forest_results, top_n=10)

    report = {
        "status": "completed",
        "target_column": target_column,
        "rows_total": int(len(df)),
        "features_count": int(len(features)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "models": {
            "Linear Regression": _extract_metrics(linear_results),
            "Random Forest": {
                **_extract_metrics(forest_results),
                "feature_importance": forest_results.get("feature_importance", {}),
            },
        },
        "comparison": comparison_df.to_dict(orient="records"),
        "best_model": best_model,
        "top_correlations": correlation_df.to_dict(orient="records"),
        "top_feature_importance": (
            importance_df.to_dict(orient="records") if importance_df is not None else []
        ),
    }

    output = write_json(report_path, report)
    print(f"Data research completed. Report saved to: {output}")


if __name__ == "__main__":
    main()
