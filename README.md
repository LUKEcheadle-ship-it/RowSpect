# RowSpect

**Catch spreadsheet problems before they reach a dashboard, model, report, or decision.**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Local-first](https://img.shields.io/badge/processing-local--first-6f42c1)](#privacy-and-safety)
[![Release qualification](https://img.shields.io/badge/tests-82%2F82%20passing-brightgreen)](#release-qualification)

**RowSpect is a local-first CSV/XLSX data quality checker for analysts and data practitioners.** Upload a spreadsheet, see what looks wrong, define reusable validation rules, preview safe type conversions, clean common issues, and export the result — without sending the dataset to a RowSpect cloud service.

> No RowSpect account. No project-operated upload backend. No telemetry. No analytics SDK. No AI API required.

## Why RowSpect

A spreadsheet can look fine and still contain duplicate records, missing values, bad dates, numeric values stored as text, unexpected categories, or structural problems that break downstream work.

RowSpect gives you a fast answer to a simple question:

> **Is this file clean and consistent enough to trust downstream?**

It is designed for people who want more than manual spreadsheet inspection but do not want to stand up a full warehouse data-quality platform just to review a CSV or Excel file.

### RowSpect is useful when you need to

- check a spreadsheet before loading it into Power BI, Tableau, Python, SQL, or a model
- catch missing values, duplicate rows, suspicious types, constant columns, and potential outliers
- enforce rules like **“Customer ID must be unique”** or **“Revenue cannot be negative”**
- reuse the same checks on recurring weekly or monthly files
- safely convert compatible text, number, boolean, and date columns
- clean conservative issues without silently guessing values
- export a cleaned file plus HTML/JSON evidence of what was found
- keep the dataset on the machine where RowSpect is running

## What RowSpect does

| Capability | RowSpect 1.2 |
| --- | --- |
| **Inputs** | CSV and multi-sheet XLSX |
| **Automatic profiling** | Missing values, blanks, duplicate rows, duplicate headers, constants, numeric-text hints, IQR outliers, column statistics |
| **Business rules** | Required, unique, numeric range, allowed values, regex, and date validation |
| **Safe conversion** | Text, integer, float, boolean, date, and datetime |
| **Cleanup** | Trim whitespace, normalize blanks, remove exact duplicates, remove empty rows |
| **Exports** | Cleaned CSV/XLSX, converted CSV/XLSX, HTML report, JSON profile, validation JSON |
| **Reusable checks** | Portable JSON validation/conversion profiles |
| **Interfaces** | Streamlit UI, Python API, CLI |
| **Privacy model** | Local processing; no RowSpect cloud upload backend |

## Try it in about a minute

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

Open the local URL printed by Streamlit and enable the built-in synthetic sample if you want to try RowSpect without using your own file.

### Typical workflow

1. **Upload** a CSV or Excel workbook.
2. **Inspect** the quality score, review signals, column statistics, and charts.
3. **Validate** business-specific expectations with reusable rules.
4. **Preview conversions** before changing any column type.
5. **Clean** conservative issues without imputation or guessed repairs.
6. **Export** the cleaned data and a standalone report.

## Reusable validation rules

RowSpect 1.2 lets you define what “good data” means for a specific file type.

Supported rules:

- required fields
- unique fields
- numeric minimum/maximum ranges
- allowed-value lists
- full-match regular expressions
- valid-date checks with an optional explicit date format

Validation results show which rules pass or fail, how many values violate each rule, and the affected spreadsheet-style row numbers.

Example rules:

- `Customer ID` must be unique
- `Revenue` must be greater than or equal to 0
- `State` must be one of an approved set of values
- `Email` must match a configured pattern
- `Order Date` must contain a valid date

## Strict type conversion

RowSpect can preview and explicitly convert columns to:

- text
- integer
- float
- boolean
- date
- datetime

Conversions are **strict by default**. If a non-empty value cannot be converted safely, RowSpect blocks that conversion rather than silently replacing the value, partially converting the column, or guessing.

The original uploaded dataframe remains unchanged.

## Reusable profiles

Save validation rules and optional conversion plans as a small JSON profile and reuse them on the next file of the same kind.

Profiles contain configuration only — not source dataset rows.

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

Stored conversions are never applied implicitly:

```bash
rowspect customers.csv \
  --rules-profile customer-rules.json \
  --apply-profile-conversions
```

## CLI

Install the package locally:

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

## Explainable quality scoring

The generic quality score is a **review aid, not a truth score**.

RowSpect applies visible deductions for problems such as missing cells, duplicate rows, blanks, constant columns, potential outliers, and structural issues. It does not pretend that a high score proves every real-world value is correct.

Business-specific expectations stay explicit through validation rules.

## Privacy and safety

RowSpect is intentionally local-first.

- uploads are processed inside the running Streamlit/Python process
- there is no RowSpect-hosted upload backend
- no telemetry or analytics SDK is required
- spreadsheet formula-like text is neutralized on export by default
- malformed, corrupt, encrypted, and implausibly expanded XLSX files are rejected
- uploads are limited to 50 MB
- XLSX expansion is capped at 250 MB uncompressed
- reusable rule profiles are size-limited and validated before use
- strict conversions never mutate the original upload

RowSpect is **not a malware sandbox** and is not presented as a hardened Internet-facing multi-tenant service.

See [`SECURITY.md`](SECURITY.md) and [`docs/SAFETY_REVIEW.md`](docs/SAFETY_REVIEW.md) for the full security model and accepted limitations.

## Release qualification

RowSpect 1.2 completed its release checklist with:

- **82/82 automated tests passing** in the qualified environment
- strict `python scripts/qualify_release.py --require-ui` gate passing
- real CSV and XLSX browser uploads passing
- multi-sheet workbook switching passing
- all six custom validation rule types exercised
- all six conversion targets exercised
- unsafe conversion blocking verified
- reusable profile round trip verified
- cleanup controls tested independently and in combination
- malformed and oversized upload handling verified
- cleaned and converted CSV/XLSX outputs independently reopened with pandas/openpyxl
- public-release audit, wheel build, CLI smoke, and rule-profile smoke passing

A synthetic **100,000 × 20** profiling benchmark completed in **1.149 seconds** in the qualification environment. Results vary by hardware and dataset.

See [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) for the exact qualification notes.

## Conservative cleaning

RowSpect can:

- remove exact duplicate rows
- trim leading/trailing whitespace
- convert blank text to missing values
- remove completely empty rows
- apply explicitly configured type conversions when every non-empty value is compatible

It deliberately does **not** impute missing values or guess how invalid values should be repaired.

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
docs/                   deployment, safety, rules, and release guidance
tests/                  automated core tests
```

## Scope

RowSpect targets small-to-medium local CSV and Excel datasets. It is not a data warehouse observability service, malware scanner, multi-tenant SaaS security boundary, or replacement for manual review of high-stakes data.

## Contributing

Issues, bug reports, and focused feature ideas are welcome. Useful additions should preserve RowSpect's small, local-first, explainable scope.

## License

MIT. See [`LICENSE`](LICENSE).
