# RowSpect

**Local-first data quality profiling for CSV and Excel files.**

RowSpect turns a messy spreadsheet into an immediate, explainable quality review. Open a `.csv` or `.xlsx` file, inspect missing values, duplicates, suspicious types, constant columns, and potential numeric outliers, explore the data visually, then export a cleaned file or standalone report.

RowSpect 1.1 is deliberately local and small: there is **no RowSpect cloud upload, account system, telemetry, analytics SDK, or AI API**.

## Why this project

RowSpect demonstrates a complete small data product rather than a notebook-only analysis:

- Python and pandas data engineering
- defensive CSV/XLSX ingestion
- deterministic, explainable data-quality rules
- Streamlit product UI
- safe spreadsheet and HTML exports
- command-line tooling
- unit-tested core logic
- privacy-conscious local processing

## Production hardening

RowSpect 1.1 adds a repeatable release and deployment path rather than relying on a developer machine:

- non-root Docker image with an HTTP health check
- Streamlit XSRF/CORS protections left enabled
- 50 MB upload limit enforced by both Streamlit configuration and RowSpect validation
- 250 MB maximum uncompressed XLSX size and 10,000 archive-entry limit
- real duplicate CSV/XLSX headers preserved and surfaced as structural issues
- formula-like spreadsheet text neutralized on export by default
- `rowspect --doctor` dependency/runtime check
- package wheel build, CLI smoke, public-release audit, and automated tests in one qualification command
- strict live Streamlit server smoke available before release

Run the non-UI qualification gate with:

```bash
python scripts/qualify_release.py
```

The final release gate is stricter:

```bash
python scripts/qualify_release.py --require-ui
```

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) and [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md).

## V1 features

- CSV and Excel (`.xlsx`) input, including multi-sheet workbooks
- 50 MB upload guard plus XLSX archive-expansion limits
- delimiter detection for comma, semicolon, tab, and pipe-delimited CSVs
- UTF-8, UTF-8 BOM, and Latin-1 CSV handling
- 0–100 quality score with visible deductions
- critical / warning / informational issue severity
- missing and blank values
- exact duplicate rows and duplicate column names
- all-missing and constant columns
- possible numbers stored as text
- IQR-based potential numeric outliers
- per-column statistics and cardinality
- missingness chart, numeric distributions, top text values, and correlation matrix
- conservative cleanup without silent imputation or type conversion
- cleaned CSV and Excel download
- optional formula-like text neutralization for spreadsheet exports
- standalone HTML report and JSON profile
- CLI for scriptable local profiling

## Quick start

Requires **Python 3.11+**.

```bash
git clone https://github.com/LUKEcheadle-ship-it/RowSpect.git
cd RowSpect
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints in the terminal. You can also enable the built-in sample from the sidebar before choosing your own file.

## CLI

Install the package:

```bash
pip install -e .
```

Profile a CSV:

```bash
rowspect sample_data/messy_customers.csv
```

Write machine-readable and standalone reports:

```bash
rowspect sample_data/messy_customers.csv \
  --json rowspect-profile.json \
  --html rowspect-report.html
```

For Excel workbooks:

```bash
rowspect workbook.xlsx --list-sheets
rowspect workbook.xlsx --sheet "Sheet 2"
```

## What the score means

The quality score begins at 100 and applies bounded deductions for:

- missing cells
- duplicate rows
- blank strings
- constant columns
- potential IQR outliers
- structural problems such as duplicate columns or an empty dataset

The score is **a review aid, not a truth score**. A legitimate extreme value can be an IQR outlier, and a dataset can score highly while still containing domain-specific errors RowSpect cannot know about.

## Conservative cleaning

V1 can:

- remove exact duplicate rows
- trim leading/trailing whitespace
- convert blank text to missing values
- remove completely empty rows

It deliberately does **not** impute missing values or silently convert data types.

Spreadsheet exports neutralize text beginning with common formula prefixes by default. This can be disabled when exact literal preservation is more important.

## Privacy and security

Uploaded data is parsed inside the running Streamlit process. RowSpect contains no hosted backend or telemetry code. If you deploy Streamlit to another machine or network, that deployment becomes the place where the file is processed.

See [`SECURITY.md`](SECURITY.md) for file-handling and export-safety details.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

The V1 suite covers CSV encodings/delimiters, Excel sheets and corruption, structural profiling, score output, cleanup, formula-safe exports, HTML escaping, chart helpers, and CLI behavior.

## Project structure

```text
app.py                  Streamlit application
rowspect/
  clean.py              conservative cleanup
  cli.py                command-line interface
  export.py             CSV/XLSX export safety
  insights.py           chart/exploration helpers
  io.py                 defensive CSV/XLSX loading
  profile.py            deterministic profiler and score
  report.py             standalone HTML report
  runtime.py            non-identifying runtime diagnostics
sample_data/            synthetic messy example
scripts/                qualification, smoke, audit, and benchmark tools
docs/                   deployment and release guidance
tests/                  automated core tests
```

## Scope

RowSpect V1 targets small-to-medium local CSV and Excel datasets. It is not a data warehouse observability service, domain-specific validator, malware scanner, or replacement for manual review of high-stakes data.

## License

MIT. See [`LICENSE`](LICENSE).
