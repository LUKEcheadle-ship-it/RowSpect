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

To be filled after the final candidate passes:

- Version:
- Branch and HEAD SHA:
- Qualification command:
- Pytest pass/fail/skip counts:
- Package build:
- CLI/API/CSV/XLSX/multi-sheet/rules/comparison/conversion/failing-row/cleanup/report checks:
- UI smoke:
- Public-release audit:
- Benchmark command, exact result, and environment:

The historical RowSpect 1.2 result of 82/82 tests remains historical evidence only. It is not a 1.3 result.

## Screenshots

No suitable real RowSpect screenshots were present in the repository during the release-candidate audit. Before public launch, capture these from the qualified Streamlit app using synthetic data only:

1. Overview with the quality score and issue summary.
2. Validate with visible rule failures and row numbers.
3. Compare with a baseline/current change summary.

Do not use mockups or fabricated screenshots as application evidence.

## Release boundary

Prepare but do not publish a GitHub Release until the final qualification evidence is reviewed and the repository owner explicitly authorizes publication.
