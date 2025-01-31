import yfinance as yf
import pandas as pd
from indicators.stochastic_rsi import stochastic_rsi
from indicators.macd import macd
from indicators.bollinger_bands import bollinger_bands
from indicators.average_directional_index import average_directional_index
from indicators.ma import ma
from indicators.stochastic_oscillator import stochastic_fast



# Helper function to calculate growth rate
def calculate_growth_rate(current, previous):
    if current and previous:
        return ((current - previous) / previous) * 100
    return None

def get_beta(stock_symbol, market_symbol='^NSEI', period='1y'):
    # Download stock and market data using yfinance
    stock = yf.Ticker(stock_symbol)
    market = yf.Ticker(market_symbol)
    
    # Download the historical data for both the stock and the market index
    stock_data = stock.history(period=period)
    market_data = market.history(period=period)
    
    # Calculate daily percentage returns for the stock and the market
    stock_data['Return'] = stock_data['Close'].pct_change()
    market_data['Return'] = market_data['Close'].pct_change()
    
    # Align both dataframes to ensure we're comparing the same dates
    data = pd.merge(stock_data[['Return']], market_data[['Return']], left_index=True, right_index=True, suffixes=('_stock', '_market'))
    
    # Drop NaN values that result from pct_change and merge
    data = data.dropna()

    # Calculate the covariance between stock and market returns
    covariance = data['Return_stock'].cov(data['Return_market'])
    
    # Calculate the variance of the market's returns
    market_variance = data['Return_market'].var()
    
    # Calculate Beta
    beta = covariance / market_variance
    return beta

def get_atr(stock_symbol, period=14):
    # Download historical stock data using yfinance
    stock = yf.Ticker(stock_symbol)
    data = stock.history(period="1y")  # Download 1 year of historical data

    # Calculate the True Range (TR) for each day
    data['High-Low'] = data['High'] - data['Low']
    data['High-Close'] = (data['High'] - data['Close'].shift()).abs()
    data['Low-Close'] = (data['Low'] - data['Close'].shift()).abs()

    # Calculate the True Range for each day (maximum of the 3 values)
    data['True Range'] = data[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)

    # Calculate the ATR as the moving average of the True Range over the specified period
    data['ATR'] = data['True Range'].rolling(window=period).mean()

    # Get the latest ATR value
    latest_atr = data['ATR'].iloc[-1]
    
    # Get the current stock price
    current_price = data['Close'].iloc[-1]

    # Calculate the ATR % (volatility percentage)
    atr_percentage = (latest_atr / current_price) * 100
    return atr_percentage


def get_data(stock_symbol):
    stock = yf.Ticker(stock_symbol)
    info = stock.info
    financials = stock.financials
    balance_sheet = stock.balance_sheet
    cashflow = stock.cashflow
    metrics = {}
    history = stock.history(period="1y")
    # Valuation Metrics
    if info.get("trailingPE") != None:
        metrics["P/E Ratio"] = info.get("trailingPE")
    if info.get("priceToBook") != None:
        metrics["P/B Ratio"] = info.get("priceToBook")
    if info.get("PegRatio") != None:
        metrics["PEG Ratio"] = info.get("PegRatio")
    if info.get("debtToEquity") != None:
        metrics["D/E Ratio"] = info.get("debtToEquity")

    # Profitability Metrics
    if info.get("returnOnEquity") != None:
        metrics["ROE (%)"] = info.get("returnOnEquity") * 100 if info.get("returnOnEquity") is not None else 0
    if info.get("profitMargins") != None:
        metrics["Net Profit Margin (%)"] = info.get("profitMargins") * 100 if info.get("profitMargins") else 0
    if info.get("operatingMargins") != None:
        metrics["Operating Margin (%)"] = info.get("operatingMargins") * 100 if info.get("operatingMargins") else 0
    if info.get("grossMargins") != None:
        metrics["Gross Margin (%)"] = info.get("grossMargins") * 100 if info.get("grossMargins") else 0
    
    # Growth Metrics

    revenue_growth = calculate_growth_rate(
        financials.loc["Total Revenue"].iloc[0],
        financials.loc["Total Revenue"].iloc[1] if len(financials.loc["Total Revenue"]) > 1 else 0
    )
    metrics["Revenue Growth (%)"] = revenue_growth

    free_cash_flow = cashflow.loc["Operating Cash Flow"].iloc[0] if "Operating Cash Flow" in cashflow.index else 0

    fcf_growth = calculate_growth_rate(
        free_cash_flow,
        cashflow.loc["Operating Cash Flow"].iloc[1] if len(cashflow.loc["Operating Cash Flow"]) > 1 else 0
    )
    metrics["FCF Growth (%)"] = fcf_growth


    metrics["EPS Growth (%)"]  = info.get("earningsGrowth") * 100 if info.get("operatingMargins") != None else 0


    # Y to Y profit growth
    new_financials = stock.quarterly_financials.T  # Transpose to make columns easy to work with
    if 'Net Income' not in new_financials.columns:
        print("Net Income data not available.")
        return None
    
    # Get the Net Income (Profit) data for the last two years
    net_income = new_financials['Net Income']
    
    # Check if we have at least two years of data
    if len(net_income) < 2:
        print("Insufficient data to calculate YoY Profit Growth.")
        return None
    
    # Calculate YoY Profit Growth
    current_year_profit = net_income.iloc[0]  # Most recent year
    previous_year_profit = net_income.iloc[1]  # Previous year

    # Calculate the YoY profit growth
    yoy_profit_growth = ((current_year_profit - previous_year_profit) / previous_year_profit) * 100
    
    metrics['YoY Profit Growth (%)'] = yoy_profit_growth

    # Y to Y sales growth
    if 'Total Revenue' not in new_financials.columns:
        print("Total Revenue data not available.")
        return None
    
    # Get the Revenue (Sales) data for the last two years
    revenue = new_financials['Total Revenue']
    
    # Check if we have at least two years of data
    if len(revenue) < 2:
        print("Insufficient data to calculate YoY Sales Growth.")
        return None
    
    # Calculate YoY Sales Growth
    current_year_sales = revenue.iloc[0]  # Most recent year
    previous_year_sales = revenue.iloc[1]  # Previous year

    # Calculate the YoY sales growth
    yoy_sales_growth = ((current_year_sales - previous_year_sales) / previous_year_sales) * 100
    metrics['YoY Sales Growth (%)'] = yoy_sales_growth

        # Q to Q sales growth
    
    if 'Total Revenue' not in new_financials.columns:
        print("Total Revenue data not available.")
        return None
    
    # Get the Revenue (Sales) data for the last two quarters
    revenue = new_financials['Total Revenue']
    
    # Check if we have at least two quarters of data
    if len(revenue) < 2:
        print("Insufficient data to calculate QoQ Sales Growth.")
        return None
    
    # Calculate QoQ Sales Growth
    current_quarter_sales = revenue.iloc[0]  # Most recent quarter
    previous_quarter_sales = revenue.iloc[1]  # Previous quarter

    # Calculate the QoQ sales growth
    qoq_sales_growth = ((current_quarter_sales - previous_quarter_sales) / previous_quarter_sales) * 100
    metrics['QoQ Sales Growth (%)']= qoq_sales_growth

    # Q to Q profit growth
    if 'Net Income' not in new_financials.columns:
        print("Net Income data not available.")
        return None
    
    # Get the Net Income (Profit) data for the last two quarters
    net_income = new_financials['Net Income']
    
    # Check if we have at least two quarters of data
    if len(net_income) < 2:
        print("Insufficient data to calculate QoQ Profit Growth.")
        return None
    
    # Calculate QoQ Profit Growth
    current_quarter_profit = net_income.iloc[0]  # Most recent quarter
    previous_quarter_profit = net_income.iloc[1]  # Previous quarter

    # Calculate the QoQ profit growth
    qoq_profit_growth = ((current_quarter_profit - previous_quarter_profit) / previous_quarter_profit) * 100
    metrics['QoQ Profit Growth (%)'] = qoq_profit_growth

    
    #TODO Sales Growth (3-Year > 5-Year)
    #TODO Profit Growth (3-Year > 5-Year)


    # Liquidity and Solvency Metrics
    if info.get("currentRatio") != None:
        metrics["Current Ratio"] = info.get("currentRatio")
    
    # Cash Conversion Cycle (Days)
    # Ensure required data exists
    required_fields = ["Inventory", "Accounts Receivable", "Accounts Payable"]
    for field in required_fields:
        if field not in balance_sheet.index:
            raise ValueError(f"Missing {field} in balance sheet for {stock_symbol}.")
    
    if "Cost Of Revenue" not in financials.index or "Total Revenue" not in financials.index:
        raise ValueError(f"Missing Cost of Revenue or Total Revenue in financials for {stock_symbol}.")

    # Extract relevant data
    inventory = balance_sheet.loc["Inventory"].mean()
    accounts_receivable = balance_sheet.loc["Accounts Receivable"].mean()
    accounts_payable = balance_sheet.loc["Accounts Payable"].mean()
    cogs = financials.loc["Cost Of Revenue"].mean()
    revenue = financials.loc["Total Revenue"].mean()

    # Calculate DIO, DSO, DPO
    dio = (inventory / cogs) * 365 if cogs else 0
    dso = (accounts_receivable / revenue) * 365 if revenue else 0
    dpo = (accounts_payable / cogs) * 365 if cogs else 0

    # Calculate CCC
    ccc = dio + dso - dpo
    metrics['Cash Conversion cycle (Days)'] = float(ccc)
    # TODO: Cash Reserves vs Debt (%)
    

    ebit = financials.loc["EBIT"].iloc[0] if "EBIT" in financials.index else 0
    interest_expense = financials.loc["Interest Expense"].iloc[0] if "Interest Expense" in financials.index else 0

   
    # Calculate derived metrics

    
    metrics["Interest Coverage Ratio"] = ebit / abs(interest_expense) if ebit and interest_expense else 0


    # Momentum and Volatility Metrics

    atr_percentage = get_atr(stock_symbol)
    metrics["Volatility (ATR %)"]= float(atr_percentage)

    metrics['Beta']= float(get_beta(stock_symbol=stock_symbol))
    history = stochastic_rsi(df=history)
    history = macd(df=history)
    history = bollinger_bands(df=history)
    history = average_directional_index(df=history)
    history = ma(df=history, period=50)
    history = stochastic_fast(df=history)
    history = ma(df=history, period=200)
    history['Volatility (%)'] = ((history['High'] - history['Low']) / history['Close']) * 100
    metrics['Volatility (%)'] = float(history['Volatility (%)'].mean())


    # Ownership and Sentiment Metrics

    # TODO: Promoter Holding Change (%)
    # TODO: Institutional Holding Change (%)
    metrics['Promoter Holding'] = stock.info.get("heldPercentInsiders", "N/A")
    metrics['Institutions Holding'] = stock.info.get("heldPercentInstitutions", "N/A")
    metrics['RSI'] = round(float(history['RSI'].iloc[-1]), 2)
    metrics['MACD Signal Line Cross'] =  round(float(history['MACD_HIST'].iloc[-1]),2)
    metrics['Volume Change (%)'] =  float(round((history['Volume'].iloc[-1] - history['Volume'].iloc[-2])/ history['Volume'].iloc[-2], 2))
    metrics['Price Above SMA-200 (%)'] = float(round((history['Close'].iloc[-1] - history['MA_200'].iloc[-1]) / history['MA_200'].iloc[-1], 2))
    metrics['Stochastic Oscillator'] = round(float(history['STOCH_FAST_D'].iloc[-1]),2)
    metrics['SMA-50 vs SMA-200'] = float(round((history['MA_50'].iloc[-1] - history['MA_200'].iloc[-1])/ history['MA_200'].iloc[-1], 2))
    metrics['Price Change (%)'] =  float(round((history['Close'].iloc[-1] - history['Close'].iloc[-2])/ history['Close'].iloc[-2], 2))
    metrics['Bollinger Bands %B'] =  float(round((history['BB_UPPER'].iloc[-1] - history['BB_LOWER'].iloc[-1]) / history['BB_LOWER'].iloc[-1], 2))
    # Market and Price Metrics:
    market_price = info.get("currentPrice")
    price_52_week_high = history["High"].max()
    price_52_week_low = history["Low"].min()
    price_moved_from_52_week_high = ((market_price- price_52_week_high) / price_52_week_high) * 100
    metrics['Price Moved from 52-Week High (%)'] = float(price_moved_from_52_week_high)
    metrics["Price (₹)"] = market_price
    metrics['Market Cap (₹)'] = info.get('marketCap') if info.get("marketCap") else 0
    price_moved_from_52_week_low = ((market_price- price_52_week_low) / price_52_week_low) * 100
    metrics['Price Away from 52-Week Low (%)'] = float(price_moved_from_52_week_low)
    metrics['PEG Ratio'] =  info.get('trailingPegRatio') if info.get("trailingPegRatio") is not None else 0
    # Dividend Metrics
    metrics['MACD Signal'] = float(history['MACD_SIGN'].iloc[-1])
    metrics["Dividend Yield (%)"] = info.get("dividendYield") * 100 if info.get("dividendYield") else 0

    return metrics

    


