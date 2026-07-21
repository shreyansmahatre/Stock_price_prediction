import plotly.graph_objects as go
import dateutil.relativedelta
import datetime
import pandas as pd
import numpy as np
import pandas_ta as pta

def plotly_table(dataframe):
    header_color = 'gray'
    rowEvenColor = '#f8fafd'
    rowOddColor = '#e1efff'
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b><b>"] + ["<b>" + str(i)[:10] + "</b>" for i in dataframe.columns],
            line_color='#0078ff', fill_color='#0078ff',
            align='center', font=dict(color='white', size=15), height=35,
        ),
        cells=dict(
            values=[["<b>" + str(i) + "<b>" for i in dataframe.index]] + [dataframe[i].tolist() for i in dataframe.columns],
            fill_color=[[rowOddColor, rowEvenColor] * (len(dataframe) // 2 + 1) for _ in range(len(dataframe.columns) + 1)],
            align='left', line_color=['white'], font=dict(color=['black'], size=15), height=35
        )
    )])
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
    return fig


# --- 2. DATA FILTERING LOGIC ---
def filter_data(dataframe: pd.DataFrame, num_period: str) -> pd.DataFrame:
    df = dataframe.copy()
    end_date = df.index.max()

    if num_period == '1mo':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(months=-1)
    elif num_period == '5d':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(days=-5)
    elif num_period == '6mo':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(months=-6)
    elif num_period == '1y':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(years=-1)
    elif num_period == '5y':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(years=-5)
    elif num_period == 'ytd':
        date = datetime.datetime(dataframe.index[-1].year, 1, 1).strftime('%Y-%m-%d')
    else:
        date = dataframe.index[0]  # Default to all data if unrecognized period

    return dataframe.reset_index()[dataframe.reset_index()['Date'] >= date]

# --- 3. BASIC LINE CHART ---
def close_chart(dataframe: pd.DataFrame, num_period = False):
    if num_period:
        dataframe = filter_data(dataframe, num_period)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Open'], mode='lines', name='Open', line=dict(width=2, color='blue')))
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Close'], mode='lines', name='Close', line=dict(width=2, color='red')))
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['High'], mode='lines', name='High', line=dict(width=2, color='green')))
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Low'], mode='lines', name='Low', line=dict(width=2, color='orange')))
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0, r=20, t=20, b=0), plot_bgcolor='white', paper_bgcolor='#e1efff',legend=dict(
    yanchor = "top",
    xanchor = "right"
    ))
    return fig

# --- 4. CANDLESTICK CHART ---
def candlestick(dataframe, num_period):
    dataframe = filter_data(dataframe, num_period)
    fig= go.Figure()

    fig.add_trace(go.Candlestick(x=dataframe['Date'],
                                 open=dataframe['Open'], high=dataframe['High'],
                                 low=dataframe['Low'], close=dataframe['Close']))
                                 
    fig.update_layout(showlegend=False, height=500, margin=dict(l=0, r=20, t=20, b=0),
                      plot_bgcolor='white', paper_bgcolor='#e1efff')
    return fig

# --- 5. RSI CHART ---
def RSI(dataframe, num_period):
    dataframe['RSI'] = pta.rsi(dataframe['Close'])
    dataframe = filter_data(dataframe, num_period)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dataframe['Date'],
        y=dataframe.RSI, name= 'RSI', marker_color='orange',line= dict(width=2,color = 'orange'),
    ))
    fig.add_trace(go.Scatter(
        x=dataframe['Date'],
        y= [70]*len(dataframe), name='overbought', marker_color='red', line=dict(width=2, color='red', dash='dash'))
    )
    fig.add_trace(go.Scatter(
        x=dataframe['Date'],
        y= [30]*len(dataframe), name='oversold', marker_color='green', line=dict(width=2, color='green', dash='dash'))
    )
    
    fig.update_layout(yaxis_range=[0,100],
        height=200, plot_bgcolor='white', paper_bgcolor='#e1efff', margin=dict(l=0, r=0, t=0, b=0 ),legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="right", x=1)       
                      )
    return fig

# --- 6. MOVING AVERAGE CHART ---
def Moving_average(dataframe, num_period):
    dataframe['SMA_50']= pta.sma(dataframe['Close'],50)
    dataframe = filter_data(dataframe, num_period)
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Open'], mode='lines', name='Open', line=dict(width=2, color='blue')))
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Close'], mode='lines', name='Close', line=dict(width=2, color='red')))
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['High'], mode='lines', name='High', line=dict(width=2, color='green')))
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Low'], mode='lines', name='Low', line=dict(width=2, color='orange')))
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['SMA_50'], mode='lines', name='SMA 50', line=dict(width=2, color='purple')))

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0, r=20, t=20, b=0), plot_bgcolor='white', paper_bgcolor='#e1efff')
    return fig

# --- 7. MACD CHART ---
def MACD(dataframe, num_period):
    macd_df = pta.macd(dataframe['Close'])
    dataframe['MACD'] = macd_df.iloc[:, 0]
    dataframe['MACD_Hist'] = macd_df.iloc[:, 1]
    dataframe['MACD_Signal'] = macd_df.iloc[:, 2]
    dataframe = filter_data(dataframe, num_period)
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dataframe['Date'],
        y=dataframe['MACD'], name= 'RSI', marker_color='orange',line= dict(width=2,color = 'orange'),
    ))
    fig.add_trace(go.Scatter(
        x=dataframe['Date'],
        y=dataframe['MACD_Signal'], name='Overbought', marker_color='red', line=dict(width=2, color='blue', dash='dash'))              
    )
    fig.update_layout(
        height=300, plot_bgcolor='white', paper_bgcolor='#e1efff', margin=dict(l=0, r=0, t=0, b=0 ),legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="right", x=1)
    )
    return fig

def Moving_average_forcast(forecast):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=forecast.index[:-30], y=forecast['Close'].iloc[:-30], mode='lines', name='Close price ', line=dict(width=2, color='black')))
    fig.add_trace(go.Scatter(x=forecast.index[-31:], y=forecast['Close'].iloc[-31:], mode='lines', name='Forecasted Close price ', line=dict(width=2, color='red')))
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(
        height=500, plot_bgcolor='white', paper_bgcolor='#e1efff', margin=dict(l=0, r=20, t=20, b=0),legend=dict(
        yanchor = "top",
        xanchor = "right"
        )
    )
    return fig


# Compatibility alias expected by older imports
def plotly_figure(dataframe: pd.DataFrame) -> go.Figure:
    """Alias for `plotly_table` to keep backwards compatibility."""
    return plotly_table(dataframe)




