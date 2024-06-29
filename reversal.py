import yfinance as yf
import pandas as pd
import numpy as np
from collections import defaultdict

def get_stock_data(ticker, start_date, end_date):
    """Fetch historical data from Yahoo Finance."""
    data = yf.download(ticker, start=start_date, end=end_date, interval="1d")
    data['Date'] = data.index
    data.reset_index(drop=True, inplace=True)
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

def find_reversal_ranges(reversal_levels, range_width):
    """Find price ranges where reversals happen multiple times."""
    range_dict = defaultdict(int)
    
    for price, count in reversal_levels:
        if count > 1:  # We're only interested in prices where reversals happen more than once
            lower_bound = int(price // range_width * range_width)
            upper_bound = lower_bound + range_width
            range_key = f"{lower_bound}-{upper_bound}"
            range_dict[range_key] += count
    
    # Sort ranges by count
    sorted_ranges = sorted(range_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_ranges

def analyze_stock_reversals(ticker, start_date, end_date, tolerance_percentage, range_width):
    """Fetch data and find reversal levels for a given stock."""
    data = get_stock_data(ticker, start_date, end_date)
    reversal_levels = find_reversal_points(data, tolerance_percentage)
    reversal_ranges = find_reversal_ranges(reversal_levels, range_width)
    return reversal_ranges

# Example usage with multiple tickers and a specified percentage tolerance
tickers = ["MGL.NS"]
start_date = "2024-01-01"
end_date = "2024-06-30"
tolerance_percentage = 2  # Define your tolerance level (in percentage)
range_width = 50  # Define the width of the price range to check for reversals

for ticker in tickers:
    reversal_ranges = analyze_stock_reversals(ticker, start_date, end_date, tolerance_percentage, range_width)
    print(f"\nReversal Ranges for {ticker} with a tolerance of {tolerance_percentage}% and range width of {range_width}:")
    for price_range, count in reversal_ranges:
        print(f"Price Range: {price_range}, Count: {count}")
