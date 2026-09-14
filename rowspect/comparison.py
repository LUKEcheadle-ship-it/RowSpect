"""Explainable comparison of recurring deliveries; no statistical drift claim."""
from __future__ import annotations

import pandas as pd
from rowspect.profile import profile_dataframe


def compare_dataframes(baseline: pd.DataFrame, current: pd.DataFrame) -> dict:
    before, after = baseline.copy(), current.copy()
    before.columns = [str(name) for name in before.columns]
    after.columns = [str(name) for name in after.columns]
    if before.columns.duplicated().any() or after.columns.duplicated().any():
        raise ValueError("Rename duplicate column names before comparing files.")
    old_profile, new_profile = profile_dataframe(before), profile_dataframe(after)
    columns = []
    for name in after.columns:
        if name not in before:
            continue
        old, new = before[name], after[name]
        old_missing = float(old.isna().mean() * 100) if len(old) else None
        new_missing = float(new.isna().mean() * 100) if len(new) else None
        item = {"column": name, "baseline_dtype": str(old.dtype), "current_dtype": str(new.dtype),
                "type_changed": str(old.dtype) != str(new.dtype),
                "missing_pct_before": old_missing, "missing_pct_after": new_missing,
                "missing_percentage_point_change": round(new_missing-old_missing, 3) if old_missing is not None and new_missing is not None else None}
        numeric = all(pd.api.types.is_numeric_dtype(s.dtype) and not pd.api.types.is_bool_dtype(s.dtype) for s in (old, new))
        if numeric:
            for label, series in (("baseline", old), ("current", new)):
                finite = series.dropna()
                finite = finite[finite.map(lambda v: float('-inf') < v < float('inf'))]
                item[label + "_median"] = float(finite.median()) if len(finite) else None
            item["median_change"] = item["current_median"] - item["baseline_median"] if all(item[k] is not None for k in ("current_median", "baseline_median")) else None
        else:
            new_values = sorted(set(new.dropna().map(str)) - set(old.dropna().map(str)))
            item.update(new_categories=new_values[:20], new_category_count=len(new_values), categories_truncated=len(new_values)>20)
        columns.append(item)
    return {"baseline_rows": len(before), "current_rows": len(after), "row_change": len(after)-len(before),
            "added_columns": [c for c in after if c not in before], "removed_columns": [c for c in before if c not in after],
            "baseline_quality_score": old_profile["quality_score"], "current_quality_score": new_profile["quality_score"],
            "quality_score_change": new_profile["quality_score"]-old_profile["quality_score"], "columns": columns,
            "interpretation": "Descriptive changes for review, not statistical proof of drift or bad data."}
