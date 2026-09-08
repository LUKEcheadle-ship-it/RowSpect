# Release checklist

A public RowSpect release should not be advertised until all required gates pass. This checklist applies to the **1.2.0** validation/conversion release candidate and must be requalified independently of 1.1.

## Required

- [ ] `python scripts/qualify_release.py --require-ui` passes
- [ ] all automated tests pass
- [ ] package version, README, and changelog agree
- [ ] CLI generic profiling produces JSON and HTML outputs
- [ ] CLI reusable-profile validation produces validation JSON
- [ ] CLI strict profile conversions are exercised
- [ ] Streamlit server health smoke passes
- [ ] manual browser walkthrough passes using both the built-in sample and one XLSX workbook
- [ ] CSV and XLSX cleaned downloads open successfully in a spreadsheet application
- [ ] converted CSV and XLSX downloads open successfully in a spreadsheet application
- [ ] reusable profile download can be reloaded and produces the same rules/conversions
- [ ] repository contains no private datasets, credentials, secrets, or machine-specific paths
- [ ] security and deployment docs match actual behavior

## Manual UI walkthrough

Check:

- [ ] empty landing page and sample toggle
- [ ] CSV upload
- [ ] XLSX sheet selection
- [ ] score and severity summary
- [ ] Issues filters
- [ ] Columns inspection
- [ ] Explore charts
- [ ] add required/unique/range/allowed-values/regex/date validation rules
- [ ] validation result table and row-number reporting
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
- [ ] malformed/oversized file error handling

## Publish

Only after the gates above pass:

- make the repository public
- create/tag the release
- add screenshots or a short demo GIF to the README
- announce the project
