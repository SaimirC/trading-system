# ============================================
# DETEKTIMI I REGJIMIT TË TREGUT (ADX)
# ============================================

import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def calculate_adx(high, low, close, period=14):
    """
    Llogarit ADX (Average Directional Index) për një seri të dhënash.
    """
    # Llogarit +DM dhe -DM
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    minus_dm = abs(minus_dm)
    
    # Llogarit True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Llogarit ATR
    atr = tr.rolling(window=period).mean()
    
    # Llogarit +DI dhe -DI
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    
    # Llogarit DX dhe ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    
    return adx, plus_di, minus_di

def classify_regime(adx_value, threshold=25):
    """
    Klasifikon regjimin e tregut bazuar në vlerën e ADX.
    """
    if adx_value >= threshold:
        return "TRENDING"
    else:
        return "RANGING"

def get_market_regime(symbol, timeframe=mt5.TIMEFRAME_H1, bars=200):
    """
    Merr të dhënat për një simbol dhe kthen regjimin aktual të tregut.
    """
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None:
        print(f"Nuk u morën të dhëna për {symbol}")
        return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    
    adx, _, _ = calculate_adx(df['high'], df['low'], df['close'], 
                               period=config.INDICATOR_PARAMS['adx_window'])
    
    current_adx = adx.iloc[-1]
    regime = classify_regime(current_adx)
    
    return {
        'symbol': symbol,
        'adx': current_adx,
        'regime': regime,
        'data': df,
        'adx_series': adx
    }

if __name__ == "__main__":
    if not mt5.initialize():
        print("Lidhja me MT5 dështoi")
        quit()
    
    print("\n=== TESTIMI I ADX PËR TË GJITHA INSTRUMENTET ===\n")
    for symbol in config.INSTRUMENTS:
        result = get_market_regime(symbol, mt5.TIMEFRAME_H1, bars=200)
        if result:
            print(f"{symbol}: ADX = {result['adx']:.2f} -> {result['regime']}")
    
    mt5.shutdown()