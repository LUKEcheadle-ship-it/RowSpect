# Security

RowSpect is a local data-quality utility, not a sandbox for hostile files.

## Supported files

V1 accepts `.csv` and `.xlsx` files up to 50 MB. Files are parsed by pandas/openpyxl in the running Python process. Do not open untrusted files with RowSpect on a machine where parsing third-party documents is prohibited by policy.

## Privacy model

RowSpect has no project-operated upload service, account system, telemetry integration, or analytics SDK. The Streamlit app processes the selected file in the process where the app is running. If you expose Streamlit on a network interface, that deployment's access controls become your responsibility.

## Workbook resource limits

In addition to the 50 MB upload limit, RowSpect inspects the XLSX ZIP container before normal workbook parsing. V1.1 rejects workbooks that expand beyond 250 MB, contain more than 10,000 archive entries, are encrypted, or do not contain the core XLSX workbook structures. These checks reduce resource-exhaustion risk but do not make RowSpect a malware sandbox.

## Runtime network boundary

The RowSpect application and `rowspect` package do not require a network client to profile files. The release audit checks the runtime source for common outbound-network client imports. Deployment tooling may make loopback HTTP requests only for health/smoke verification.

## Spreadsheet formula safety

Downloaded CSV/XLSX files neutralize text beginning with common spreadsheet formula prefixes (`=`, `+`, `-`, `@`) by default. Users may explicitly disable this when exact text preservation is required.

## Reporting a vulnerability

Please open a GitHub issue for non-sensitive security bugs. Do not attach private datasets, credentials, customer data, or confidential workbooks. For a report that would expose sensitive exploit details, use GitHub's private vulnerability reporting feature if it is enabled for the repository.
