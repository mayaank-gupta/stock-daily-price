import yfinance as yf
import pandas as pd
import numpy as np

def classify_trend(row):
    if row['Close'] > row['Open']:
        return 'uptrend'
    elif row['Close'] < row['Open']:
        return 'downtrend'
    else:
        return 'no_trend'

def analyze_trend_volumes(ticker, start_date, end_date):
    data = get_stock_data(ticker, start_date, end_date)
    
    if data.empty:
        print(f"No data fetched for {ticker}.")
        return None
    
    data['Trend'] = data.apply(classify_trend, axis=1)
    
    uptrend_days = data[data['Trend'] == 'uptrend']
    downtrend_days = data[data['Trend'] == 'downtrend']
    
    avg_volume_uptrend = uptrend_days['Volume'].mean()
    avg_volume_downtrend = downtrend_days['Volume'].mean()
    
    if avg_volume_downtrend > 0:
        percentage_higher = ((avg_volume_uptrend - avg_volume_downtrend) / avg_volume_downtrend) * 100
    else:
        percentage_higher = np.inf
    
    return {
        'ticker': ticker,
        'avg_volume_uptrend': avg_volume_uptrend,
        'avg_volume_downtrend': avg_volume_downtrend,
        'uptrend_volumes': uptrend_days['Volume'].tolist(),
        'downtrend_volumes': downtrend_days['Volume'].tolist(),
        'higher_volume_uptrend': avg_volume_uptrend > avg_volume_downtrend,
        'percentage_higher': percentage_higher
    }

def find_stocks_with_volume_trend(ticker, start_date, end_date):
    analysis = analyze_trend_volumes(ticker, start_date, end_date)
    if analysis:
        return analysis
    return

def get_stock_data(ticker, start_date, end_date):
    """Fetch historical data from Yahoo Finance."""
    data = yf.download(ticker, start=start_date, end=end_date, interval="1d")
    return data

def find_reversal_points(data, tolerance_percentage):
    """Find potential reversal points in the historical data."""
    lows = data['Low']
    reversals = {}

    for i in range(1, len(lows) - 1):
        if lows[i] < lows[i - 1] and lows[i] < lows[i + 1]:
            reversal_point = lows[i]
            if reversal_point in reversals:
                reversals[reversal_point] += 1
            else:
                reversals[reversal_point] = 1

    # Sort reversals by count
    sorted_reversals = sorted(reversals.items(), key=lambda x: x[1], reverse=True)

    # Consolidate nearby reversal points based on percentage tolerance
    consolidated_reversals = []
    for price, count in sorted_reversals:
        found = False
        for idx in range(len(consolidated_reversals)):
            consolidated_price, consolidated_count = consolidated_reversals[idx]
            if abs(consolidated_price - price) <= (tolerance_percentage / 100) * price:
                # Update the consolidated price and count
                new_price = (consolidated_price * consolidated_count + price * count) / (consolidated_count + count)
                consolidated_reversals[idx] = (new_price, consolidated_count + count)
                found = True
                break
        if not found:
            consolidated_reversals.append((price, count))

    return sorted(consolidated_reversals, key=lambda x: x[1], reverse=True)

def calculate_recent_sma(data):
    """Calculate recent 20, 50, and 200 Simple Moving Averages (SMA)."""
    data['20SMA'] = data['Close'].rolling(window=20, min_periods=1).mean()
    data['50SMA'] = data['Close'].rolling(window=50, min_periods=1).mean()
    data['200SMA'] = data['Close'].rolling(window=200, min_periods=1).mean()
    return data[['Close', '20SMA', '50SMA', '200SMA']].iloc[-1].to_dict()  # Return only the most recent values as dictionary

def analyze_stock_reversals(ticker, start_date, current_date, tolerance_percentage, num_reversals=3):
    """Fetch data and find potential support or reversal points for a given stock."""
    data = get_stock_data(ticker, start_date, current_date)
    reversal_levels = find_reversal_points(data, tolerance_percentage)
    highest_count_reversals = reversal_levels[:num_reversals]
    data_with_sma = calculate_recent_sma(data)
    return highest_count_reversals, data_with_sma