import pandas as pd


def stochastic_fast(df, Kperiod=10, Dperiod=3):
    """
    Fast K = (Current Close - Lowest Low)/(Highest High - Lowest Low) * 100
    Fast D = 3-day SMA of %K
    """

    K = 100 * (
        (df.Close - df.Low.rolling(window=Kperiod).min())
        / (df.High.rolling(window=Kperiod).max() - df.Low.rolling(window=Kperiod).min())
    )
    df["STOCH_FAST_K"] = K
    D = K.rolling(Dperiod).mean()
    df["STOCH_FAST_D"] = D
    return df


def stochastic_slow(df, Kperiod=10, Dperiod=3):
    """
    Slow K = Kperiod SMA of Fast K
    Slow D = Dperiod SMA of Slow K
    """

    df = stochastic_fast(df)
    K = df["STOCH_FAST_K"]
    slowK = K.rolling(Kperiod).mean()
    df["STOCH_SLOW_K"] = slowK
    slowD = slowK.rolling(Dperiod).mean()
    df["STOCH_SLOW_D"] = slowD
    return df
