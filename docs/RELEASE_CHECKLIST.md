# Release checklist

A public RowSpect release should not be advertised until all required gates pass.

## Required

- [ ] `python scripts/qualify_release.py --require-ui` passes
- [ ] all automated tests pass
- [ ] package version, README, and changelog agree
- [ ] CLI sample profiling produces JSON and HTML outputs
- [ ] Streamlit server health smoke passes
- [ ] manual browser walkthrough passes using both the built-in sample and one XLSX workbook
- [ ] CSV and XLSX cleaned downloads open successfully in a spreadsheet application
- [ ] repository contains no private datasets, credentials, secrets, or machine-specific paths
- [ ] security and deployment docs match actual behavior

## Manual UI walkthrough

Check:

1. empty landing page and sample toggle
2. CSV upload
3. XLSX sheet selection
4. score and severity summary
5. Issues filters
6. Columns inspection
7. Explore charts
8. conservative cleanup switches
9. cleaned CSV download
10. cleaned XLSX download
11. HTML report download
12. JSON profile download
13. malformed/oversized file error handling

## Publish

Only after the gates above pass:

- make the repository public
- create/tag the release
- add screenshots or a short demo GIF to the README
- announce the project
