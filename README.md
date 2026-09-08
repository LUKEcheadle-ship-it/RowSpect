# RowSpect

**Local-first data quality profiling, validation, and safe cleanup for CSV and Excel files.**

RowSpect turns a messy spreadsheet into an immediate, explainable quality review. Open a `.csv` or `.xlsx` file, inspect structural problems, explore the data, define business-specific validation rules, preview safe type conversions, then export a cleaned file or standalone report.

RowSpect 1.2.0 is deliberately local and small: there is **no RowSpect cloud upload, account system, telemetry, analytics SDK, or AI API**.

## Why this project

RowSpect is a complete small data product rather than a notebook-only analysis:

- Python and pandas data engineering
- defensive CSV/XLSX ingestion
- deterministic, explainable data-quality rules
- reusable business validation profiles
- explicit type-conversion previews
- Streamlit product UI
- safe spreadsheet and HTML exports
- command-line tooling
- unit-tested core logic
- privacy-conscious local processing

## New in 1.2

### Custom validation rules

Define what good data means for your own dataset. RowSpect supports:

- required fields
- unique fields
- numeric minimum/maximum ranges
- allowed-value lists
- full-match regular expressions
- valid-date checks with an optional explicit date format

Validation results show which rules pass or fail, how many values violate each rule, and the affected spreadsheet-style row numbers.

### Safe type conversion

Preview and explicitly convert columns to:

- text
- integer
- float
- boolean
- date
- datetime

Conversions are **strict by default**. If even one non-empty value cannot be converted safely, that conversion is blocked rather than silently replacing the value or guessing.

### Reusable profiles

Save validation rules and optional conversion plans as a small JSON profile, then load that profile the next time the same kind of spreadsheet arrives. Profiles contain configuration only; they do not contain source dataset rows.

The same profile can be used from the UI or CLI:

```bash
rowspect customers.csv --rules-profile customer-rules.json
```

For pipeline-style validation:

```bash
rowspect customers.csv \
  --rules-profile customer-rules.json \
  --validation-json validation-results.json \
  --fail-on-validation
```

Stored conversion plans are never applied implicitly. Opt in explicitly:

```bash
rowspect customers.csv \
  --rules-profile customer-rules.json \
  --apply-profile-conversions
```

## Production hardening

RowSpect includes a repeatable release and deployment path rather than relying on one developer machine:

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

## Core quality checks

- CSV and Excel (`.xlsx`) input, including multi-sheet workbooks
- 50 MB upload guard plus XLSX archive-expansion limits
- delimiter detection for comma, semicolon, tab, and pipe-delimited CSVs
- UTF-8, UTF-8 BOM, and Latin-1 CSV handling
- 0–100 generic quality score with visible deductions
- critical / warning / informational issue severity
- missing and blank values
- exact duplicate rows and duplicate column names
- all-missing and constant columns
- possible numbers stored as text
- IQR-based potential numeric outliers
- per-column statistics and cardinality
- missingness chart, numeric distributions, top text values, and correlation matrix
- conservative cleanup without silent imputation
- cleaned CSV and Excel download
- standalone HTML report and JSON profile

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

Write machine-readable and standalone generic reports:

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

## What the generic score means

The generic quality score begins at 100 and applies bounded deductions for:

- missing cells
- duplicate rows
- blank strings
- constant columns
- potential IQR outliers
- structural problems such as duplicate columns or an empty dataset

The score is **a review aid, not a truth score**. A legitimate extreme value can be an IQR outlier, and a dataset can score highly while still containing domain-specific errors RowSpect cannot know about. Custom validation rules are separate from this generic score so business-specific expectations stay explicit.

## Conservative cleaning

RowSpect can:

- remove exact duplicate rows
- trim leading/trailing whitespace
- convert blank text to missing values
- remove completely empty rows
- apply explicitly configured type conversions when every non-empty value is compatible

It deliberately does **not** impute missing values or guess how invalid values should be repaired.

Spreadsheet exports neutralize text beginning with common formula prefixes by default. This can be disabled when exact literal preservation is more important.

## Privacy and security

Uploaded data is parsed inside the running Streamlit process. RowSpect contains no hosted backend or telemetry code. If you deploy Streamlit to another machine or network, that deployment becomes the place where the file is processed.

Reusable rule profiles contain rule names, column references, validation parameters, and optional conversion plans—not the dataset itself.

See [`SECURITY.md`](SECURITY.md) for file-handling and export-safety details.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

The test suite covers CSV encodings/delimiters, Excel sheets and corruption, structural profiling, score output, cleanup, formula-safe exports, HTML escaping, chart helpers, CLI behavior, custom validation, strict conversions, and reusable rule profiles.

## Project structure

```text
app.py                  Streamlit application
rowspect/
  clean.py              conservative cleanup
  cli.py                command-line interface
  conversion.py         explicit safe type conversion
  export.py             CSV/XLSX export safety
  insights.py           chart/exploration helpers
  io.py                 defensive CSV/XLSX loading
  profile.py            deterministic generic profiler and score
  report.py             standalone HTML report
  rule_profiles.py      reusable JSON validation/conversion profiles
  runtime.py            non-identifying runtime diagnostics
  validation.py         user-defined validation rules
sample_data/            synthetic messy example
scripts/                qualification, smoke, audit, and benchmark tools
docs/                   deployment and release guidance
tests/                  automated core tests
```

## Scope

RowSpect targets small-to-medium local CSV and Excel datasets. It is not a data warehouse observability service, malware scanner, or replacement for manual review of high-stakes data. Custom rules make domain expectations explicit, but RowSpect still cannot determine whether an arbitrary real-world value is factually correct without a rule describing that expectation.

## License

MIT. See [`LICENSE`](LICENSE).
