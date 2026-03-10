import MetaTrader5 as mt5
import pandas as pd

# Inicializo pa specifikuar rrugën
if not mt5.initialize():
    print("Lidhja me MT5 dështoi. Gabimi:", mt5.last_error())
    quit()
else:
    print("Lidhja me MT5 u realizua me sukses!")

# Pjesa tjetër e kodit njësoj...
account_info = mt5.account_info()
if account_info is not None:
    account_info_dict = account_info._asdict()
    df_account = pd.DataFrame([account_info_dict])
    print("\nInformacioni i Llogarisë:")
    print(df_account)
else:
    print("Nuk u mor informacioni i llogarisë.")

rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M5, 0, 10)
if rates is not None:
    df_rates = pd.DataFrame(rates)
    df_rates['time'] = pd.to_datetime(df_rates['time'], unit='s')
    print("\nTë dhënat e fundit për EUR/USD (M5):")
    print(df_rates[['time', 'open', 'high', 'low', 'close']])
else:
    print("Nuk u morën të dhënat e çmimit.")

mt5.shutdown()