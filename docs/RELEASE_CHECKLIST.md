# Release checklist

A public RowSpect release should not be advertised until all required gates pass.

## Required

- [x] `python scripts/qualify_release.py --require-ui` passes
- [x] all automated tests pass
- [x] package version, README, and changelog agree
- [x] CLI sample profiling produces JSON and HTML outputs
- [x] Streamlit server health smoke passes
- [x] manual browser walkthrough passes using both the built-in sample and one XLSX workbook
- [x] CSV and XLSX cleaned downloads open successfully in a spreadsheet application
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
- [x] conservative cleanup switches
- [x] cleaned CSV download
- [x] cleaned XLSX download
- [x] HTML report download
- [x] JSON profile download
- [x] malformed/oversized file error handling

## Publish

Only after the gates above pass:

- make the repository public
- create/tag the release
- add screenshots or a short demo GIF to the README
- announce the project
