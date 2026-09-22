# Release checklist

A public RowSpect release should not be advertised until all required gates pass. This checklist applies to the **1.3.0** release candidate. Historical 1.2 qualification evidence is not reused as 1.3 evidence.

## Required

- [x] `python scripts/qualify_release.py --require-ui` passes on the final candidate
- [x] all automated tests pass on the final candidate
- [x] package version, README, and changelog agree
- [x] CLI generic profiling produces JSON and HTML outputs
- [x] CLI reusable-profile validation produces validation JSON
- [x] CLI comparison produces deterministic comparison JSON
- [x] CLI failing-row export is deduplicated and includes source row/reasons
- [x] CLI strict profile conversions are exercised, including Int64 and float safety
- [x] Streamlit server health smoke passes
- [ ] manual browser walkthrough passes using both the built-in sample and one XLSX workbook — automated UI smoke passed; full manual XLSX walkthrough remains to be done
- [ ] CSV and XLSX cleaned downloads open successfully in a spreadsheet application — blocker: no native spreadsheet application is installed or exposed for verification in this environment
- [ ] converted CSV and XLSX downloads open successfully in a spreadsheet application — blocker: no native spreadsheet application is installed or exposed for verification in this environment
- [x] reusable profile serialization can be reloaded and produces the same rules/conversions — explicit qualification gate plus unit coverage
- [x] repository contains no private datasets, credentials, secrets, or machine-specific paths
- [x] security and deployment docs match actual behavior

## Manual UI walkthrough

The built-in sample walkthrough was completed on the final candidate across Overview, Issues, Columns, Explore, Validate, Convert, Clean, Export, and Compare. The items below remain unchecked when they require an uploaded XLSX, a downloaded artifact, or a native spreadsheet application.

Check:

- [x] empty landing page and sample toggle
- [ ] CSV upload
- [ ] XLSX sheet selection
- [x] score and severity summary
- [ ] Issues filters
- [ ] Columns inspection
- [ ] Explore charts
- [ ] add required/unique/range/allowed-values/regex/date validation rules
- [x] required validation result and row-number reporting
- [ ] save reusable rule profile
- [ ] reload reusable rule profile
- [ ] preview safe integer/float/boolean/date/datetime/text conversions
- [ ] blocked conversion stays unapplied when an incompatible value exists
- [ ] safe conversion plan exports converted CSV and XLSX
- [ ] safe conversion plan can feed the cleanup working copy
- [ ] conservative cleanup switches
- [ ] cleaned CSV download
- [ ] cleaned XLSX download
- [ ] HTML report download
- [ ] generic JSON profile download
- [ ] custom validation JSON download
- [x] malformed/oversized file error handling (automated gate)
- [ ] numeric header `0` displays as `0` in Validate and Convert selectors
- [x] Compare tab empty state explains how to load a baseline
- [ ] Compare tab with an uploaded baseline and exported JSON
- [x] CSV identifier safety and Preserve CSV text behavior are verified (automated gate)
- [x] cross-column numeric/date/text modes and all operators are verified (automated tests)
- [x] failing-row CSV warning about original source data is visible

## Publish

Only after every required gate above passes:

- make the repository public
- create/tag the release
- add screenshots or a short demo GIF to the README
- announce the project

Record the exact final test count, qualification command, benchmark environment, and unavailable checks in `CHANGELOG.md` and `docs/LAUNCH.md`. Do not publish a GitHub Release from this repository until the final qualification evidence has been reviewed.
