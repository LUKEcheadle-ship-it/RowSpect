from __future__ import annotations

from typing import Any

import pandas as pd


def _display_value(value: Any) -> str | None:
    """Convert arbitrary cell values into Arrow-safe display text."""
    try:
        missing = pd.isna(value)
    except (TypeError, ValueError):
        missing = False
    if isinstance(missing, bool) and missing:
        return None
    return str(value)


def column_display_label(value: Any, position: int) -> str:
    """Return a stable, human-readable label for a source column."""
    text = str(value)
    return text.strip() or f"Unnamed column {position}"


def display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a display-only copy with labels Streamlit/Arrow can render safely.

    The analysis dataframe is intentionally left unchanged so duplicate and blank
    source headers remain visible to the profiler and exports. Only the copy used
    by the UI gets deterministic suffixes for ambiguous labels.
    """
    display = df.copy(deep=True)
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

    # Arrow requires a consistent type for each column. Profile/rule tables can
    # legitimately contain numeric, text, list, and dict values in one object
    # column, so stringify object-like values only in this display copy.
    for position in range(display.shape[1]):
        series = display.iloc[:, position]
        if not (
            pd.api.types.is_object_dtype(series.dtype)
            or pd.api.types.is_string_dtype(series.dtype)
            or isinstance(series.dtype, pd.CategoricalDtype)
        ):
            continue
        display.iloc[:, position] = series.map(_display_value)
    return display
