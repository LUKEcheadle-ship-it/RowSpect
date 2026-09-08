# RowSpect 1.2 launch kit

This document keeps public launch messaging consistent with the product’s tested scope.

## One-line description

**Local-first CSV/XLSX data quality profiling, validation, safe cleanup, and reusable rule profiles.**

## Short product pitch

RowSpect is a local-first spreadsheet quality checker for CSV and Excel files. It finds structural and data-quality problems, lets you define reusable business rules, previews safe type conversions, performs conservative cleanup, and exports cleaned files plus HTML/JSON evidence — without requiring a RowSpect cloud upload service.

## Suggested GitHub description

`Local-first CSV/XLSX data quality profiling, validation, safe cleanup, and reusable rule profiles.`

## Suggested GitHub topics

- `data-quality`
- `data-cleaning`
- `data-validation`
- `data-profiling`
- `csv`
- `excel`
- `xlsx`
- `pandas`
- `streamlit`
- `python`
- `local-first`
- `privacy`

## Primary positioning

RowSpect should be marketed as:

> **A local spreadsheet quality checker for analysts and data practitioners who want fast, explainable CSV/XLSX validation without setting up a full data-quality platform.**

The strongest differentiators are:

1. **Spreadsheet-first** — CSV and Excel are the primary workflow, not an afterthought.
2. **Local-first** — no RowSpect cloud upload backend is required.
3. **Explainable** — deterministic checks and visible score deductions rather than opaque AI judgments.
4. **Reusable** — validation/conversion profiles turn one-off spreadsheet review into a repeatable process.
5. **Safe-by-default conversion** — incompatible values block a conversion instead of being silently coerced.
6. **UI + CLI** — useful interactively and scriptable for recurring checks.

## What not to claim

Do not market RowSpect as:

- an AI system that automatically fixes any spreadsheet
- a replacement for Great Expectations, Soda, or enterprise data-observability platforms
- a malware scanner or hostile-file sandbox
- an Internet-ready multi-tenant SaaS platform
- a guarantee that all values in a dataset are correct
- a replacement for domain-expert review of high-stakes data

## Launch post — LinkedIn

I just finished RowSpect 1.2, an open-source, local-first data quality tool for CSV and Excel files.

The idea is simple: before a spreadsheet reaches a dashboard, model, or report, RowSpect gives you a fast, explainable review of what may be wrong.

It can identify missing values, duplicates, suspicious types, constant columns, potential outliers, and structural problems. You can also define reusable business rules like “Customer ID must be unique,” “Revenue cannot be negative,” or “State must be one of these values.”

RowSpect 1.2 also adds strict type-conversion previews, reusable rule profiles, conservative cleanup, cleaned CSV/XLSX exports, HTML/JSON reports, and a CLI for repeatable checks.

The project is deliberately local-first: there is no RowSpect cloud upload backend, account system, telemetry, analytics SDK, or AI API required to analyze a file.

Release qualification covered 82 automated tests, real CSV/XLSX browser workflows, all validation and conversion types, malformed-file handling, export validation, and a public-release audit.

Repository: https://github.com/LUKEcheadle-ship-it/RowSpect

Feedback and contributions are welcome.

## Launch post — X / short social

RowSpect 1.2 is live: a local-first CSV/XLSX data quality checker.

Upload a spreadsheet → find issues → add reusable validation rules → preview safe type conversions → clean common problems → export the result.

No RowSpect cloud upload backend or AI API required.

https://github.com/LUKEcheadle-ship-it/RowSpect

## Launch post — Reddit / developer community

**I built RowSpect: a local-first CSV/XLSX data quality checker with reusable validation rules**

I wanted a lightweight way to inspect recurring spreadsheets without setting up a full data-quality stack or uploading the file to a hosted service.

RowSpect 1.2 supports:

- CSV and multi-sheet XLSX
- missing/blank/duplicate/constant/outlier review signals
- explainable 0–100 generic quality score
- required, unique, range, allowed-value, regex, and date rules
- reusable JSON rule/conversion profiles
- strict type-conversion previews
- conservative cleanup
- cleaned CSV/XLSX plus HTML/JSON reports
- Streamlit UI and CLI

The project is local-first and deterministic. It deliberately does not impute missing values or guess how invalid values should be repaired.

The 1.2 release qualification passed 82 automated tests plus real browser upload, validation, conversion, cleanup, malformed-file, and export workflows.

Repo: https://github.com/LUKEcheadle-ship-it/RowSpect

I’d be interested in feedback on useful spreadsheet-quality checks that would fit the same small/local scope.

## Release notes — v1.2.0

### RowSpect 1.2.0

RowSpect 1.2 turns the original spreadsheet profiler into a reusable validation workflow.

#### Added

- custom required, unique, range, allowed-value, regex, and date rules
- exact validation violation counts and spreadsheet-style row numbers
- strict text/integer/float/boolean/date/datetime conversion previews
- safe converted CSV/XLSX exports
- reusable JSON validation/conversion profiles
- profile upload/download in Streamlit
- CLI profile validation and `--fail-on-validation`
- explicit `--apply-profile-conversions` opt-in for stored conversions
- 1.2-specific release qualification coverage

#### Safety behavior

- validation rules never modify the source dataset
- conversions are strict and opt-in by default
- incompatible non-empty values block conversion
- original uploads remain unchanged
- formula-like spreadsheet text is neutralized on export by default
- rule profiles contain configuration rather than source dataset rows

#### Qualification

- 82/82 automated tests passing in the qualified environment
- strict release qualification PASS
- real CSV/XLSX upload and multi-sheet switching PASS
- all six validation rule types PASS
- all six conversion targets PASS
- unsafe conversion blocking PASS
- profile round trip PASS
- cleanup controls PASS
- malformed/oversized upload handling PASS
- cleaned/converted outputs independently reopened with pandas/openpyxl
- public-release audit, wheel build, CLI/profile smoke PASS
- 100,000 × 20 synthetic profiling benchmark: 1.149 seconds in the qualification environment

See `SECURITY.md` and `docs/SAFETY_REVIEW.md` for scope and known limitations.

## First-week marketing checklist

- make the repository public
- use the suggested GitHub description and topics above
- create the `v1.2.0` GitHub Release using the release notes above
- add 2–3 real screenshots from the qualified Streamlit UI
- pin RowSpect on the GitHub profile if it represents the work you want interviewers to see first
- publish the LinkedIn post
- optionally publish the shorter X post and a technically framed developer-community post
- answer early issues quickly and convert repeated questions into README/docs improvements

## Screenshot guidance

Use only real RowSpect UI screenshots with the built-in synthetic dataset or another synthetic dataset. Useful shots:

1. Overview showing quality score, metrics, and missingness.
2. Validate tab showing reusable rules and violation results.
3. Convert or Clean tab showing strict conversion/cleanup behavior.

Do not use generated mock screenshots as if they were real product evidence.
