# ============================================
# INDIKATORË TEKNIKË PËR INSTRUMENTE TË NDRYSHME
# ============================================

import pandas as pd
import ta
import MetaTrader5 as mt5
import sys
import os

# Shtojmë rrugën e dosjes kryesore për të importuar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Lidhu me MT5
if not mt5.initialize():
    print("Lidhja me MT5 dështoi")
    quit()
print("Lidhur me MT5")

# Përdor instrumentin e parë nga lista për testim (mund ta ndryshosh)
symbol = config.INSTRUMENTS[0]  # "EURUSD"
print(f"\n=== Analizoj {symbol} ===")


# Merr 100 shufrat e fundit M15
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 100)
if rates is None:
    print(f"Nuk u morën të dhëna për {symbol}")
    mt5.shutdown()
    quit()

# Konverto në DataFrame
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)

# Llogarit indikatorët duke përdorur parametrat nga config
df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=config.INDICATOR_PARAMS['rsi_window']).rsi()
df['ema50'] = ta.trend.EMAIndicator(df['close'], window=config.INDICATOR_PARAMS['ema_fast']).ema_indicator()
df['ema200'] = ta.trend.EMAIndicator(df['close'], window=config.INDICATOR_PARAMS['ema_slow']).ema_indicator()
df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], 
                                            window=config.INDICATOR_PARAMS['atr_window']).average_true_range()

# Shfaq 5 rreshtat e fundit
print(df[['close', 'rsi', 'ema50', 'ema200', 'atr']].tail())

# ============================================
# PËR TË ARDHMEN: Mund të shtojmë një cikël për të gjitha instrumentet
# ============================================
# Për të analizuar të gjitha instrumentet njëherësh, thjesht vendos një for:
#
# for symbol in config.INSTRUMENTS:
#     rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 100)
#     ... (pjesa tjetër)

mt5.shutdown()