# Security

RowSpect is a local data-quality utility, not a sandbox for hostile files.

For the public-release assessment and accepted residual risks, see [`docs/SAFETY_REVIEW.md`](docs/SAFETY_REVIEW.md).

## Supported files

RowSpect accepts `.csv` and `.xlsx` files up to 50 MB. Files are parsed by pandas/openpyxl in the running Python process. Do not open untrusted files with RowSpect on a machine where parsing third-party documents is prohibited by policy.

## Privacy model

RowSpect has no project-operated upload service, account system, telemetry integration, or analytics SDK. The Streamlit app processes the selected file in the process where the app is running. If you expose Streamlit on a network interface, that deployment's access controls become your responsibility.

Reusable 1.2 rule profiles contain configuration metadata only: profile name/description, column references, rule parameters, and optional conversion plans. They do not contain source dataset rows unless a user manually edits a profile file to add unrelated data.

## Workbook resource limits

In addition to the 50 MB upload limit, RowSpect inspects the XLSX ZIP container before normal workbook parsing. RowSpect rejects workbooks that expand beyond 250 MB, contain more than 10,000 archive entries, are encrypted, or do not contain the core XLSX workbook structures. These checks reduce resource-exhaustion risk but do not make RowSpect a malware sandbox.

## Runtime network boundary

The RowSpect application and `rowspect` package do not require a network client to profile files. The release audit checks the runtime source for common outbound-network client imports. Deployment tooling may make loopback HTTP requests only for health/smoke verification.

## Custom regex rules

Regular-expression rules are user-supplied local configuration. RowSpect limits regex pattern length, validates that patterns compile, and applies them only to the selected local column. This is not a hardened regex sandbox; do not load rule profiles from untrusted sources when hostile regular-expression denial-of-service is a concern.

## Type-conversion safety

Type conversions are explicit and strict by default. RowSpect previews compatibility first and blocks a conversion when any non-empty value is incompatible. The original upload is not modified; converted data exists only in a working copy or exported file. The CLI also requires an explicit `--apply-profile-conversions` flag before stored conversion plans are applied.

## Spreadsheet formula safety

Downloaded CSV/XLSX files neutralize text beginning with common spreadsheet formula prefixes (`=`, `+`, `-`, `@`) by default. Users may explicitly disable this when exact text preservation is required.

## Reporting a vulnerability

Please open a GitHub issue for non-sensitive security bugs. Do not attach private datasets, credentials, customer data, or confidential workbooks. For a report that would expose sensitive exploit details, use GitHub's private vulnerability reporting feature if it is enabled for the repository.
