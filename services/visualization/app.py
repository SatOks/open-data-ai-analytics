from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("PLOT_SHOW", "0")

from src.visualization import (  # noqa: E402
    plot_correlation_matrix,
    plot_distribution,
    plot_missing_values,
    setup_plot_style,
)
from services.common import get_env, load_dataframe_from_sqlite, wait_for_file


def main() -> None:
    sqlite_path = Path(get_env("SQLITE_PATH", "/app/runtime/db/life_expectancy.db"))
    table_name = get_env("DB_TABLE", "life_expectancy")
    quality_report_path = Path(get_env("QUALITY_REPORT_PATH", "/app/runtime/results/quality_report.json"))
    research_report_path = Path(get_env("RESEARCH_REPORT_PATH", "/app/runtime/results/research_report.json"))
    figures_dir = Path(get_env("FIGURES_DIR", "/app/runtime/results/figures"))

    os.environ["FIGURES_DIR"] = str(figures_dir)

    wait_for_file(sqlite_path, timeout=180, interval=2.0)
    wait_for_file(quality_report_path, timeout=180, interval=2.0)
    wait_for_file(research_report_path, timeout=180, interval=2.0)

    df = load_dataframe_from_sqlite(sqlite_path, table_name)

    setup_plot_style()
    plot_missing_values(df, save=True, filename="missing_values.png")

    if "Life expectancy " in df.columns:
        plot_distribution(df, "Life expectancy ", save=True, filename="distribution_life_expectancy.png")

    plot_correlation_matrix(df, save=True, filename="correlation_matrix.png")
    print(f"Visualizations generated in: {figures_dir}")


if __name__ == "__main__":
    main()
