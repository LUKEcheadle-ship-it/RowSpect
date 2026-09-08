# Security

RowSpect is a local data-quality utility, not a sandbox for hostile files.

## Supported files

V1 accepts `.csv` and `.xlsx` files up to 50 MB. Files are parsed by pandas/openpyxl in the running Python process. Do not open untrusted files with RowSpect on a machine where parsing third-party documents is prohibited by policy.

## Privacy model

RowSpect has no project-operated upload service, account system, telemetry integration, or analytics SDK. The Streamlit app processes the selected file in the process where the app is running. If you expose Streamlit on a network interface, that deployment's access controls become your responsibility.

## Spreadsheet formula safety

Downloaded CSV/XLSX files neutralize text beginning with common spreadsheet formula prefixes (`=`, `+`, `-`, `@`) by default. Users may explicitly disable this when exact text preservation is required.

## Reporting a vulnerability

Please open a GitHub issue for non-sensitive security bugs. Do not attach private datasets, credentials, customer data, or confidential workbooks. For a report that would expose sensitive exploit details, use GitHub's private vulnerability reporting feature if it is enabled for the repository.
