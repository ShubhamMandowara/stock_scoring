def ma(df, period):
    df["MA_" + str(period)] = df["Close"].rolling(window=period).mean()
    return df
