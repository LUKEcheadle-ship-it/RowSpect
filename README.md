# RowSpect

**Know what is wrong with a spreadsheet before it reaches a dashboard, model, or report.**

RowSpect is a local-first data quality tool for CSV and Excel files. Drop in a spreadsheet, get an explainable quality review, define reusable business rules, preview safe type conversions, clean common problems, and export the result — without sending the dataset to a RowSpect cloud service.

> RowSpect 1.2.0 is deliberately small and local: no account system, no project-operated upload backend, no telemetry, no analytics SDK, and no AI API.

## Why RowSpect

Most spreadsheet quality problems are discovered manually: missing values, duplicate records, inconsistent types, unexpected categories, bad dates, or a column that quietly changed between reports. RowSpect turns that review into a repeatable workflow that an analyst can understand without first building a data-quality platform.

**Use RowSpect when you want to:**

- inspect a CSV or XLSX file before using it downstream
- find missing, duplicate, structural, type, and outlier signals quickly
- define business rules such as “Customer ID must be unique” or “Revenue cannot be negative”
- safely convert text numbers, dates, booleans, and other compatible columns
- reuse the same validation rules on recurring files
- export a cleaned spreadsheet plus HTML/JSON evidence of the review
- keep the dataset on the machine where RowSpect is running

RowSpect is intentionally narrower than a warehouse observability platform and more validation-focused than a general-purpose data transformation workbench. It is built for local, spreadsheet-first review.

## What you get

| Area | RowSpect 1.2 |
| --- | --- |
| Inputs | CSV and multi-sheet XLSX |
| Generic profiling | Missing values, blanks, duplicates, duplicate headers, constants, numeric-text hints, IQR outliers, column statistics |
| Business validation | Required, unique, numeric range, allowed values, regex, and date rules |
| Safe conversion | Text, integer, float, boolean, date, and datetime |
| Cleanup | Trim whitespace, normalize blanks, remove exact duplicates, remove empty rows |
| Outputs | Cleaned CSV/XLSX, converted CSV/XLSX, HTML report, JSON profile, validation JSON |
| Reuse | Portable JSON rule/conversion profiles |
| Interfaces | Streamlit UI, Python API, CLI |
| Privacy model | Local processing; no RowSpect cloud upload backend |

## A typical workflow

1. **Upload** a CSV or Excel workbook.
2. **Inspect** the quality score, review signals, column statistics, and charts.
3. **Validate** business-specific expectations with reusable rules.
4. **Preview conversions** before changing any column type.
5. **Clean** conservative issues without imputation or guessed repairs.
6. **Export** the cleaned data and a standalone report.

The generic quality score is a review aid, not a truth score. RowSpect can identify suspicious structure and values, but it cannot know whether an arbitrary real-world value is factually correct unless you define a rule describing that expectation.

## New in 1.2

### Reusable validation rules

Define what good data means for your dataset:

- required fields
- unique fields
- numeric minimum/maximum ranges
- allowed-value lists
- full-match regular expressions
- valid-date checks with an optional explicit date format

Validation results show which rules pass or fail, how many values violate each rule, and the affected spreadsheet-style row numbers.

### Strict type conversion

Preview and explicitly convert columns to:

- text
- integer
- float
- boolean
- date
- datetime

Conversions are **strict by default**. If a non-empty value cannot be converted safely, RowSpect blocks that conversion rather than silently replacing the value, partially converting the column, or guessing.

### Portable rule profiles

Save validation rules and optional conversion plans as a small JSON profile and reuse them on the next file of the same kind. Profiles contain configuration only; they do not contain source dataset rows.

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

Open the local URL printed by Streamlit. You can enable the built-in synthetic sample before choosing your own file.

## CLI

Install the package:

```bash
pip install -e .
```

Profile a CSV:

```bash
rowspect sample_data/messy_customers.csv
```

Write generic machine-readable and standalone reports:

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

## Production hardening

RowSpect includes a repeatable qualification and deployment path rather than relying only on a developer machine:

- 50 MB upload limit enforced by Streamlit and RowSpect validation
- 250 MB maximum uncompressed XLSX size
- 10,000 XLSX archive-entry limit
- invalid, corrupt, encrypted, or implausibly expanded XLSX containers rejected before normal parsing
- duplicate CSV/XLSX headers preserved and surfaced as structural issues
- spreadsheet formula-like text neutralized on export by default
- self-contained HTML reports escape user-controlled values
- reusable rule profiles capped at 256 KB and validated before use
- strict conversion plans never mutate the original upload
- non-root Docker image with an HTTP health check
- Streamlit XSRF/CORS protections left enabled
- `rowspect --doctor` runtime diagnostics
- automated release audit, wheel build, CLI/profile smoke, and live Streamlit smoke

See [`SECURITY.md`](SECURITY.md) and [`docs/SAFETY_REVIEW.md`](docs/SAFETY_REVIEW.md) for the security model and known limits.

## Release qualification

RowSpect 1.2 completed its release checklist with:

- **82/82 automated tests passing** in the qualified environment
- strict `python scripts/qualify_release.py --require-ui` gate passing
- real CSV and XLSX browser uploads passing
- multi-sheet workbook switching passing
- all six custom rule types exercised
- all six conversion targets exercised
- unsafe conversion blocking verified
- cleanup controls tested independently and in combination
- malformed and oversized upload handling verified
- cleaned and converted CSV/XLSX outputs independently reopened with pandas/openpyxl
- public-release audit, wheel build, CLI smoke, and rule-profile smoke passing

A synthetic **100,000 × 20** profiling benchmark completed in **1.149 seconds** in the qualification environment. Benchmark results vary by hardware and dataset.

The release checklist and exact qualification notes are in [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md).

## Conservative cleaning

RowSpect can:

- remove exact duplicate rows
- trim leading/trailing whitespace
- convert blank text to missing values
- remove completely empty rows
- apply explicitly configured type conversions when every non-empty value is compatible

It deliberately does **not** impute missing values or guess how invalid values should be repaired.

Spreadsheet exports neutralize text beginning with common formula prefixes (`=`, `+`, `-`, `@`) by default. This can be disabled when exact literal preservation is more important.

## Privacy and security

Uploaded data is parsed inside the running Streamlit process. RowSpect contains no hosted backend or telemetry code. If you deploy Streamlit to another machine or network, that deployment becomes the place where the file is processed.

RowSpect is **not a malware sandbox**. File limits and workbook checks reduce common resource-exhaustion risks, but untrusted files should still be handled according to your organization’s security policy. User-supplied regex rules are also local configuration rather than a hardened regex sandbox.

See [`SECURITY.md`](SECURITY.md) for the full file-handling and export-safety notes.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

The suite covers CSV encodings/delimiters, Excel sheets and corruption, structural profiling, score output, cleanup, formula-safe exports, HTML escaping, chart helpers, CLI behavior, custom validation, strict conversions, reusable profiles, and release metadata.

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

## License

MIT. See [`LICENSE`](LICENSE).
