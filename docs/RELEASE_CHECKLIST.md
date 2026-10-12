# Release checklist

A versioned public release should not be advertised until its required gates pass. Source maintenance can be merged separately from package publication. This checklist applies to source version **1.3.0**; publication remains tracked in [issue #3](https://github.com/LUKEcheadle-ship-it/RowSpect/issues/3).

## October 12 maintenance — completed

The following evidence belongs to source `ef12c1f210e8b0720939da529365270e89aecb65`, merged through PR #14. Full receipts and exact workflow identifiers are in [LAUNCH.md](LAUNCH.md).

- [x] 121 local tests and strict release qualification passed
- [x] actual Chromium CSV/XLSX uploads, independent worksheet selection, nine tabs, comparisons, rules, blocked conversions, downloads and fresh-session profile reload passed
- [x] the browser receipt binds the exact clean source checkout
- [x] actual cleaned CSV and XLSX downloads opened in native Gnumeric 1.12.56
- [x] actual converted CSV and XLSX downloads opened in native Gnumeric 1.12.56
- [x] native imports preserve expected row counts and neutralized formula-like text; XLSX padded identifiers remain text
- [x] original synthetic inputs and downloaded files remain unchanged
- [x] source repairs merged into main

These are automated real-browser and desktop-application checks with inspected screenshots, not a claim of a human manual walkthrough of every option. Microsoft Excel specifically was not tested. CSV automatic import typing is application-controlled; use text import for padded identifiers or prefer XLSX.

## Historical candidate evidence

The entries below preserve the prior candidate record at `6018b7a5961c42040fc8c659311fc6479aa28f41`. They are not fresh results for later commits.

- [x] strict release qualification and all automated tests passed on the historical candidate
- [x] package version, README and changelog agreed on 1.3.0
- [x] CLI profiling, validation, comparison and deduplicated failing-row exports passed
- [x] CLI strict profile conversions and reusable-profile round-trip passed
- [x] Streamlit server health smoke and public-source audit passed
- [x] security and deployment documentation was reviewed

The historical environment lacked native spreadsheet verification. The separate October 12 desktop run above supplies that evidence for the maintenance source; it does not retroactively change the historical result.

## Required for a separately selected versioned release

No package or GitHub Release is created simply by completing this checklist's maintenance section. Record the intended release SHA and match its code/artifacts to the qualifying evidence. Existing checks need rerunning when affected by later source changes.

- [ ] exact formal-release revision, package version, license, README and changelog verified together
- [ ] strict qualification result is bound to that formal-release revision
- [ ] installation, sample workflow and documented Docker usage verified for the release distribution
- [ ] complete manual browser walkthrough recorded using the sample, CSV and XLSX, if claiming manual qualification
- [ ] cleaned and converted CSV/XLSX outputs bound to the release are covered by native application evidence
- [ ] final privacy, security and release evidence reviewed
- [ ] repository owner publication authorization recorded
- [ ] versioned GitHub Release published with accurate notes and matching artifacts

## Historical manual UI record

The prior sample walkthrough did not certify unchecked interactions. The October 12 automated browser results above are separate supporting evidence, not replacements for a human-manual claim.

- [x] empty landing page and sample toggle
- [ ] CSV upload
- [ ] XLSX sheet selection
- [x] score and severity summary
- [ ] Issues filters
- [ ] Columns inspection
- [ ] Explore charts
- [ ] add each validation rule type
- [x] required validation result and row-number reporting
- [ ] save and reload reusable profiles
- [ ] preview all conversion target types
- [ ] blocked conversion remains unapplied
- [ ] converted CSV/XLSX exports and cleanup working copy
- [ ] cleanup switches and cleaned CSV/XLSX downloads
- [ ] HTML, generic JSON and validation JSON downloads
- [x] malformed/oversized handling (automated historical gate)
- [ ] numeric column-header `0` displayed correctly in selectors
- [x] Compare empty-state guidance
- [ ] uploaded comparison baseline and JSON export
- [x] CSV identifier safety, cross-column modes/operators (automated historical checks)
- [x] original-data warning on failing-row export

## Presentation

The repository is already public and the real synthetic-data dashboard screenshot is already stored and referenced. Preserve accurate evidence by revision. A screenshot, source merge or passing CI run alone is not a formal publication record.
