# P2-ETF-COMPRESSION-COMPLEXITY

**Algorithmic complexity analysis via compression (zlib).**  
Ranks ETFs by compressibility of their return series – lower compression ratio indicates more predictable (i.e., less efficient) behaviour.

## Features

- Uses **zlib** lossless compression as a proxy for Kolmogorov complexity.
- Computes compression ratio = compressed size / original size.
- Ranks assets: lower ratio → more compressible → more likely to exhibit patterns.
- Works on three ETF universes (FI_COMMODITIES, EQUITY_SECTORS, COMBINED).
- Data from `P2SAMAPA/fi-etf-macro-signal-master-data` (2008–present).
- Results pushed to `P2SAMAPA/p2-etf-compression-complexity-results`.

## Installation

```bash
git clone https://github.com/P2SAMAPA/P2-ETF-COMPRESSION-COMPLEXITY.git
cd P2-ETF-COMPRESSION-COMPLEXITY
pip install -r requirements.txt
