# RowSpect 1.3 launch notes

This file separates recorded candidate evidence from the checks still needed for a versioned public release. Publication is tracked in [issue #3](https://github.com/LUKEcheadle-ship-it/RowSpect/issues/3); source availability is not the same as publishing a package or GitHub Release.

## Release themes

- descriptive current-file versus baseline comparison
- cross-column numeric, date, and text validation
- deduplicated failing-row CSV exports with source row numbers and reasons
- safer CSV inference for padded identifiers and literal `NA`/`NULL`
- strict integer and float conversion hardening
- formula-safe exports, output collision protection, and existing local-first file limits

## Recorded qualification snapshot

The following results are retained from the named historical candidate. They are not a fresh execution or qualification of subsequent commits.

- Version: 1.3.0
- Branch: `release/rowspect-1.3-20260923`
- Qualification target SHA: `6018b7a5961c42040fc8c659311fc6479aa28f41`
- Qualification command: `python scripts/qualify_release.py --require-ui`
- Pytest: 107 passed, 0 failed, 0 skipped
- Package build: `rowspect-1.3.0-py3-none-any.whl` built successfully
- CLI/API/CSV/XLSX/multi-sheet/rules/comparison/conversion/failing-row/cleanup/report checks: passed
- reusable-profile serialize/reload round-trip: passed
- cleaned CSV/XLSX archive reload with pandas/openpyxl: passed
- UI smoke: passed on loopback
- Public-release audit: passed
- Benchmark: `RowSpect benchmark: 100,000 rows x 20 columns in 1.452s` on Windows Python 3.12.10 with pandas 2.2.3, openpyxl 3.1.5, and Streamlit 1.63.0

The benchmark is an observed run, not a performance guarantee. The changelog records the same snapshot. Earlier README figures of 93 tests and 1.923 seconds did not identify their exact candidate there; they must not be combined with this snapshot or presented as current qualification.

The remaining checks are explicitly listed in [the release checklist](RELEASE_CHECKLIST.md): a manual XLSX browser walkthrough and opening generated workbooks in a native spreadsheet application were unavailable in the qualification environment. Programmatic pandas/openpyxl reloads and an HTTP server smoke do not substitute for those checks.

The historical RowSpect 1.2 result of 82/82 tests remains historical evidence only. It is not a 1.3 result.

## Screenshots

The repository already contains a [real dashboard screenshot](assets/rowspect-dashboard.png), referenced from the README and merged through [PR #13](https://github.com/LUKEcheadle-ship-it/RowSpect/pull/13). Do not recreate or replace it with a mockup.

Additional real-app captures using synthetic data can document Validate rule failures and Compare changes. These would supplement the existing screenshot; their absence does not mean the existing screenshot is missing. A screenshot is presentation evidence, not proof that every manual workbook check passed.

## Release boundary

Before publication, select the exact release commit, run `python scripts/qualify_release.py --require-ui`, record its results and environment separately from the historical snapshot, and complete the outstanding manual checks. The CI release job also uses `--require-ui`, which refuses to skip the smoke check when Streamlit is unavailable.

Prepare but do not publish a GitHub Release until the final qualification evidence is reviewed and the repository owner explicitly authorizes publication.
