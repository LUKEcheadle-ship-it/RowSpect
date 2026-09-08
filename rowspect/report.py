from __future__ import annotations

from html import escape
from typing import Any


def _cell(value: Any) -> str:
    return "—" if value is None else escape(str(value))


def build_html_report(profile: dict[str, Any], source_name: str = "dataset") -> str:
    """Generate a self-contained HTML profile report with no external assets."""
    issue_rows = "".join(
        "<tr>"
        f"<td><span class='sev {escape(issue['severity'])}'>{_cell(issue['severity']).title()}</span></td>"
        f"<td>{_cell(issue['category'])}</td>"
        f"<td>{_cell(issue.get('column'))}</td>"
        f"<td>{_cell(issue.get('count'))}</td>"
        f"<td>{_cell(issue['message'])}</td>"
        "</tr>"
        for issue in profile["issues"]
    ) or '<tr><td colspan="5">No data-quality issues detected by the current checks.</td></tr>'

    column_rows = "".join(
        "<tr>"
        f"<td>{_cell(column['column'])}</td>"
        f"<td>{_cell(column['dtype'])}</td>"
        f"<td>{_cell(column['missing_pct'])}%</td>"
        f"<td>{_cell(column['blank_count'])}</td>"
        f"<td>{_cell(column['unique_count'])}</td>"
        f"<td>{_cell(column['outlier_count'])}</td>"
        "</tr>"
        for column in profile["columns"]
    )

    components = profile.get("score_components", {})
    component_rows = "".join(
        f"<tr><td>{escape(name.replace('_', ' ').title())}</td><td>{_cell(value)}</td></tr>"
        for name, value in components.items()
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RowSpect report — {escape(source_name)}</title>
<style>
:root {{ color-scheme: light; }}
body {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif; margin: 0; background: #f6f8fa; color: #1f2328; }}
main {{ max-width: 1120px; margin: 0 auto; padding: 42px 24px 72px; }}
h1 {{ margin: 0 0 6px; letter-spacing: -0.02em; }}
.subtle {{ color: #636c76; margin-top: 0; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(150px,1fr)); gap: 12px; margin: 24px 0; }}
.card {{ background: white; border: 1px solid #d0d7de; border-radius: 12px; padding: 18px; box-shadow: 0 1px 2px rgba(31,35,40,.04); }}
.metric {{ font-size: 29px; font-weight: 750; }}
table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #d0d7de; margin-bottom: 28px; border-radius: 10px; overflow: hidden; }}
th, td {{ text-align: left; border-bottom: 1px solid #d8dee4; padding: 10px 12px; vertical-align: top; }}
th {{ background: #f6f8fa; }}
h2 {{ margin-top: 36px; }}
.sev {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
.sev.critical {{ background: #ffebe9; color: #cf222e; }}
.sev.warning {{ background: #fff8c5; color: #7d4e00; }}
.sev.info {{ background: #ddf4ff; color: #0969da; }}
footer {{ color: #636c76; font-size: 14px; margin-top: 32px; }}
</style>
</head>
<body>
<main>
<h1>RowSpect data quality report</h1>
<p class="subtle">Source: {escape(source_name)} · Local deterministic analysis</p>
<section class="grid">
  <div class="card"><div class="metric">{profile['quality_score']}</div><div>{_cell(profile.get('quality_label'))} · score / 100</div></div>
  <div class="card"><div class="metric">{profile['rows']}</div><div>Rows</div></div>
  <div class="card"><div class="metric">{profile['columns_count']}</div><div>Columns</div></div>
  <div class="card"><div class="metric">{profile['missing_pct']}%</div><div>Missing cells</div></div>
  <div class="card"><div class="metric">{profile['duplicate_rows']}</div><div>Duplicate rows</div></div>
  <div class="card"><div class="metric">{profile['issue_count']}</div><div>Review signals</div></div>
</section>
<h2>Issues</h2>
<table><thead><tr><th>Severity</th><th>Category</th><th>Column</th><th>Count</th><th>Details</th></tr></thead><tbody>{issue_rows}</tbody></table>
<h2>Column profile</h2>
<table><thead><tr><th>Column</th><th>Type</th><th>Missing</th><th>Blanks</th><th>Unique</th><th>IQR outliers</th></tr></thead><tbody>{column_rows}</tbody></table>
<h2>Score deductions</h2>
<table><thead><tr><th>Component</th><th>Penalty</th></tr></thead><tbody>{component_rows}</tbody></table>
<footer>Generated locally by RowSpect. The score is a review aid, not a guarantee that data is correct.</footer>
</main>
</body>
</html>"""
