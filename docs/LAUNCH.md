# RowSpect 1.3 launch notes

This file is the release-note template for the final 1.3 candidate. It must contain only evidence from the exact candidate that passed qualification.

## Release themes

- descriptive current-file versus baseline comparison
- cross-column numeric, date, and text validation
- deduplicated failing-row CSV exports with source row numbers and reasons
- safer CSV inference for padded identifiers and literal `NA`/`NULL`
- strict integer and float conversion hardening
- formula-safe exports, output collision protection, and existing local-first file limits

## Qualification evidence

- Version: 1.3.0
- Branch: `feature/v1.2-validation-conversion-profiles`
- Qualification target SHA: `5b9fc06`
- Qualification command: `python scripts/qualify_release.py --require-ui`
- Pytest: 93 passed, 0 failed, 0 skipped
- Package build: `rowspect-1.3.0-py3-none-any.whl` built successfully
- CLI/API/CSV/XLSX/multi-sheet/rules/comparison/conversion/failing-row/cleanup/report checks: passed
- reusable-profile serialize/reload round-trip: passed
- cleaned CSV/XLSX archive reload with pandas/openpyxl: passed
- UI smoke: passed on loopback
- Public-release audit: passed
- Benchmark: `RowSpect benchmark: 100,000 rows x 20 columns in 1.923s` on Windows Python 3.12.10 with pandas 2.2.3, openpyxl 3.1.5, and Streamlit 1.63.0

The historical RowSpect 1.2 result of 82/82 tests remains historical evidence only. It is not a 1.3 result.

## Screenshots

No screenshot files are stored in the repository yet. The qualified app was inspected with synthetic data during this pass; before public launch, save these real-app captures under `docs/assets/` and reference them from the README:

1. Overview with the quality score and issue summary.
2. Validate with visible rule failures and row numbers.
3. Compare with a baseline/current change summary.

Do not use mockups or fabricated screenshots as application evidence.

## Release boundary

Prepare but do not publish a GitHub Release until the final qualification evidence is reviewed and the repository owner explicitly authorizes publication.
