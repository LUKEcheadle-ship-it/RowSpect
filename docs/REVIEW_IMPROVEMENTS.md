# Review improvements

These are development changes on top of the 1.2 baseline. Historical 1.2 qualification numbers in the README describe that baseline, not a new release.

CSV import infers numbers only when exact conversion is possible. Leading-zero IDs, padded text, mixed columns, and literal NA/NULL codes stay text. Empty cells are missing. Enable **Keep all CSV values as text** or `--preserve-text` to disable CSV inference. Excel's native text/number distinction is respected; number-format display padding is not reconstructed.

Strict integer conversion parses decimal values without a float intermediate, rejects fractions and values outside signed Int64, and reports incompatible values without casting exceptions. Float conversion rejects non-finite numbers and loss of significant decimal digits. An explicit integer conversion can remove leading-zero formatting; preserve those identifiers as text.

**Compare** accepts an earlier CSV/XLSX and reports added/removed columns, type changes, missingness percentage-point changes, new category examples, numeric medians, and row/quality changes. This is a descriptive comparison, not a statistical significance test. Exported comparisons may contain category values; review them before sharing.

```bash
rowspect current.csv --baseline previous.csv --comparison-json comparison.json
```

Cross-column rules can compare numeric, date, or text values using `eq`, `ne`, `lt`, `le`, `gt`, or `ge`. Numeric comparisons use exact decimals. Missing values are skipped; use required rules to reject them. Malformed non-empty values fail; missing/duplicate column references are configuration errors.

```json
{"name":"Orders", "rules":[
  {"id":"refund-limit", "type":"compare_columns", "column":"refund", "other_column":"total", "operator":"le", "comparison":"numeric"},
  {"id":"shipping-order", "type":"compare_columns", "column":"ship_date", "other_column":"order_date", "operator":"ge", "comparison":"date"}
]}
```

```bash
rowspect orders.csv --rules-profile orders-rules.json --failing-rows repairs.csv --fail-on-validation
```

The repair CSV includes every failing row once, the source row number, rule IDs, and reasons. It contains source data and must be handled accordingly. Source row numbers refer to the loaded table, with a header at row 1. Formula protection covers both data and headers. CLI exports refuse to overwrite input paths.
