# RowSpect

**Local-first data quality profiling for CSV and Excel files.**

RowSpect turns a messy spreadsheet into an immediate, understandable quality report. Upload a `.csv` or `.xlsx` file, inspect missing values, duplicates, suspicious types, constant columns, and potential numeric outliers, then export a cleaned CSV or standalone HTML report.

RowSpect is intentionally small and privacy-conscious: the application contains no cloud upload, account system, analytics SDK, or telemetry integration.

## What it demonstrates

- Python data engineering with pandas
- deterministic data-quality rules and scoring
- CSV and multi-sheet Excel ingestion
- local-first Streamlit interface
- conservative data cleaning without silent imputation
- HTML and JSON report generation
- unit-tested analysis logic

## Features

- CSV and Excel (`.xlsx`) upload
- Excel sheet selection
- dataset health score from 0–100
- row, column, missing-value, and duplicate summaries
- per-column type, uniqueness, missingness, top-value, and numeric statistics
- blank-string detection
- constant-column detection
- possible numeric-as-text detection
- IQR-based potential outlier detection
- optional duplicate removal and whitespace cleanup
- cleaned CSV download
- standalone HTML report download
- machine-readable JSON profile export

## Quick start

Requires Python 3.11+.

```bash
git clone https://github.com/LUKEcheadle-ship-it/RowSpect.git
cd RowSpect
python -m venv .venv
```

Activate the environment, then install and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Or install the package with development dependencies:

```bash
pip install -e ".[dev]"
pytest
streamlit run app.py
```

A deliberately messy example is included at `sample_data/messy_customers.csv`.

## How the quality score works

The score starts at 100 and applies bounded penalties for:

- missing cells
- duplicate rows
- blank strings
- constant columns
- potential IQR outliers

The score is a fast review aid, not a statement that the data is objectively correct. Outliers and inferred type hints are surfaced for human review rather than automatically changed.

## Privacy

RowSpect reads uploaded data into the running Streamlit process and performs analysis locally in that session. The project does not include telemetry, cloud storage, remote APIs, or an upload backend.

As with any local tool, users are responsible for where they run it and who can access that machine or Streamlit server.

## Tests

```bash
pytest
```

The test suite covers profiling, duplicate detection, numeric-text hints, conservative cleaning, CSV ingestion, and HTML escaping.

## Project structure

```text
app.py                  Streamlit interface
rowspect/
  clean.py              conservative cleaning operations
  io.py                 CSV/XLSX loaders
  profile.py            deterministic profiling and quality score
  report.py             standalone HTML report generator
sample_data/            safe example data
tests/                  unit tests
```

## Scope

RowSpect v0.1 focuses on small-to-medium local CSV and Excel datasets. It is not intended to replace a data warehouse observability platform or perform domain-specific validation without user-defined rules.

## License

MIT
