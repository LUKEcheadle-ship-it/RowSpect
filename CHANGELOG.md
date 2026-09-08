# Changelog

## 1.1.0

Production-hardening release candidate.

### Added
- non-root Docker deployment with a Streamlit health check
- Streamlit runtime safety configuration and 50 MB server upload limit
- `rowspect --doctor` runtime diagnostics without host-identifying data
- repeatable release qualification, live UI smoke, benchmark, and public-release audit scripts
- deployment and release-checklist documentation
- exact runtime dependency pins for the application deployment path
- XLSX archive expansion and archive-entry safety limits
- preservation of original CSV/XLSX headers so duplicate column names are detected in real uploaded files

### Hardened
- malformed CSV quote handling now fails with a clean user-facing error
- invalid/encrypted/implausibly expanded XLSX containers fail before normal workbook parsing
- package wheel build is part of the release qualification gate
- public-release audit checks runtime code for unexpected network clients, common secret formats, machine-specific paths, and non-sample datasets

### Qualification
- 60 automated tests passing in the qualification environment
- package wheel build passing
- CLI/report smoke passing
- public-release audit passing
- 100,000-row x 20-column synthetic benchmark completed in 1.670 seconds in the qualification environment
- strict live Streamlit UI qualification passing on loopback
- Docker qualification remains environment-dependent and was unavailable on the qualification host

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
