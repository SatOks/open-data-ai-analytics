# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-02-24

### Added
- Initial project structure with modular Python architecture
- `data_load.py` — data loading module with Kaggle API support (5 functions)
- `data_quality_analysis.py` — data quality checks: missing values, duplicates, outliers via IQR and Z-score (7 functions)
- `data_research.py` — hypothesis testing and ML modeling: Linear Regression, Random Forest, Gradient Boosting (10 functions)
- `visualization.py` — comprehensive plotting module: distributions, correlation matrix, scatter plots, feature importance, model predictions (8 functions)
- Jupyter notebooks `01`–`04` covering the full data science workflow
- `reports/figures/` with generated plots at 300 DPI
- `README.md` with project description and research hypotheses
- `requirements.txt` with all Python dependencies
- `LAB_REPORT_VISUAL.md` — full visual lab report

### Git Workflow
- Feature branch workflow with 4 branches: `feature/data_load`, `feature/data_quality_analysis`, `feature/data_research`, `feature/visualization`
- All merges performed with `--no-ff` flag to preserve branch history
- Intentional merge conflict created and resolved in `update-about-section-v1/v2` branches
- Conventional commits used throughout (`feat`, `docs`, `chore`)

### Results
- Hypothesis 1 confirmed: GDP correlates with Life Expectancy (r = 0.46, p < 0.001)
- Hypothesis 2 confirmed: Immunization reduces child mortality (r = −0.62, p < 0.001)
- Hypothesis 3 confirmed: Random Forest achieves R² = 0.92 on test set

[0.1.0]: https://github.com/username/open-data-ai-analytics/releases/tag/v0.1.0
