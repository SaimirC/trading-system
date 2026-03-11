# ============================================
# KONFIGURIMI I INSTRUMENTEVE DHE PARAMETRAVE
# ============================================

# Lista e të gjitha instrumenteve që do të tregtojmë
INSTRUMENTS = [
    "EURUSD",   # Euro / Dollar
    "GBPUSD",   # Sterlina / Dollar
    "USDJPY",   # Dollar / Jeni
    "AUDUSD",   # Dollari Australian / Dollar
    "USDCAD",   # Dollar / Dollari Kanadez
    "XAUUSD",   # Ar / Dollar
    "XAGUSD"    # Argjend / Dollar
]

# Timeframes që do të përdorim (për kontekst dhe hyrje)
TIMEFRAMES = {
    "higher": ["H4", "H1"],
    "lower": ["M15", "M5"]
}

# Parametrat e përbashkët për indikatorët
INDICATOR_PARAMS = {
    "rsi_window": 14,
    "ema_fast": 50,
    "ema_slow": 200,
    "atr_window": 14,
    "adx_window": 14
}

# Parametrat për swing detection
SWING_PARAMS = {
    "order": 5  # Numri i shufrave për të majtas/djathtas për ekstremet lokale
}

# Parametrat për Fibonacci
FIB_PARAMS = {
    "tolerance": 0.001,  # 0.1% tolerancë për zonën Golden Pocket
    "confluence_threshold": 3  # Pragu për sinjal (score >= 3)
}