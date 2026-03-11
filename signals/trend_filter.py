# ============================================
# FILTRI I TRENDIT (ADX)
# ============================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from indicators.regime_detector import get_market_regime
import MetaTrader5 as mt5

def is_trending(symbol, timeframe=mt5.TIMEFRAME_H1):
    """
    Kthen True nëse instrumenti është në trend (ADX > 25), False përndryshe.
    """
    result = get_market_regime(symbol, timeframe)
    if result is None:
        return False
    return result['regime'] == "TRENDING"

def filter_all_instruments():
    """
    Teston të gjitha instrumentet dhe tregon cilat janë në trend.
    """
    print("\n=== FILTRI I TRENDIT ===\n")
    for symbol in config.INSTRUMENTS:
        if is_trending(symbol):
            print(f"✅ {symbol} - NË TREND")
        else:
            print(f"❌ {symbol} - JO NË TREND")

if __name__ == "__main__":
    if not mt5.initialize():
        print("Lidhja me MT5 dështoi")
        quit()
    
    filter_all_instruments()
    
    mt5.shutdown()