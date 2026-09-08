# Contributing to RowSpect

RowSpect aims to stay small, deterministic, and easy to inspect.

## Local setup

```bash
python -m venv .venv
pip install -e ".[dev]"
pytest
streamlit run app.py
```

## Good contribution areas

- new deterministic data-quality checks with tests
- CSV/XLSX parsing edge cases
- accessibility and UI improvements
- sample datasets that contain no private or licensed data
- report formatting improvements

Please avoid adding telemetry, cloud uploads, secrets, proprietary datasets, or automatic destructive data transformations.
