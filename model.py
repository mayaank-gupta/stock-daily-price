import yfinance as yf
import pandas as pd
import numpy as np

def get_stock_data(ticker, start_date, end_date):
    return yf.download(ticker, start=start_date, end=end_date, interval="1d")

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

def find_stocks_with_volume_trend(tickers, start_date, end_date):
    results = []
    for ticker in tickers:
        analysis = analyze_trend_volumes(ticker, start_date, end_date)
        if analysis:
            results.append(analysis)
    
    return [result for result in results if result['higher_volume_uptrend']]

# Example usage
tickers = ["MGL.NS", "STARHEALTH.NS", "APOLLOTYRE.NS", "IGL.NS", "DELHIVERY.NS", "RKEC.NS"]
start_date = "2022-01-01"
end_date = "2024-06-30"

stocks_with_volume_trend = find_stocks_with_volume_trend(tickers, start_date, end_date)

# Display the results
for stock in stocks_with_volume_trend:
    print(f"{stock['ticker']} has higher average volumes on uptrend days and lower on downtrend days.")
    print(f"Average Volume on Uptrend Days: {stock['avg_volume_uptrend']}")
    print(f"Average Volume on Downtrend Days: {stock['avg_volume_downtrend']}")
    print(f"Percentage Higher Volume on Uptrend Days: {stock['percentage_higher']:.2f}%\n")
