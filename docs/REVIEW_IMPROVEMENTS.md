# Review improvements: historical implementation record

This document records the post-1.2 review that led to the RowSpect 1.3 release candidate. It is not a qualification report and does not replace the exact evidence in `docs/LAUNCH.md`.

| Feature | Implementation | UI | CLI | Tests | Docs | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline comparison | `rowspect.comparison` | Compare tab | `--baseline`, `--comparison-json` | comparison regression tests | README, launch notes | candidate feature |
| Cross-column validation | `compare_columns` with six operators and three modes | rule editor | reusable profiles | boundary/configuration tests | rule profile docs | candidate feature |
| Failing-row export | deduplicated source rows with audit columns | validation download | `--failing-rows` | deduplication/CLI tests | README, SECURITY | candidate feature |
| CSV inference | canonical numeric inference, literal code preservation | Preserve CSV text option | `--preserve-text` | identifier/code regressions | README, rule docs | candidate feature |
| Conversion hardening | Decimal parsing, signed Int64 bounds, finite/loss-aware floats | existing conversion preview | profile conversion path | overflow/fraction/precision tests | SECURITY, rule docs | candidate feature |
| Export safety | formula-like headers and cells neutralized; output collisions rejected | existing download path | all CLI exports | formula/collision tests | SECURITY | candidate feature |

The generic quality score remains descriptive. RowSpect does not prove that a dataset is correct, perform statistical significance testing, or act as a malware sandbox.
