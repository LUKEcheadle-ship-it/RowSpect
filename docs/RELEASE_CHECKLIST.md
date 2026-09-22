# Release checklist

A public RowSpect release should not be advertised until all required gates pass. This checklist applies to the **1.3.0** release candidate. Historical 1.2 qualification evidence is not reused as 1.3 evidence.

## Required

- [ ] `python scripts/qualify_release.py --require-ui` passes on the final candidate
- [ ] all automated tests pass on the final candidate
- [ ] package version, README, and changelog agree
- [x] CLI generic profiling produces JSON and HTML outputs
- [ ] CLI reusable-profile validation produces validation JSON
- [ ] CLI comparison produces deterministic comparison JSON
- [ ] CLI failing-row export is deduplicated and includes source row/reasons
- [ ] CLI strict profile conversions are exercised, including Int64 and float safety
- [ ] Streamlit server health smoke passes
- [x] manual browser walkthrough passes using both the built-in sample and one XLSX workbook
- [ ] CSV and XLSX cleaned downloads open successfully in a spreadsheet application — blocker: no native spreadsheet application is installed or exposed for verification in this environment
- [ ] converted CSV and XLSX downloads open successfully in a spreadsheet application — blocker: no native spreadsheet application is installed or exposed for verification in this environment
- [ ] reusable profile download can be reloaded and produces the same rules/conversions
- [x] repository contains no private datasets, credentials, secrets, or machine-specific paths
- [x] security and deployment docs match actual behavior

## Manual UI walkthrough

Check:

- [x] empty landing page and sample toggle
- [x] CSV upload
- [x] XLSX sheet selection
- [x] score and severity summary
- [x] Issues filters
- [x] Columns inspection
- [x] Explore charts
- [x] add required/unique/range/allowed-values/regex/date validation rules
- [x] validation result table and row-number reporting
- [x] save reusable rule profile
- [x] reload reusable rule profile
- [x] preview safe integer/float/boolean/date/datetime/text conversions
- [x] blocked conversion stays unapplied when an incompatible value exists
- [x] safe conversion plan exports converted CSV and XLSX
- [x] safe conversion plan can feed the cleanup working copy
- [x] conservative cleanup switches
- [x] cleaned CSV download
- [x] cleaned XLSX download
- [x] HTML report download
- [x] generic JSON profile download
- [x] custom validation JSON download
- [x] malformed/oversized file error handling
- [x] numeric header `0` displays as `0` in Validate and Convert selectors
- [ ] Compare tab explains baseline/current changes and exports JSON
- [ ] CSV identifier safety and Preserve CSV text behavior are verified
- [ ] cross-column numeric/date/text modes and all operators are verified
- [ ] failing-row CSV warning about original source data is visible

## Publish

Only after every required gate above passes:

- make the repository public
- create/tag the release
- add screenshots or a short demo GIF to the README
- announce the project

Record the exact final test count, qualification command, benchmark environment, and unavailable checks in `CHANGELOG.md` and `docs/LAUNCH.md`. Do not publish a GitHub Release from this repository until the final qualification evidence has been reviewed.
