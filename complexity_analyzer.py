"""
Algorithmic complexity analysis using compression (zlib).
Computes compression ratio as proxy for Kolmogorov complexity.
"""

import zlib
import numpy as np
import pandas as pd

class ComplexityAnalyzer:
    def __init__(self, compression_level=9, lookback=None):
        self.compression_level = compression_level
        self.lookback = lookback   # number of days to use (None = all)

    def _to_bytes(self, series):
        """Convert a numpy array of floats to a byte string for compression."""
        # Scale to 16‑bit integers to preserve precision while reducing size
        # We multiply by 1e6 to capture 6 decimal places of log returns
        scaled = (series * 1e6).astype(np.int32)
        return scaled.tobytes()

    def compression_ratio(self, series):
        """Return compressed size / original size (lower = more compressible)."""
        if len(series) == 0:
            return 1.0
        byte_data = self._to_bytes(series)
        original_size = len(byte_data)
        if original_size == 0:
            return 1.0
        compressed = zlib.compress(byte_data, level=self.compression_level)
        return len(compressed) / original_size

    def normalised_compression_distance(self, x, y):
        """NCD between two series (optional, not used in ranking)."""
        cx = self.compression_ratio(x) * len(x)
        cy = self.compression_ratio(y) * len(y)
        xy = np.concatenate([x, y])
        cxy = self.compression_ratio(xy) * len(xy)
        return (cxy - min(cx, cy)) / max(cx, cy)

    def rank_tickers(self, returns_df):
        """
        returns_df: DataFrame with dates as index, tickers as columns.
        Returns: DataFrame with ticker, compression_ratio, and rank.
        """
        ratios = {}
        for ticker in returns_df.columns:
            series = returns_df[ticker].dropna()
            if self.lookback is not None and len(series) > self.lookback:
                series = series.iloc[-self.lookback:]
            if len(series) < 10:
                ratios[ticker] = 1.0
                continue
            ratio = self.compression_ratio(series.values)
            ratios[ticker] = ratio
        # Create sorted ranking (lower ratio = more compressible = higher rank)
        sorted_items = sorted(ratios.items(), key=lambda x: x[1])
        rank_df = pd.DataFrame([(t, r, i+1) for i, (t, r) in enumerate(sorted_items)],
                               columns=["ticker", "compression_ratio", "rank"])
        return rank_df
