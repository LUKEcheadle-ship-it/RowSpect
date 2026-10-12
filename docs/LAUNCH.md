# RowSpect 1.3 launch notes

Source availability and a maintenance merge are distinct from publishing a package or GitHub Release. Versioned publication remains tracked in [issue #3](https://github.com/LUKEcheadle-ship-it/RowSpect/issues/3).

## October 12 maintenance update — merged

[PR #14](https://github.com/LUKEcheadle-ship-it/RowSpect/pull/14) merged the tested source `ef12c1f210e8b0720939da529365270e89aecb65` as main commit `cad428d799e4cfae8059b8d881ae2e90728f9c13`.

The update fixes smoke-test process cleanup and independent baseline worksheet selection, including a worksheet named `0`. It adds real browser workflow qualification and separates historical evidence from current results.

- Complete local suite: 121 tests passed.
- Strict qualification: `python scripts/qualify_release.py --require-ui` passed, including compilation, source audit, package build, CLI/API workflows, CSV/XLSX reloads and real HTTP smoke.
- Exact-source Chromium run [38298170367](https://github.com/LUKEcheadle-ship-it/RowSpect/actions/runs/38298170367): nine tabs and six grouped upload/rules/comparison/conversion/cleanup/download/profile-reload workflows passed. The receipt records a clean source checkout. Synthetic input hashes remained unchanged.
- Native desktop run [38302346632](https://github.com/LUKEcheadle-ship-it/RowSpect/actions/runs/38302346632): all four actual browser exports, cleaned/converted CSV and XLSX, opened successfully in Gnumeric 1.12.56. Screenshots were inspected. Native import retained expected row counts and formula-like text as text; XLSX padded identifiers remained strings. The original downloaded files were unchanged.
- Native artifact 11771161900: SHA-256 `2beb5f5e3f5cc9e08a3d69f0d74a79ae885be012786d8a476da0edd29c5c4f49`.

This completes the reviewed maintenance work and the previously missing native-application compatibility check for those exports. It is automated real-application evidence, not a claim that a person manually checked every interaction. Microsoft Excel specifically was not tested. CSV has no type metadata: a spreadsheet application's automatic import can remove identifier padding; select text import for identifiers, or use XLSX.

No formal package/GitHub Release or user-PC deployment is implied. The checklist distinguishes these completed maintenance checks from requirements for a separately selected versioned release.

## Release themes

- descriptive current-file versus baseline comparison
- cross-column numeric, date, and text validation
- deduplicated failing-row CSV exports with source row numbers and reasons
- safer CSV inference for padded identifiers and literal `NA`/`NULL`
- strict integer and float conversion hardening
- formula-safe exports, output collision protection, and local-first file limits

## Historical qualification snapshot

The following results belong to the named historical candidate, not subsequent commits:

- Version: 1.3.0
- Branch: `release/rowspect-1.3-20260923`
- Source SHA: `6018b7a5961c42040fc8c659311fc6479aa28f41`
- Qualification command: `python scripts/qualify_release.py --require-ui`
- Pytest: 107 passed, 0 failed, 0 skipped
- Package: `rowspect-1.3.0-py3-none-any.whl` built successfully
- CLI/API/CSV/XLSX/multi-sheet/rules/comparison/conversion/failing-row/cleanup/report, reusable-profile round-trip, programmatic CSV/XLSX reload, HTTP smoke and public audit: passed
- Benchmark: 100,000 rows x 20 columns in 1.452 seconds on Windows Python 3.12.10, pandas 2.2.3, openpyxl 3.1.5 and Streamlit 1.63.0

That environment did not provide the full workbook browser/native-application checks. The later October 12 evidence above closes the specified maintenance gaps without changing that historical record. The earlier README's 93-test/1.923-second figures did not identify their exact candidate and must not be combined with these results. Timings are observations, not performance guarantees. RowSpect 1.2's 82/82 result remains historical only.

## Screenshots

The repository's [real dashboard screenshot](assets/rowspect-dashboard.png) was merged through [PR #13](https://github.com/LUKEcheadle-ship-it/RowSpect/pull/13) and remains in the README. The October 12 artifacts add real synthetic-data browser and native-application captures. Screenshots illustrate tested behavior; they do not independently certify every possible workflow.

## Versioned release boundary

Before a formal package release, select the exact release revision, rerun any checks affected by subsequent changes and review the remaining release checklist. Retain the owner publication decision and accurate matching artifact/version evidence. Do not replace historical results or mark unperformed manual checks as passed.
