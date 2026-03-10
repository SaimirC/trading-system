import pandas as pd
import ta
import MetaTrader5 as mt5
from datetime import datetime

# Lidhu me MT5 (pa specifikuar rrugë, pasi testi tregoi se funksionon)
if not mt5.initialize():
    print("Lidhja me MT5 dështoi")
    quit()

# Merr të dhëna për EURUSD (100 shufra M15)
rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M15, 0, 100)
if rates is None:
    print("Nuk u morën të dhëna")
    mt5.shutdown()
    quit()

# Konverto në DataFrame
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)

# Llogarit disa indikatorë me bibliotekën 'ta'
df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
df['ema50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()

# Shfaq 5 rreshtat e fundit
print(df[['close', 'rsi', 'ema50', 'atr']].tail())

# Mbyll lidhjen
mt5.shutdown()