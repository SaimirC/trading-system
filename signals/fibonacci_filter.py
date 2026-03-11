# ============================================
# FILTRI FIBONACCI – GOLDEN POCKET DETECTOR
# ============================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from scipy.signal import argrelextrema

def get_swing_points(df, order=5):
    """
    Gjen pikat Swing High dhe Swing Low në një DataFrame me të dhëna OHLC.
    - order: numri i shufrave në secilën anë për të konsideruar një ekstrem.
    Kthen një DataFrame me kolonat shtesë 'swing_high' dhe 'swing_low'.
    """
    df = df.copy()
    # Gjej majat lokale (swing highs)
    high_idx = argrelextrema(df['high'].values, np.greater_equal, order=order)[0]
    df['swing_high'] = np.nan
    df.iloc[high_idx, df.columns.get_loc('swing_high')] = df['high'].iloc[high_idx].values

    # Gjej fundet lokale (swing lows)
    low_idx = argrelextrema(df['low'].values, np.less_equal, order=order)[0]
    df['swing_low'] = np.nan
    df.iloc[low_idx, df.columns.get_loc('swing_low')] = df['low'].iloc[low_idx].values

    return df

def get_fib_levels(swing_low, swing_high):
    """
    Llogarit nivelet Fibonacci nga një lëvizje swing.
    Nëse swing_low < swing_high (tendencë rritëse), nivelet janë nga low në high.
    Përndryshe (tendencë zbritëse), nivelet janë nga high në low.
    Kthen një dictionary me nivelet 0.236, 0.382, 0.5, 0.618, 0.786.
    """
    diff = swing_high - swing_low
    if swing_low < swing_high:  # Uptrend
        return {
            '0.236': swing_high - 0.236 * diff,
            '0.382': swing_high - 0.382 * diff,
            '0.5': swing_high - 0.5 * diff,
            '0.618': swing_high - 0.618 * diff,
            '0.786': swing_high - 0.786 * diff
        }
    else:  # Downtrend (swing_low > swing_high)
        return {
            '0.236': swing_low + 0.236 * diff,
            '0.382': swing_low + 0.382 * diff,
            '0.5': swing_low + 0.5 * diff,
            '0.618': swing_low + 0.618 * diff,
            '0.786': swing_low + 0.786 * diff
        }

def is_in_golden_pocket(price, fib_levels):
    """
    Kontrollon nëse çmimi aktual është midis niveleve 0.5 dhe 0.618.
    """
    lower = min(fib_levels['0.5'], fib_levels['0.618'])
    upper = max(fib_levels['0.5'], fib_levels['0.618'])
    return lower <= price <= upper

def check_fibonacci(symbol, timeframe=mt5.TIMEFRAME_M15, bars=500, swing_order=5):
    """
    Funksioni kryesor për një instrument.
    Merr të dhënat, gjen swing-et e fundit, llogarit Fibonacci dhe kontrollon nëse çmimi aktual është në Golden Pocket.
    Kthen një dictionary me rezultatet.
    """
    # Merr të dhënat
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None:
        print(f"Nuk u morën të dhëna për {symbol}")
        return None

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)

    # Gjej pikat swing
    df = get_swing_points(df, order=swing_order)

    # Merr swing-un më të fundit (më të riun në kohë)
    # Duhet të kemi të paktën një swing high dhe një swing low për të formuar një lëvizje
    last_highs = df['swing_high'].dropna()
    last_lows = df['swing_low'].dropna()

    if len(last_highs) == 0 or len(last_lows) == 0:
        print(f"{symbol}: Nuk u gjetën mjaftueshëm pika swing.")
        return None

    # Përcaktojmë lëvizjen e fundit: nga swing-u i fundit low në swing-un e fundit high (ose anasjelltas)
    # Për thjeshtësi, marrim swing-un më të fundit dhe paraardhësin e tij
    all_swings = pd.concat([last_highs, last_lows]).sort_index()
    if len(all_swings) < 2:
        print(f"{symbol}: Nuk mjaftojnë pikat për një lëvizje.")
        return None

    # Dy pikat më të fundit
    last_swing = all_swings.iloc[-1]
    prev_swing = all_swings.iloc[-2]

    # Përcaktojmë nëse lëvizja është rritëse apo zbritëse
    if prev_swing < last_swing:
        swing_low, swing_high = prev_swing, last_swing
        trend = "UPTREND"
    else:
        swing_low, swing_high = last_swing, prev_swing
        trend = "DOWNTREND"

    # Llogarit nivelet Fibonacci
    fib_levels = get_fib_levels(swing_low, swing_high)

    # Çmimi aktual (mbyllja e shufrës më të fundit)
    current_price = df['close'].iloc[-1]

    # Kontrollo nëse është në Golden Pocket
    in_golden = is_in_golden_pocket(current_price, fib_levels)

    return {
        'symbol': symbol,
        'trend': trend,
        'swing_low': swing_low,
        'swing_high': swing_high,
        'fib_levels': fib_levels,
        'current_price': current_price,
        'in_golden_pocket': in_golden
    }

def filter_all_instruments():
    """
    Teston të gjitha instrumentet dhe tregon cilat janë në Golden Pocket.
    """
    print("\n=== FILTRI FIBONACCI (GOLDEN POCKET) ===\n")
    for symbol in config.INSTRUMENTS:
        result = check_fibonacci(symbol)
        if result:
            status = "✅ NË GOLDEN POCKET" if result['in_golden_pocket'] else "❌ JO NË GOLDEN POCKET"
            print(f"{symbol}: {status} | Çmimi: {result['current_price']:.5f} | "
                  f"Zona 0.5-0.618: [{result['fib_levels']['0.5']:.5f}, {result['fib_levels']['0.618']:.5f}]")

if __name__ == "__main__":
    if not mt5.initialize():
        print("Lidhja me MT5 dështoi")
        quit()
    
    filter_all_instruments()
    
    mt5.shutdown()