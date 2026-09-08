from __future__ import annotations

import argparse
import time

import numpy as np
import pandas as pd

from rowspect.profile import profile_dataframe


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a repeatable RowSpect profiling benchmark.")
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--numeric", type=int, default=12)
    parser.add_argument("--text", type=int, default=8)
    args = parser.parse_args()

    rng = np.random.default_rng(42)
    data: dict[str, object] = {
        f"numeric_{index}": rng.normal(size=args.rows) for index in range(args.numeric)
    }
    for index in range(args.text):
        data[f"text_{index}"] = rng.choice(["A", "B", "C", "D", None], size=args.rows)
    df = pd.DataFrame(data)

    start = time.perf_counter()
    profile = profile_dataframe(df)
    elapsed = time.perf_counter() - start
    print(
        f"RowSpect benchmark: {args.rows:,} rows x {df.shape[1]} columns in {elapsed:.3f}s | "
        f"score={profile['quality_score']} issues={profile['issue_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
