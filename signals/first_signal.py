# ============================================
# SINJALI I PARË ME CONFLUENCE SCORE
# ============================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import MetaTrader5 as mt5
from signals.trend_filter import is_trending
from signals.fibonacci_filter import check_fibonacci

def calculate_confluence_score(symbol):
    """
    Llogarit një score nga 0-4 bazuar në disa faktorë.
    Score >= threshold (në config) gjeneron sinjal.
    """
    score = 0
    reasons = []
    
    # Filtri 1: Trend nga ADX
    if is_trending(symbol):
        score += 1
        reasons.append("adx_trend")
    
    # Filtri 2: Golden Pocket nga Fibonacci
    fib_result = check_fibonacci(symbol)
    if fib_result and fib_result['in_golden_pocket']:
        score += 1
        reasons.append("fib_golden")
    
    # Filtri 3: Nëse jemi në Golden Pocket, kontrollojmë nëse trendi i lëvizjes
    # përputhet me trendin e përgjithshëm
    if fib_result:
        if (fib_result['overall_trend'] == "UPTREND" and fib_result['swing_trend'] == "UPTREND"):
            score += 1
            reasons.append("trend_alignment")
        elif (fib_result['overall_trend'] == "DOWNTREND" and fib_result['swing_trend'] == "DOWNTREND"):
            score += 1
            reasons.append("trend_alignment")
    
    # Filtri 4: Volatilitet i përshtatshëm (do të shtojmë më vonë)
    # Për tani, e lëmë placeholder
    # if good_volatility(symbol):
    #     score += 1
    #     reasons.append("volatility_ok")
    
    return score, reasons, fib_result

def scan_all_instruments():
    """
    Skanon të gjitha instrumentet dhe kthen listën e sinjaleve.
    """
    signals = []
    threshold = config.FIB_PARAMS.get('confluence_threshold', 3)
    
    print(f"\n=== SKANIMI PËR SINJALE (pragu = {threshold}) ===\n")
    
    for symbol in config.INSTRUMENTS:
        score, reasons, fib_result = calculate_confluence_score(symbol)
        
        if score >= threshold and fib_result:
            # Përcaktojmë drejtimin
            if fib_result['overall_trend'] == "UPTREND":
                signal = "BUY"
            else:
                signal = "SELL"
            
            signal_info = {
                'symbol': symbol,
                'signal': signal,
                'price': fib_result['current_price'],
                'fib_levels': fib_result['fib_levels'],
                'trend': fib_result['overall_trend'],
                'score': score,
                'reasons': reasons
            }
            signals.append(signal_info)
            print(f"✅ SINJAL {signal} për {symbol} | Score: {score}/{threshold} | Arsye: {reasons}")
        else:
            print(f"❌ {symbol}: Score {score}/{threshold} | Arsye: {reasons if reasons else 'asnjë'}")
    
    return signals

if __name__ == "__main__":
    if not mt5.initialize():
        print("Lidhja me MT5 dështoi")
        quit()
    
    signals = scan_all_instruments()
    
    if signals:
        print(f"\n🎯 Gjithsej {len(signals)} sinjale të gjetura:")
        for sig in signals:
            print(f"   - {sig['symbol']}: {sig['signal']} në {sig['price']:.5f} (score {sig['score']})")
    else:
        print("\n😴 Nuk u gjet asnjë sinjal.")
    
    mt5.shutdown()