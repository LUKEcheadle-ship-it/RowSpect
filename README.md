# RowSpect

**Catch spreadsheet problems before they reach a dashboard, model, report, or decision.**

Local-first CSV/XLSX data quality profiling, validation, safe cleanup, comparison, and reusable rule profiles.

RowSpect turns a messy spreadsheet into an immediate, explainable quality review. Open a `.csv` or `.xlsx` file, inspect structural problems, explore the data, define business-specific validation rules, preview safe type conversions, then export a cleaned file or standalone report.

RowSpect 1.3.0 is deliberately local and small: there is **no RowSpect cloud upload, account system, telemetry, analytics SDK, or AI API**.

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

## 1.3 capability map

| Workflow | What RowSpect demonstrates |
| --- | --- |
| Inspect | deterministic profiling, quality score, missingness, duplicates, types, and outlier signals |
| Validate | reusable rules, cross-column comparisons, and row-level failure reasons |
| Compare | current-vs-baseline schema, rows, missingness, medians, categories, and score changes |
| Convert | strict text/integer/float/boolean/date/datetime conversion with bounds and precision checks |
| Clean and export | conservative cleanup, failing-row CSVs, formula-safe CSV/XLSX, JSON, and HTML reports |

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

## New in 1.3

- Compare a current file with a previous baseline from the Streamlit Compare tab or the CLI.
- Add `compare_columns` rules with `eq`, `ne`, `lt`, `le`, `gt`, and `ge` in numeric, date, or text mode.
- Export each failing source row once with its spreadsheet row number, failed rule IDs, and human-readable reasons.
- Preserve identifiers and literal codes such as `00123`, `NA`, and `NULL`; use `--preserve-text` when all CSV fields must remain text.
- Harden explicit integer and float conversion against Int64 overflow, fractional values, non-finite values, and meaningful precision loss.

Comparison is descriptive change detection, not statistical significance testing, and the generic quality score is a review aid—not proof that a dataset is correct.

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

Compare files and write deterministic JSON:

```bash
rowspect current.csv \
  --baseline previous.csv \
  --comparison-json comparison.json
```

Export failed records from a reusable validation profile:

```bash
rowspect customers.csv \
  --rules-profile customer-rules.json \
  --failing-rows failing-rows.csv \
  --fail-on-validation
```

The failing-row file can contain original source data. Handle it with the same care as the input file.

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

The test suite covers CSV encodings/delimiters and identifier safety, Excel sheets and corruption, structural profiling, score output, cleanup, formula-safe exports, HTML escaping, chart helpers, CLI behavior, custom and cross-column validation, strict conversions, comparisons, failing-row exports, and reusable rule profiles. Exact release qualification evidence is recorded in the changelog and launch notes after the final candidate passes.

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
  comparison.py         descriptive current-vs-baseline comparison
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
