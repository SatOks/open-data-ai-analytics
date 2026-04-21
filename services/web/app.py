from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, send_from_directory

from services.common import get_env

app = Flask(__name__, template_folder="templates", static_folder="static")

SQLITE_PATH = Path(get_env("SQLITE_PATH", "/app/runtime/db/life_expectancy.db"))
DB_TABLE = get_env("DB_TABLE", "life_expectancy")
LOAD_SUMMARY_PATH = Path(get_env("LOAD_SUMMARY_PATH", "/app/runtime/results/load_summary.json"))
QUALITY_REPORT_PATH = Path(get_env("QUALITY_REPORT_PATH", "/app/runtime/results/quality_report.json"))
RESEARCH_REPORT_PATH = Path(get_env("RESEARCH_REPORT_PATH", "/app/runtime/results/research_report.json"))
FIGURES_DIR = Path(get_env("FIGURES_DIR", "/app/runtime/results/figures"))


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_preview(limit: int = 20) -> dict:
    if not SQLITE_PATH.exists():
        return {"columns": [], "rows": []}

    query = f'SELECT * FROM "{DB_TABLE}" LIMIT {limit}'
    with sqlite3.connect(SQLITE_PATH) as conn:
        preview_df = pd.read_sql_query(query, conn)

    return {
        "columns": preview_df.columns.tolist(),
        "rows": preview_df.to_dict(orient="records"),
    }


def _list_figures() -> list[str]:
    if not FIGURES_DIR.exists():
        return []
    return sorted([p.name for p in FIGURES_DIR.glob("*.png")])


@app.route("/health")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@app.route("/figures/<path:filename>")
def get_figure(filename: str):
    return send_from_directory(FIGURES_DIR, filename)


@app.route("/")
def index():
    preview = _read_preview()
    load_summary = _load_json(LOAD_SUMMARY_PATH)
    quality_report = _load_json(QUALITY_REPORT_PATH)
    research_report = _load_json(RESEARCH_REPORT_PATH)
    figures = _list_figures()

    return render_template(
        "index.html",
        preview=preview,
        load_summary=load_summary,
        quality_report=quality_report,
        research_report=research_report,
        figures=figures,
    )


if __name__ == "__main__":
    web_port = int(get_env("WEB_PORT", "8080"))
    app.run(host="0.0.0.0", port=web_port)
