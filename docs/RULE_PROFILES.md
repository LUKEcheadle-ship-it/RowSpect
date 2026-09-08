# Reusable rule profiles

RowSpect 1.2 profiles are small UTF-8 JSON files that describe business-specific validation rules and optional explicit type-conversion plans. They contain configuration only; RowSpect does not write source dataset rows into a profile.

## Profile shape

```json
{
  "version": 1,
  "name": "Customer import checks",
  "description": "Checks used for the monthly customer export.",
  "rules": [],
  "conversions": []
}
```

See [`sample_data/customer_rules.json`](../sample_data/customer_rules.json) for a complete synthetic example.

## Validation rules

Every rule requires:

- `type`
- `column`
- optional `id`
- optional `severity`: `critical`, `warning`, or `info`
- optional custom `message`

Supported rule types:

### Required

```json
{"type": "required", "column": "email"}
```

Fails for null values and blank/whitespace-only text.

### Unique

```json
{"type": "unique", "column": "customer_id"}
```

Flags every non-empty occurrence of a duplicated value.

### Range

```json
{"type": "range", "column": "age", "min": 18, "max": 100}
```

`min`, `max`, or both may be supplied. Non-empty values that cannot be interpreted numerically fail the rule.

### Allowed values

```json
{"type": "allowed_values", "column": "region", "values": ["South", "East", "West"]}
```

Missing values are ignored unless a separate `required` rule is also present.

### Regex

```json
{
  "type": "regex",
  "column": "email",
  "pattern": "[^@\\s]+@[^@\\s]+\\.[^@\\s]+"
}
```

Patterns use Python regular-expression full-match semantics. Profiles from untrusted sources should not be treated as sandboxed code; see [`SECURITY.md`](../SECURITY.md).

### Date

```json
{"type": "date", "column": "signup_date", "format": "%Y-%m-%d"}
```

`format` is optional. When present, values must parse using that explicit format.

## Conversion plans

Conversion plans are never applied implicitly.

```json
{"column": "age", "target_type": "integer"}
```

Supported target types:

- `text`
- `integer`
- `float`
- `boolean`
- `date`
- `datetime`

The Streamlit UI previews compatibility before export. The CLI requires `--apply-profile-conversions` before stored plans are applied.

Strict conversion is the default: if any non-empty value cannot be converted, that conversion is blocked rather than silently replacing the value with missing data.

## CLI examples

Validate a dataset:

```bash
rowspect customers.csv --rules-profile customer-rules.json
```

Write validation results:

```bash
rowspect customers.csv \
  --rules-profile customer-rules.json \
  --validation-json validation.json
```

Make validation failure visible to scripts with exit code 1:

```bash
rowspect customers.csv \
  --rules-profile customer-rules.json \
  --fail-on-validation
```

Explicitly apply safe conversions before validation:

```bash
rowspect customers.csv \
  --rules-profile customer-rules.json \
  --apply-profile-conversions
```

## Column-name behavior

Profiles reference columns by exact header name. If a configured header is missing or appears more than once, RowSpect reports a configuration error rather than guessing which column was intended.
