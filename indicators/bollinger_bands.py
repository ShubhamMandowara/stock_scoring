import pandas as pd
import numpy as np


def bollinger_bands(df, period=20, extra=False):
    """
    Main Function To Be Called To Get All the Values Of Bollinger Bands
    """

    df["BB_LOWER"] = lower_bollinger_band(df.Close, period)
    df["BB_MIDDLE"] = middle_bollinger_band(df.Close, period)
    df["BB_UPPER"] = upper_bollinger_band(df.Close, period)

    if extra:
        df["bandwidth"] = bandwidth(df)
        df["bb_range"] = bb_range(df)
        df["percent_bandwidth"] = percent_bandwidth(df)
        df["percent_b"] = percent_b(df)
    return df


def upper_bollinger_band(data, period, std_mult=2.0):
    """
    Upper Bollinger Band.

    Formula:
    u_bb = SMA(t) + STD(SMA(t-n:t)) * std_mult
    """

    period = int(period)
    simple_ma = data.rolling(window=period).mean()[period - 1 :]

    upper_bb = []
    for idx in range(len(data) - period + 1):
        std_dev = np.std(data[idx : idx + period])
        upper_bb.append(simple_ma.iloc[idx] + std_dev * std_mult)

    non_computable_values = np.repeat(np.nan, len(data) - len(upper_bb))
    upper_bb = np.append(non_computable_values, upper_bb)

    return np.array(upper_bb)


def middle_bollinger_band(data, period, std=2.0):
    """
    Middle Bollinger Band.

    Formula:
    m_bb = sma()
    """

    period = int(period)
    mid_bb = data.rolling(window=period).mean()

    return mid_bb


def lower_bollinger_band(data, period, std=2.0):
    """
    Lower Bollinger Band.

    Formula:
    u_bb = SMA(t) - STD(SMA(t-n:t)) * std_mult
    """

    period = int(period)
    simple_ma = data.rolling(window=period).mean()[period - 1 :]
    lower_bb = []
    for idx in range(len(data) - period + 1):
        std_dev = np.std(data[idx : idx + period])
        lower_bb.append(simple_ma.iloc[idx] - std_dev * std)

    non_computable_values = np.repeat(np.nan, len(data) - len(lower_bb))
    lower_bb = np.append(non_computable_values, lower_bb)
    return np.array(lower_bb)


def bandwidth(df):
    """
    Bandwidth.

    Formula:
    bw = u_bb - l_bb / m_bb
    """

    bandwidth = (
        df["upper_bollinger_band"]
        - df["lower_bollinger_band"] / df["middle_bollinger_band"]
    )

    return bandwidth


def bb_range(df):
    """
    Range.

    Formula:
    bb_range = u_bb - l_bb
    """
    bb_range = df["upper_bollinger_band"] - df["lower_bollinger_band"]
    return bb_range


def percent_bandwidth(df):
    """
    Percent Bandwidth.

    Formula:
    %_bw = data() - l_bb() / bb_range()
    """
    percent_bandwidth = df.Close - df.lower_bollinger_band / bb_range(df)
    return percent_bandwidth


def percent_b(df):
    """
    %B.

    Formula:
    %B = ((data - lb) / (ub - lb)) * 100
    """
    lb = df.lower_bollinger_band
    ub = df.upper_bollinger_band
    percent_b = ((df.Close - lb) / (ub - lb)) * 100
    return percent_b