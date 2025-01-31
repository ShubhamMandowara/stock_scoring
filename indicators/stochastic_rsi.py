import pandas as pd
import numpy as np


def relative_strength_index(df, period=14):
    """
    Positive Change = Close - Prior Close if it is positive
    Negative Change = Close - Prior Close if it is negative

    average_gain = Wilders Smoothed moving average of positive change as per period
    average_loss = Wilders Smoothed moving average of negative change as per period

    RS = (((Prior Average Gain * period-1) + Current Positive Change)/14)/(((Prior Average Loss * period-1) + Current Negative Change)/14)

    RSI = 100-(100/(1+RS))

    """

    change = df.Close - df.Close.shift(1)
    pos_change = change.copy()
    pos_change[pos_change < 0] = 0

    neg_change = change.copy()
    neg_change[neg_change > 0] = 0
    neg_change = abs(neg_change)

    avg_gain = pos_change.rolling(window=period, min_periods=period - 1).mean()
    avg_loss = neg_change.rolling(window=period, min_periods=period - 1).mean()

    for i in range(period + 1, len(df)):
        avg_gain[i] = (avg_gain[i - 1] * (period - 1) + pos_change[i]) / period

    for i in range(period + 1, len(df)):
        avg_loss[i] = (avg_loss[i - 1] * (period - 1) + neg_change[i]) / period

    RS = pd.Series(np.zeros(len(df)))

    RS = (((avg_gain.shift(1) * (period - 1)) + pos_change) / period) / (
        ((avg_loss.shift(1) * (period - 1)) + neg_change) / period
    )
    RS[period - 1] = avg_gain[period - 1] / avg_loss[period - 1]

    df["RSI"] = 100 - (100 / (1 + RS))
    return df


def stochastic_rsi(df, period=14, Kperiod=5, Dperiod=3):
    # Stochastic_Fast of RSi will give stochastic relative strength
    df = stochastic_fast_rsi(relative_strength_index(df, period), Kperiod, Dperiod)

    return df


def stochastic_fast_rsi(df, Kperiod=14, Dperiod=3):
    # Calculation of Fast K and D for RSI
    """
    %K = (Current Close - Lowest Low)/(Highest High - Lowest Low) * 100
    %D = 3-day SMA of %K
    """

    K = 100 * (
        (df.RSI - df.RSI.rolling(window=Kperiod).min())
        / (df.RSI.rolling(window=Kperiod).max() - df.RSI.rolling(window=Kperiod).min())
    )
    df["RSI_FAST_K"] = K
    D = K.rolling(Dperiod).mean()
    df["RSI_FAST_D"] = D
    return df