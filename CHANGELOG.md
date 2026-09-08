# Changelog

## 1.0.0

RowSpect V1 is the first release candidate intended for public use.

### Added
- CSV and multi-sheet XLSX ingestion with a 50 MB V1 upload limit
- delimiter detection for comma, semicolon, tab, and pipe-delimited CSVs
- UTF-8/UTF-8-BOM/Latin-1 CSV handling
- deterministic 0–100 quality score with visible score deductions
- critical, warning, and informational issue severity
- missing, blank, duplicate-row, duplicate-column, all-missing, constant, numeric-text, and IQR-outlier checks
- interactive Streamlit exploration for missingness, distributions, top values, and correlations
- conservative cleanup with before/after summary
- cleaned CSV and XLSX exports
- optional formula-like text neutralization for safer spreadsheet exports
- standalone HTML and JSON analysis exports
- command-line profiling with `rowspect`
- expanded unit tests for parsing, profiling, cleanup, exports, reporting, insights, and CLI behavior

### Safety and privacy
- no RowSpect cloud backend, accounts, telemetry, or analytics SDK
- uploads are read into the local Streamlit process
- HTML output escapes user-controlled source names and report values
- spreadsheet export can neutralize formula-like text by default
