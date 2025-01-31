
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import date
from src.fundamental_score import calculate_fundamental_score
from src.scores import calculate_stock_score
from src.get_data_for_scoring_yfinance import get_data
st.sidebar.title("Navigation")
menu_option = st.sidebar.selectbox("Select a section", ['Fundamental Score'])

if menu_option == 'Fundamental Score':
    st.title("Fundamental Score")
    query = st.text_input('Enter Stock Symbol')
    fundamental_details = calculate_fundamental_score(ticker=query)
    st.write(f'Fundamental Details of Stock: {query}')
    st.write(fundamental_details)
    metrics = get_data(stock_symbol=query+'.NS')
    score =  calculate_stock_score(metrics=metrics)
    
    text = f"Overall score of {query} is: {round(score, 2)}"

    st.header(f'{text}')
    st.write(f' NOTE: A score greater than or equal to 0.5 indicates a favorable buying opportunity 📈')
    st.write(f' NOTE: A score less than 0.5 indicates a favorable selling opportunity 📉')
