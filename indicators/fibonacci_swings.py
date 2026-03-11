# ============================================
# FIBONACCI DHE PIKAT SWING PËR INSTRUMENTE TË NDRYSHME
# ============================================

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Lidhu me MT5
if not mt5.initialize():
    print("Lidhja me MT5 dështoi")
    quit()
print("Lidhur me MT5")

# Zgjidh instrumentin (për testim përdor të parin)
symbol = config.INSTRUMENTS[0]  # "EURUSD"
print(f"\n=== Analizoj {symbol} për pikat Swing ===")

# Merr 500 shufrat e fundit M15
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 500)
if rates is None:
    print(f"Nuk u morën të dhëna për {symbol}")
    mt5.shutdown()
    quit()

# Pjesa tjetër e kodit vijon njësoj...
# (vazhdo nga pjesa ku krijon df, gjen swing highs/lows, etj.)