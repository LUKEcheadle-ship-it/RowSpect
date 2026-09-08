from __future__ import annotations

import pandas as pd


def display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a display-only copy with labels Streamlit/Arrow can render safely.

    The analysis dataframe is intentionally left unchanged so duplicate and blank
    source headers remain visible to the profiler and exports. Only the copy used
    by the UI gets deterministic suffixes for ambiguous labels.
    """
    display = df.copy(deep=False)
    seen: set[str] = set()
    counts: dict[str, int] = {}
    labels: list[str] = []

    for position, column in enumerate(display.columns, start=1):
        base = str(column).strip() or f"Unnamed column {position}"
        counts[base] = counts.get(base, 0) + 1
        label = base if counts[base] == 1 else f"{base} [{counts[base]}]"
        while label in seen:
            counts[base] += 1
            label = f"{base} [{counts[base]}]"
        seen.add(label)
        labels.append(label)

    display.columns = labels
    return display
