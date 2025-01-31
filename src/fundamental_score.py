import yfinance as yf
import pandas as pd
import numpy as np

def calculate_fundamental_score(ticker):
    # Fetch data using yfinance
    stock = yf.Ticker(ticker+'.NS')
    
    # Get the financial data
    balance_sheet = stock.balance_sheet
    financials = stock.financials
    cashflow = stock.cashflow
    info = stock.info
    
    # Check if data is available
    if balance_sheet.empty or financials.empty or cashflow.empty:
        print(f"Data not available for {ticker}.")
        return None

    # Calculate key financial metrics
    try:
        # Profitability Ratios
        roe = financials.loc['Net Income'].iloc[0] / balance_sheet.loc['Stockholders Equity'].iloc[0]
        net_profit_margin = financials.loc['Net Income'].iloc[0] / financials.loc['Total Revenue'].iloc[0]

        # Valuation Ratios
        pe_ratio = info.get("trailingPE", np.nan)
        pb_ratio = info.get("priceToBook", np.nan)

        # Debt Ratios
        debt_to_equity = balance_sheet.loc['Current Liabilities'].iloc[0] / balance_sheet.loc['Stockholders Equity'].iloc[0]

        # Efficiency Ratios
        roa = financials.loc['Net Income'].iloc[0] / balance_sheet.loc['Total Assets'].iloc[0]
        asset_turnover = financials.loc['Total Revenue'].iloc[0] / balance_sheet.loc['Total Assets'].iloc[0]

        # Growth Metrics
        revenue_growth = (financials.loc['Total Revenue'].iloc[0] - financials.loc['Total Revenue'].iloc[1]) / financials.loc['Total Revenue'].iloc[1]
        net_income_growth = (financials.loc['Net Income'].iloc[0] - financials.loc['Net Income'].iloc[1]) / financials.loc['Net Income'].iloc[1]

    except KeyError as e:
        print(f"Missing data for calculation: {e}")
        return None

    # Assign scores to each metric based on thresholds
    scores = {
        'ROE': 1 if roe > 0.15 else 0,
        'Net Profit Margin': 1 if net_profit_margin > 0.1 else 0,
        'P/E Ratio': 1 if pe_ratio < 20 else 0,
        'P/B Ratio': 1 if pb_ratio < 3 else 0,
        'Debt-to-Equity': 1 if debt_to_equity < 1 else 0,
        'ROA': 1 if roa > 0.05 else 0,
        'Asset Turnover': 1 if asset_turnover > 0.5 else 0,
        'Revenue Growth': 1 if revenue_growth > 0.05 else 0,
        'Net Income Growth': 1 if net_income_growth > 0.05 else 0
    }
    return_dict = {}

    for metric, score in scores.items():
        return_dict[metric] = '✅' if score else '❌'
        # print(f"{metric}: {'✅' if score else '❌'}")

    return return_dict
