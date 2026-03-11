# ============================================
# SINJALI I PARË: TREND + GOLDEN POCKET
# ============================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import MetaTrader5 as mt5
from signals.trend_filter import is_trending
from signals.fibonacci_filter import check_fibonacci

def generate_signal(symbol):
    """
    Gjeneron një sinjal për një instrument duke kombinuar filtrat e trendit dhe Fibonacci.
    """
    # Filtri 1: A është në trend?
    if not is_trending(symbol):
        return None  # Nuk ka sinjal
    
    # Filtri 2: A është në Golden Pocket?
    fib_result = check_fibonacci(symbol)
    if fib_result is None or not fib_result['in_golden_pocket']:
        return None  # Nuk ka sinjal
    
    # Nëse kalon të dy filtrat, kemi sinjal
    # Përcaktojmë drejtimin bazuar në trendin e lëvizjes
    if fib_result['trend'] == "UPTREND":
        signal = "BUY"
    else:
        signal = "SELL"
    
    return {
        'symbol': symbol,
        'signal': signal,
        'price': fib_result['current_price'],
        'fib_levels': fib_result['fib_levels'],
        'trend': fib_result['trend']
    }

def scan_all_instruments():
    """
    Skanon të gjitha instrumentet dhe kthen listën e sinjaleve.
    """
    signals = []
    print("\n=== SKANIMI PËR SINJALE ===\n")
    for symbol in config.INSTRUMENTS:
        sig = generate_signal(symbol)
        if sig:
            signals.append(sig)
            print(f"✅ SINJAL {sig['signal']} për {sig['symbol']} në çmimin {sig['price']:.5f}")
        else:
            print(f"❌ {symbol}: Nuk ka sinjal")
    
    return signals

if __name__ == "__main__":
    if not mt5.initialize():
        print("Lidhja me MT5 dështoi")
        quit()
    
    signals = scan_all_instruments()
    
    if signals:
        print(f"\nGjithsej {len(signals)} sinjale të gjetura.")
    else:
        print("\nNuk u gjet asnjë sinjal.")
    
    mt5.shutdown()