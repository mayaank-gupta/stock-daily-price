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

def find_highest_count_reversal(reversal_levels):
    """Find the highest count reversal point."""
    if reversal_levels:
        return reversal_levels[0]  # Return the reversal point with the highest count
    else:
        return None

def analyze_stock_reversals(ticker, start_date, end_date, tolerance_percentage):
    """Fetch data and find potential support or reversal points for a given stock."""
    data = get_stock_data(ticker, start_date, end_date)
    reversal_levels = find_reversal_points(data, tolerance_percentage)
    highest_count_reversal = find_highest_count_reversal(reversal_levels)
    return highest_count_reversal

# Example usage with a single ticker and a specified percentage tolerance
ticker = "TCS.NS"
start_date = "2024-01-01"
end_date = "2024-05-31"
tolerance_percentage = 5  # Define your tolerance level (in percentage)

highest_count_reversal = analyze_stock_reversals(ticker, start_date, end_date, tolerance_percentage)

if highest_count_reversal:
    price, count = highest_count_reversal
    print(f"\nThe highest count reversal point for {ticker} with a tolerance of {tolerance_percentage}%:")
    print(f"Price: {price:.2f}, Count: {count}")
else:
    print(f"No significant reversal points found for {ticker} within the specified tolerance.")
