
import pandas as pd


def macd(df, n_fast=12, n_slow=26, n_signal=9):
    """
    MACD = 12 Period EMA - 26 Period EMA
    MACD Signal = 9 Period EMA of MACD
    MACD Hist = MACD-MACD signal
    """
    EMAfast = pd.Series(df["Close"].ewm(span=n_fast, min_periods=n_slow).mean())
    EMAslow = pd.Series(df["Close"].ewm(span=n_slow, min_periods=n_slow).mean())

    MACD = pd.Series(EMAfast - EMAslow, name="MACD")
    MACDsign = pd.Series(
        MACD.ewm(span=n_signal, min_periods=n_signal).mean(), name="MACD_SIGN"
    )
    MACDdiff = pd.Series(MACD - MACDsign, name="MACD_HIST")

    df = df.join(MACD)
    df = df.join(MACDsign)
    df = df.join(MACDdiff)
    return df
