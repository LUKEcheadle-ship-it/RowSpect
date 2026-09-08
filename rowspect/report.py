from __future__ import annotations

from html import escape
from typing import Any


def _cell(value: Any) -> str:
    return "—" if value is None else escape(str(value))


def build_html_report(profile: dict[str, Any], source_name: str = "dataset") -> str:
    """Generate a self-contained HTML profile report with no external assets."""
    issue_rows = "".join(
        "<tr>"
        f"<td>{_cell(issue['severity']).title()}</td>"
        f"<td>{_cell(issue['category'])}</td>"
        f"<td>{_cell(issue.get('column'))}</td>"
        f"<td>{_cell(issue.get('count'))}</td>"
        f"<td>{_cell(issue['message'])}</td>"
        "</tr>"
        for issue in profile["issues"]
    ) or '<tr><td colspan="5">No data-quality issues detected.</td></tr>'

    column_rows = "".join(
        "<tr>"
        f"<td>{_cell(column['column'])}</td>"
        f"<td>{_cell(column['dtype'])}</td>"
        f"<td>{_cell(column['missing_pct'])}%</td>"
        f"<td>{_cell(column['unique_count'])}</td>"
        f"<td>{_cell(column['outlier_count'])}</td>"
        "</tr>"
        for column in profile["columns"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RowSpect report — {escape(source_name)}</title>
<style>
body {{ font-family: Inter, ui-sans-serif, system-ui, sans-serif; margin: 0; background: #f6f8fa; color: #1f2328; }}
main {{ max-width: 1100px; margin: 0 auto; padding: 40px 24px 64px; }}
h1 {{ margin-bottom: 4px; }}
.subtle {{ color: #636c76; margin-top: 0; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(160px,1fr)); gap: 12px; margin: 24px 0; }}
.card {{ background: white; border: 1px solid #d0d7de; border-radius: 10px; padding: 18px; }}
.metric {{ font-size: 28px; font-weight: 700; }}
table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #d0d7de; margin-bottom: 28px; }}
th, td {{ text-align: left; border-bottom: 1px solid #d8dee4; padding: 10px 12px; vertical-align: top; }}
th {{ background: #f6f8fa; }}
h2 {{ margin-top: 34px; }}
footer {{ color: #636c76; font-size: 14px; margin-top: 32px; }}
</style>
</head>
<body>
<main>
<h1>RowSpect data quality report</h1>
<p class="subtle">Source: {escape(source_name)}</p>
<section class="grid">
  <div class="card"><div class="metric">{profile['quality_score']}</div><div>Quality score / 100</div></div>
  <div class="card"><div class="metric">{profile['rows']}</div><div>Rows</div></div>
  <div class="card"><div class="metric">{profile['columns_count']}</div><div>Columns</div></div>
  <div class="card"><div class="metric">{profile['missing_pct']}%</div><div>Missing cells</div></div>
  <div class="card"><div class="metric">{profile['duplicate_rows']}</div><div>Duplicate rows</div></div>
</section>
<h2>Issues</h2>
<table><thead><tr><th>Severity</th><th>Category</th><th>Column</th><th>Count</th><th>Details</th></tr></thead><tbody>{issue_rows}</tbody></table>
<h2>Column profile</h2>
<table><thead><tr><th>Column</th><th>Type</th><th>Missing</th><th>Unique</th><th>IQR outliers</th></tr></thead><tbody>{column_rows}</tbody></table>
<footer>Generated locally by RowSpect. No upload or cloud service is required.</footer>
</main>
</body>
</html>"""
