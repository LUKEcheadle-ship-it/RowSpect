# RowSpect 1.2 safety review

Review date: 2026-09-08

This review summarizes the security posture of the RowSpect 1.2 public release candidate. It is a product-scope review, not a claim of formal penetration testing or a security certification.

## Intended trust boundary

RowSpect is a **local data-quality utility** for CSV and XLSX files. Its intended deployment is a local workstation or a controlled Docker/Streamlit environment.

It is not designed to be:

- a malware sandbox
- an Internet-facing multi-tenant SaaS service
- a tenant-isolation boundary
- a substitute for endpoint security controls
- a guarantee that a dataset is factually correct

## Verified protections

### Local processing and privacy

- The runtime contains no RowSpect cloud upload backend.
- No account system, telemetry SDK, analytics SDK, or AI API is required for normal profiling.
- The public-release audit checks runtime code for common outbound-network client imports.
- Rule profiles store configuration metadata, not source dataset rows.

### Upload and workbook limits

- CSV/XLSX uploads are limited to 50 MB.
- XLSX containers are inspected before normal workbook parsing.
- XLSX expansion is capped at 250 MB uncompressed.
- XLSX containers are limited to 10,000 archive entries.
- Encrypted, corrupt, and structurally invalid XLSX files are rejected with user-facing errors.
- XLSX contents are read from memory rather than extracted to filesystem paths.

### Spreadsheet export safety

- Formula-like text beginning with `=`, `+`, `-`, or `@` is neutralized by default for CSV/XLSX export.
- Export safety operates on a copy and does not mutate the source dataframe.
- Generated HTML reports escape user-controlled source names, issue text, and profile values.

### Conversion safety

- Type conversions are explicit and opt-in.
- Strict mode blocks a conversion if any non-empty value is incompatible.
- Stored profile conversions are not applied by the CLI unless `--apply-profile-conversions` is supplied.
- The original uploaded dataframe remains unchanged; conversion occurs on a working copy.
- Arbitrary numeric columns are not silently treated as Unix-epoch dates.

### Reusable-profile safety

- Profiles are JSON data, not executable code.
- Profile size is capped at 256 KB.
- Unsupported profile versions are rejected.
- Rule IDs and conversion IDs must be unique.
- At most 100 validation rules and 100 conversions are accepted per profile.
- Regex patterns are length-limited and validated before use.

### Release controls

The 1.2 qualification evidence includes:

- 82/82 automated tests passing in the qualified environment
- strict Streamlit release qualification passing
- real CSV and multi-sheet XLSX browser uploads
- malformed and oversized upload error handling
- all six validation rule types
- all six conversion targets
- blocked unsafe conversions
- UI reusable-profile round trip
- individual and combined cleanup controls
- independent pandas/openpyxl reads of cleaned and converted CSV/XLSX outputs
- public-release audit, wheel build, CLI smoke, and reusable-profile CLI smoke

See `docs/RELEASE_CHECKLIST.md` for the exact release evidence.

## Residual risks and accepted limitations

### Untrusted document parsing

RowSpect relies on pandas/openpyxl for CSV/XLSX parsing. Resource limits reduce obvious workbook-expansion abuse, but RowSpect is not a hardened document sandbox. Do not use it as the sole security boundary for hostile files.

### User-supplied regular expressions

Regex validation is local user configuration. Pattern length is limited and syntax is validated, but the Python regex engine is not treated as a hardened untrusted-regex sandbox. A pathological regex can consume excessive CPU on adversarial input. Do not import untrusted rule profiles when regex denial-of-service is a concern.

### Network deployment

The local privacy model does not automatically make a Streamlit deployment safe for the public Internet. Internet-facing deployment would require additional controls such as authentication, TLS termination, reverse-proxy hardening, user isolation, rate limiting, logging policy, and a dedicated security review.

### Domain correctness

A high RowSpect score does not prove that business values are correct. Generic profiling finds structural and statistical review signals. Business correctness must be expressed through validation rules or verified by a knowledgeable reviewer.

### Native spreadsheet application check

The qualified environment did not provide Microsoft Excel or LibreOffice Calc. Generated cleaned and converted CSV/XLSX outputs were independently reopened and validated with pandas/openpyxl instead. Native opening is retained as an optional additional sanity check, not a blocking release gate.

## Release assessment

Within its documented scope — local or controlled CSV/XLSX profiling, validation, conservative cleanup, conversion, and export — no known issue identified during the 1.2 qualification blocks public release.

The largest remaining security caveat is deliberate and documented: **RowSpect should not be presented as a hostile-file sandbox or public multi-tenant service.**
