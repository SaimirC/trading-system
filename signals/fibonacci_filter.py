# ============================================
# FILTRI FIBONACCI – GOLDEN POCKET DETECTOR
# VERSIONI I PËRMIRËSUAR ME:
# - Zgjedhje valide e pikave swing
# - Filtrimi me EMA50/EMA200
# - Tolerancë për zonën
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

def get_last_valid_swing(df):
    """
    Gjen dy pikat e fundit swing që formojnë një lëvizje valide (high dhe low).
    Kthen (swing_low, swing_high, trend) ku trend është "UPTREND" nëse lëvizja e fundit
    ishte nga low në high, ose "DOWNTREND" nëse ishte nga high në low.
    """
    highs = df['swing_high'].dropna()
    lows = df['swing_low'].dropna()
    
    # Krijo një seri të vetme me të gjitha pikat, duke shënuar llojin
    all_points = []
    for idx in highs.index:
        all_points.append((idx, 'high', highs[idx]))
    for idx in lows.index:
        all_points.append((idx, 'low', lows[idx]))
    
    # Rendit sipas indeksit (kohës)
    all_points.sort(key=lambda x: x[0])
    
    if len(all_points) < 2:
        return None, None, None
    
    # Kërko dy pikat e fundit që janë të llojeve të ndryshme
    last_valid = None
    for i in range(len(all_points)-1, 0, -1):
        if all_points[i][1] != all_points[i-1][1]:
            last_valid = (all_points[i-1], all_points[i])
            break
    
    if last_valid is None:
        return None, None, None
    
    p1, p2 = last_valid
    # p1 është më e hershme, p2 më e vonë
    if p1[1] == 'low' and p2[1] == 'high':
        return p1[2], p2[2], "UPTREND"
    elif p1[1] == 'high' and p2[1] == 'low':
        return p2[2], p1[2], "DOWNTREND"  # Kthe (low, high) për llogaritje
    else:
        return None, None, None

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
    else:  # Downtrend (swing_low > swing_high) - ky rast nuk duhet të ndodhë me logjikën tonë
        return {
            '0.236': swing_low + 0.236 * diff,
            '0.382': swing_low + 0.382 * diff,
            '0.5': swing_low + 0.5 * diff,
            '0.618': swing_low + 0.618 * diff,
            '0.786': swing_low + 0.786 * diff
        }

def is_in_golden_pocket_with_tolerance(price, fib_levels, tolerance=0.001):
    """
    Kontrollon nëse çmimi është brenda një tolerance nga zona 0.5-0.618.
    tolerance = 0.001 do të thotë 0.1% e çmimit.
    """
    lower = min(fib_levels['0.5'], fib_levels['0.618'])
    upper = max(fib_levels['0.5'], fib_levels['0.618'])
    
    # Zgjero zonën me tolerance
    lower -= price * tolerance
    upper += price * tolerance
    
    return lower <= price <= upper

def check_fibonacci(symbol, timeframe=mt5.TIMEFRAME_M15, bars=500, swing_order=5):
    """
    Funksioni kryesor për një instrument.
    Merr të dhënat, gjen swing-et e fundit, llogarit Fibonacci dhe kontrollon nëse çmimi aktual është në Golden Pocket.
    Tani përfshin:
    - Filtër trendi me EMA50/EMA200
    - Zgjedhje valide të pikave swing
    - Tolerancë për zonën
    """
    # Merr të dhënat
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None:
        print(f"Nuk u morën të dhëna për {symbol}")
        return None

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)

    # Llogarit EMA50 dhe EMA200 për kontrollin e trendit
    df['ema50'] = df['close'].ewm(span=50).mean()
    df['ema200'] = df['close'].ewm(span=200).mean()
    
    trend_up = df['ema50'].iloc[-1] > df['ema200'].iloc[-1]
    trend_down = df['ema50'].iloc[-1] < df['ema200'].iloc[-1]
    
    # Nëse nuk ka trend të qartë, kthej None (pa sinjal)
    if not (trend_up or trend_down):
        return None

    # Gjej pikat swing
    df = get_swing_points(df, order=swing_order)

    # Merr lëvizjen e fundit të vlefshme
    swing_low, swing_high, swing_trend = get_last_valid_swing(df)
    if swing_low is None or swing_high is None:
        return None

    # Llogarit nivelet Fibonacci
    fib_levels = get_fib_levels(swing_low, swing_high)

    # Çmimi aktual (mbyllja e shufrës më të fundit)
    current_price = df['close'].iloc[-1]

    # Kontrollo nëse është në Golden Pocket me tolerancë
    tolerance = config.FIB_PARAMS.get('tolerance', 0.001)
    in_golden = is_in_golden_pocket_with_tolerance(current_price, fib_levels, tolerance)

    # Përcakto trendin e përgjithshëm (për sinjalin)
    if trend_up:
        overall_trend = "UPTREND"
    else:
        overall_trend = "DOWNTREND"

    return {
        'symbol': symbol,
        'swing_trend': swing_trend,
        'overall_trend': overall_trend,
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
                  f"Zona 0.5-0.618: [{result['fib_levels']['0.5']:.5f}, {result['fib_levels']['0.618']:.5f}] | "
                  f"Trendi: {result['overall_trend']}")
        else:
            print(f"{symbol}: ❌ Nuk plotëson kriteret (pa trend ose pa lëvizje valide)")

if __name__ == "__main__":
    if not mt5.initialize():
        print("Lidhja me MT5 dështoi")
        quit()
    
    filter_all_instruments()
    
    mt5.shutdown()