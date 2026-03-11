# ============================================
# FILTRAT KRYESORË TË VENDIMMARRJES
# ============================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from indicators.regime_detector import get_market_regime
import MetaTrader5 as mt5

def trend_filter(symbol, timeframe=mt5.TIMEFRAME_H1):
    """
    Filtri 1: Kontrollon nëse tregu është në trend (ADX > 25)
    Kthen True nëse është në trend, False përndryshe.
    """
    result = get_market_regime(symbol, timeframe)
    if result is None:
        return False
    return result['regime'] == "TRENDING"

def fibonacci_zone_filter(symbol, timeframe=mt5.TIMEFRAME_M15):
    """
    Filtri 2: Kontrollon nëse çmimi aktual është afër zonës Golden Pocket (0.5-0.618)
    Kjo është një version i thjeshtë; do ta detajojmë më vonë.
    """
    # Për momentin, kthejmë True për testim
    # Në të ardhmen, këtu do të llogarisim nivelet Fibonacci
    return True

def should_trade(symbol):
    """
    Funksioni kryesor që vendos nëse duhet të tregtojmë një instrument.
    Kombinon të gjithë filtrat.
    """
    # Hapi 1: Kontrollo trendin në H1
    if not trend_filter(symbol, mt5.TIMEFRAME_H1):
        print(f"{symbol}: Refuzohet - nuk është në trend")
        return False
    
    # Hapi 2: Kontrollo zonën Fibonacci në M15
    if not fibonacci_zone_filter(symbol, mt5.TIMEFRAME_M15):
        print(f"{symbol}: Refuzohet - nuk është në zonën Fibonacci")
        return False
    
    # Nëse kalon të gjithë filtrat
    print(f"{symbol}: KALON filtrat - gati për sinjal")
    return True

# ============================================
# TESTIMI PËR TË GJITHA INSTRUMENTET
# ============================================
if __name__ == "__main__":
    if not mt5.initialize():
        print("Lidhja me MT5 dështoi")
        quit()
    
    print("\n=== TESTIMI I FILTRAVE PËR TË GJITHA INSTRUMENTET ===\n")
    for symbol in config.INSTRUMENTS:
        print(f"\nAnalizoj {symbol}...")
        should_trade(symbol)
    
    mt5.shutdown()