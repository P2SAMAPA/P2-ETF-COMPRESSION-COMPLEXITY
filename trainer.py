"""
Main training script for compression‑complexity analysis.
For each universe, compute compression ratios and rank ETFs.
"""

import pandas as pd
import json
from pathlib import Path
import config
import data_manager
from complexity_analyzer import ComplexityAnalyzer
import push_results

def main():
    if not config.HF_TOKEN:
        print("HF_TOKEN not set")
        return

    df = data_manager.load_master_data()
    all_results = {}

    for universe_name, tickers in config.UNIVERSES.items():
        print(f"\n=== Universe: {universe_name} ===")
        returns = data_manager.prepare_returns_matrix(df, tickers)
        if returns.empty:
            continue

        # Use full history by default (lookback=None) or apply config
        ca = ComplexityAnalyzer(compression_level=config.COMPRESSION_LEVEL,
                                lookback=config.LOOKBACK_WINDOW if config.LOOKBACK_WINDOW > 0 else None)
        rank_df = ca.rank_tickers(returns)
        rank_df = rank_df.sort_values("rank")  # rank 1 = most compressible

        # Prepare output
        top_picks = []
        for _, row in rank_df.head(config.TOP_N).iterrows():
            top_picks.append({
                "ticker": row["ticker"],
                "compression_ratio": float(row["compression_ratio"]),
                "rank": int(row["rank"])
            })

        universe_results = {
            "top_picks": top_picks,
            "all_ratios": dict(zip(rank_df["ticker"], rank_df["compression_ratio"])),
            "lookback_days": config.LOOKBACK_WINDOW if config.LOOKBACK_WINDOW else "full"
        }
        all_results[universe_name] = universe_results

    Path("results").mkdir(exist_ok=True)
    local_path = Path(f"results/complexity_{config.TODAY}.json")
    with open(local_path, "w") as f:
        json.dump({"run_date": config.TODAY, "universes": all_results}, f, indent=2)

    push_results.push_daily_result(local_path)
    print("\n=== Complexity analysis complete ===")

if __name__ == "__main__":
    main()
