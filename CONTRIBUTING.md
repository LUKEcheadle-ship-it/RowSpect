# Contributing to RowSpect

RowSpect is intentionally small. Contributions should improve data-quality usefulness without turning the project into a hosted data platform.

## Development

```bash
python -m venv .venv
# activate the environment
pip install -e ".[dev]"
pytest
streamlit run app.py
```

## Pull requests

Please include:
- a short description of the user-facing change
- tests for new deterministic analysis or export behavior
- no real customer, employer, school, or private datasets
- no telemetry, analytics SDKs, tracking pixels, or silent network calls

Prefer small changes that are easy to review and reproduce.
