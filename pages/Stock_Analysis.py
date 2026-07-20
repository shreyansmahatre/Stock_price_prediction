import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
try:
    import ta
    _ta_import_ok = True
    _ta_import_err = None
except Exception as _e:
    # ta is optional for some pages; handle absence gracefully and show a helpful message later
    ta = None
    _ta_import_ok = False
    _ta_import_err = str(_e)
from pages.utils.plotly_figure import plotly_figure, candlestick, RSI, MACD, close_chart
import sys

import plotly.graph_objects as go

def plotly_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df[col] for col in df.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    return fig

# Debug: show which Python executable is running and whether 'ta' imports correctly.

# Note: calling st.set_page_config is recommended only once at the top-level app
# (e.g., in Trading_App.py). Avoid calling it inside pages to prevent conflicts.

st.title("Stock Analysis")

col1, col2, col3 = st.columns(3)

today = datetime.date.today()

with col1:
    ticker = st.text_input("Stock Ticker", "TSLA")
with col2:
    # Default to roughly one year before today using timedelta to avoid errors
    start_date = st.date_input("Choose Start Date", today - datetime.timedelta(days=365))
with col3:
    end_date = st.date_input("Choose End Date", today)

st.write("Selected:", ticker, start_date, "to", end_date)

st.subheader(ticker)

stock = yf.Ticker(ticker)

st.write(stock.info['longBusinessSummary'])
st.write("**Sector:**", stock.info['sector'])
st.write("**Full Time Employees:**", stock.info['fullTimeEmployees'])
st.write("**Website:**", stock.info['website'])

col1, col2 = st.columns(2)
    
with col1:
    df= pd.DataFrame(index = ['Market Cap','Beta','EPS','PE Ratio'])
    df[''] = [stock.info['marketCap'], stock.info['beta'], stock.info['trailingEps'], stock.info['trailingPE']]
    fig_df = plotly_figure(df)
    st.plotly_chart(fig_df, use_container_width=True)
with col2:
    df = pd.DataFrame(index = ['Quick Ratio', 'Revenue per Share', 'Profit Margins','Debt to Equity', 'Return on Equity']) 
    df[''] = [stock.info.get('quickRatio', np.nan), stock.info.get('revenuePerShare', np.nan), stock.info.get('profitMargins', np.nan), stock.info.get('debtToEquity', np.nan), stock.info.get('returnOnEquity', np.nan)]
    fig_df = plotly_figure(df)  
    st.plotly_chart(fig_df, use_container_width=True)

data = yf.download(ticker, start=start_date, end=end_date)

col1 , col2 , col3 = st.columns(3)
daily_change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
col1.metric("Daily change", str(round(data['Close'].iloc[-1],2)), str(round(daily_change,2)))

last_10_df = data.tail(10).sort_index(ascending=False).round(3)
fig_df = plotly_table(last_10_df)

st.write('#### Historical Data (last 10 rows)')
st.plotly_chart(fig_df, use_container_width=True)

col1, col2, col3, col4, col5, col6, col7= st.columns([1,1,1,1,1,1,1])

num_period = ''
with col1:
    if st.button('5D'):
        num_period = '5D'
with col2:
    if st.button('1M'):
        num_period = '1M'
with col3:
    if st.button('6M'):
        num_period = '6M'
with col4:
    if st.button('YTD'):
        num_period = 'YTD'
with col5:
    if st.button('1Y'):
        num_period = '1Y'
with col6:
    if st.button('5Y'):
        num_period = '5Y'
with col7:
    if st.button('MAX'):
        num_period = 'MAX'
        
col1, col2, col3 = st.columns(3) 
with col1:
    chart_type = st.selectbox('',('Candle', 'Line'))
with col2:
    if chart_type == 'Candle':
        indicators = st.selectbox('',('RSI','MACD'))
    else:
        indicators = st.selectbox('',('RSI','Moving Average','MACD'))
        
ticker_ = yf.Ticker(ticker)
new_df1 = ticker_.history(period= 'max')
data1 = ticker_.history(period = 'max')
if num_period == '':
    if chart_type == 'Candle' and indicators == 'RSI':
        st.plotly_chart(candlestick(data1, '1y'),use_container_width=True)
        st.plotly_chart(RSI(data1, '1y'), use_container_width=True)
    
    if chart_type == 'Candle' and indicators == 'MACD':
        st.plotly_chart(candlestick(data1, '1y'), use_container_width=True)
        st.plotly_chart(MACD(data1, '1y'), use_container_width=True)
        
    if chart_type == 'Line' and indicators == 'RSI':
        st.plotly_chart(close_chart(data1, '1y'), use_container_width=True)
        st.plotly_chart(RSI(data1, '1y'), use_container_width=True)
        
    if chart_type == 'Line' and indicators == 'MACD':
        st.plotly_chart(close_chart(data1, '1y'), use_container_width=True)
        st.plotly_chart(MACD(data1, '1y'), use_container_width=True)
        
else:
    if chart_type == 'Candle' and indicators == 'RSI':
        st.plotly_chart(candlestick(data1, num_period), use_container_width=True)
        st.plotly_chart(RSI(data1, num_period), use_container_width=True)
    
    if chart_type == 'Candle' and indicators == 'MACD':
        st.plotly_chart(candlestick(data1, num_period), use_container_width=True)
        st.plotly_chart(MACD(data1, num_period), use_container_width=True)
        
    if chart_type == 'Line' and indicators == 'RSI':
        st.plotly_chart(close_chart(data1, num_period), use_container_width=True)
        st.plotly_chart(RSI(data1, num_period), use_container_width=True)
        
    if chart_type == 'Line' and indicators == 'MACD':
        st.plotly_chart(close_chart(data1, num_period), use_container_width=True)
        st.plotly_chart(MACD(data1, num_period), use_container_width=True)        
