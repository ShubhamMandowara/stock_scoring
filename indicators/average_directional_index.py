import pandas as pd


def average_directional_index(df):
    """
    True Range(TR) is max of
        -Current High less the current Low
        -Current High less the previous Close (absolute value)
        -Current Low less the previous Close (absolute value)

    Positive DM = maximum of Current High - PriorHigh and 0 if Current High - Prior High > Prior Low - Current Low

    Negative DM = maximum of Prior Low - Current Low and 0 if Prior Low - Current Low > Current High - Prior High

    Calculation of TR14
    First TR14 = Sum of first 14 periods of TR1
    Second TR14 = First TR14 - (First TR14/14) + Current TR1
    Subsequent Values = Prior TR14 - (Prior TR14/14) + Current TR1

    positive DM14 abd negative DM14 smoothed same as TR14

    positive DI = positive DM14 / TR14
    negative DI = negative DM14 / TR14

    DX = absolute (positive DI - negative DI)/absolute(positive DI + negative DI)

    First ADX14 = 14 period Average of DX
    Second ADX14 = ((First ADX14 x 13) + Current DX Value)/14
    Subsequent ADX14 = ((Prior ADX14 x 13) + Current DX Value)/14
    """

    df1 = df.copy()
    pd.set_option("chained_assignment", None)
    Low = df["Low"]
    High = df["High"]
    Close = df["Close"]

    # Calculation Of True Range
    a = High - Low
    b = abs(High - Close.shift(1))
    c = abs(Low - Close.shift(1))
    d = round(a.clip(lower=b, axis=0), 3)
    TR = round(d.clip(lower=c, axis=0), 3)
    df["TR"] = TR

    # Calculation of Pos DM
    a = High - High.shift(1)
    b = Low.shift(1) - Low
    pos_DM1 = pd.Series([max(a[i], 0) if a[i] > b[i] else 0 for i in range(len(a))])
    pos_DM1 = round(pos_DM1, 3)
    df["pos_DM1"] = pos_DM1

    # Calculation of Neg DM
    neg_DM1 = pd.Series([max(b[i], 0) if b[i] > a[i] else 0 for i in range(len(a))])
    neg_DM1 = round(neg_DM1, 3)
    df["neg_DM1"] = neg_DM1

    # TR14 Calculation
    df["TR14"] = pd.Series()
    df["TR14"].iloc[14] = df["TR"][:15].sum()

    for i in range(15, len(df)):
        df["TR14"][i] = df["TR14"][i - 1] - (df["TR14"][i - 1] / 14) + df["TR"][i]

    # Calculation of Positive DM14 as well as Negative DM14
    df["pos_DM14"] = pd.Series()
    df["pos_DM14"].iloc[14] = df["pos_DM1"][:15].sum()

    for i in range(15, len(df)):
        df["pos_DM14"][i] = (
            df["pos_DM14"][i - 1] - (df["pos_DM14"][i - 1] / 14) + df["pos_DM1"][i]
        )

    df["neg_DM14"] = pd.Series()
    df["neg_DM14"].iloc[14] = df["neg_DM1"][:15].sum()

    for i in range(15, len(df)):
        df["neg_DM14"][i] = (
            df["neg_DM14"][i - 1] - (df["neg_DM14"][i - 1] / 14) + df["neg_DM1"][i]
        )

    # DI Calculation
    df["pos_DI14"] = df["pos_DM14"] / df["TR14"] * 100
    df["neg_DI14"] = df["neg_DM14"] / df["TR14"] * 100

    df["DI 14 Diff"] = abs(df["pos_DI14"] - df["neg_DI14"])
    df["DI 14 Sum"] = abs(df["pos_DI14"] + df["neg_DI14"])

    # DX Calculation
    df["DX"] = df["DI 14 Diff"] / df["DI 14 Sum"] * 100

    # ADX Calculation
    df["ADX"] = pd.Series()
    df["ADX"].iloc[27] = df["DX"].iloc[13:27].mean()

    for i in range(28, len(df)):
        df["ADX"][i] = (df["ADX"][i - 1] * 13 + df["DX"][i]) / 14

    df1["ADX"] = df["ADX"]
    return df1