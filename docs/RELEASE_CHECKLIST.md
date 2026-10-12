# Release checklist

A public RowSpect release should not be advertised until all required gates pass. This checklist applies to source version **1.3.0**. Historical evidence belongs to the exact commit that was checked, not every later commit. Publication remains tracked in [issue #3](https://github.com/LUKEcheadle-ship-it/RowSpect/issues/3).

## Recorded candidate evidence

The checked entries below preserve the prior candidate record described in [LAUNCH.md](LAUNCH.md), at `6018b7a5961c42040fc8c659311fc6479aa28f41`. They are not new test results for the current branch.

- [x] `python scripts/qualify_release.py --require-ui` passed on the recorded candidate
- [x] all automated tests passed on the recorded candidate
- [x] package version, README, and changelog agreed on version 1.3.0
- [x] CLI generic profiling produced JSON and HTML outputs
- [x] CLI reusable-profile validation produced validation JSON
- [x] CLI comparison produced deterministic comparison JSON
- [x] CLI failing-row export was deduplicated and included source row/reasons
- [x] CLI strict profile conversions were exercised, including Int64 and float safety
- [x] Streamlit server health smoke passed
- [x] reusable profile serialization reloaded with the same rules/conversions
- [x] public-release audit passed on the recorded candidate
- [x] security and deployment docs were reviewed against candidate behavior

## Required for the selected release commit

Record the selected SHA and evidence locations before checking these items. A missing result is still pending, not a pass or proof of an application defect.

- [ ] exact release commit, package version, license, README, and changelog verified
- [ ] `python scripts/qualify_release.py --require-ui` passes on that exact commit, with test count and environment recorded
- [ ] installation, sample workflow, and documented Docker usage verified
- [ ] manual browser walkthrough passes using the built-in sample, a CSV, and an XLSX workbook
- [ ] cleaned CSV and XLSX downloads open successfully in a native spreadsheet application
- [ ] converted CSV and XLSX downloads open successfully in a native spreadsheet application
- [ ] final privacy, security, and release evidence reviewed

The recorded environment did not provide a native spreadsheet application. Do not mark the workbook-opening checks complete based only on programmatic archive reloads or an HTTP smoke test.

## Manual UI walkthrough record

Earlier notes report a built-in-sample walkthrough. Preserve the specific checked items below; that broad description does not certify the unchecked interactions. Entries explicitly labeled automated are supporting automated evidence, not manual checks. Recheck the required workflows on the selected release commit and record the result.

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
- [x] CSV identifier safety and Preserve CSV text behavior (automated gate)
- [x] cross-column numeric/date/text modes and all operators (automated tests)
- [x] failing-row CSV warning about original source data is visible

## Presentation and publication

- [x] repository is public
- [x] real synthetic-data dashboard screenshot is stored at `docs/assets/rowspect-dashboard.png` and referenced from the README
- [ ] exact-candidate qualification and outstanding manual checks reviewed
- [ ] repository owner explicitly authorizes publication
- [ ] versioned `v1.3.0` GitHub Release published with accurate notes and matching artifacts

Record the exact final test count, qualification command, benchmark environment, and unavailable checks in `CHANGELOG.md` and `docs/LAUNCH.md` without replacing historical results with unexecuted claims. A merged source change, passing CI run, or screenshot does not by itself authorize publication.
