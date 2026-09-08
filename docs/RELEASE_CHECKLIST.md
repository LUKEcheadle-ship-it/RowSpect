# Release checklist

A public RowSpect release should not be advertised until all required gates pass. This checklist applies to the **1.2.0** validation/conversion release candidate and must be requalified independently of 1.1.

## Required

- [x] `python scripts/qualify_release.py --require-ui` passes
- [x] all automated tests pass
- [x] package version, README, and changelog agree
- [x] CLI generic profiling produces JSON and HTML outputs
- [x] CLI reusable-profile validation produces validation JSON
- [x] CLI strict profile conversions are exercised
- [x] Streamlit server health smoke passes
- [x] manual browser walkthrough passes using both the built-in sample and one XLSX workbook
- [ ] CSV and XLSX cleaned downloads open successfully in a spreadsheet application — blocker: no native spreadsheet application is installed or exposed for verification in this environment
- [ ] converted CSV and XLSX downloads open successfully in a spreadsheet application — blocker: no native spreadsheet application is installed or exposed for verification in this environment
- [x] reusable profile download can be reloaded and produces the same rules/conversions
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

## Publish

Only after the gates above pass:

- make the repository public
- create/tag the release
- add screenshots or a short demo GIF to the README
- announce the project
