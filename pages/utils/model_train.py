import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import numpy as np
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import pandas as pd

def get_data(ticker):
    stock_data = yf.download(ticker, start='2024-01-01')
    # If download failed or returned no data, return an empty DataFrame
    if stock_data is None or stock_data.empty:
        return pd.DataFrame(columns=['Close'])
    # yfinance returns MultiIndex columns (e.g. ('Close', 'TSLA')); flatten
    # so downstream concat/union with plain-Index frames doesn't break.
    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data.columns = stock_data.columns.get_level_values(0)
    return stock_data[['Close']]

def stationary_check(close_prices):
    # Ensure we work with a 1-D numpy array and handle empty inputs
    arr = np.asarray(close_prices).ravel()
    if arr.size == 0:
        # Return non-stationary p-value so calling code can handle it
        return 1.0
    # If the series is constant, adfuller will raise — treat as non-stationary
    if np.max(arr) == np.min(arr):
        return 1.0
    try:
        adf_test = adfuller(arr)
        p_value = round(adf_test[1], 3)
    except Exception:
        # On any failure, conservatively return non-stationary p-value
        p_value = 1.0
    return p_value

def get_rolling_mean(close_price):
    rolling_mean = close_price.rolling(window=7).mean().dropna()
    return rolling_mean

def get_differencing_order(close_price):
    # If input is empty, no differencing can be computed
    if close_price is None or len(close_price) == 0:
        return 0
    p_value = stationary_check(close_price)
    d = 0
    # limit maximum differencing to avoid infinite loops on bad input
    max_diff = 5
    while p_value > 0.05 and d < max_diff:
        d += 1
        close_price = close_price.diff().dropna()
        if len(close_price) == 0:
            break
        p_value = stationary_check(close_price)
    return d

def fit_model(data, differencing_order):
    # ARIMA requires enough observations; validate input length
    arr = np.asarray(data).ravel()
    if arr.size < 10:
        # Not enough data to fit a sensible ARIMA model; return zeros
        return np.zeros(30)
    model = ARIMA(data, order=(30, differencing_order, 30))
    model_fit = model.fit()
    
    forecast_steps = 30
    # Use get_forecast which returns a PredictionResults object with .predicted_mean
    try:
        forecast_res = model_fit.get_forecast(steps=forecast_steps)
        pred = forecast_res.predicted_mean
    except Exception:
        # Older/newer statsmodels may return a simple Series/ndarray from forecast()
        forecast = model_fit.forecast(steps=forecast_steps)
        pred = forecast

    # Ensure we return a 1-D numpy array for downstream metrics
    try:
        predictions = np.asarray(pred).ravel()
    except Exception:
        predictions = np.array(pred)

    return predictions

def evaluate_model(original_price, differencing_order):
    train_data, test_data = original_price[:-30], original_price[-30:]
    predictions = fit_model(train_data, differencing_order)
    rmse = np.sqrt(mean_squared_error(test_data, predictions))
    return round(rmse, 2)

def scaling(close_price):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(np.array(close_price).reshape(-1, 1))
    return scaled_data, scaler

def get_forecast(original_price, differencing_order):
    predictions = fit_model(original_price, differencing_order)
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=29)).strftime('%Y-%m-%d')
    forecast_index = pd.date_range(start=start_date, end=end_date, freq='D')
    forecast_df = pd.DataFrame(predictions, index=forecast_index, columns=['Close'])
    return forecast_df

def inverse_scaling(scaler, scaled_data):
    close_price = scaler.inverse_transform(np.array(scaled_data).reshape(-1, 1))
    return close_price
