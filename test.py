import yfinance as yf

def analyze_stock_data(ticker_symbol, start_date="2021-01-01", end_date="2024-05-31"):
    # Fetch historical data
    historical_data = yf.download(ticker_symbol, start=start_date, end=end_date, interval="1d")
    
    # Check if data is fetched successfully
    if historical_data.empty:
        print("No data fetched for the given ticker symbol.")
        return
    
    # Calculate the average of open and close prices
    historical_data['Average_Open_Close'] = (historical_data['Open'] + historical_data['Close']) / 2
    
    # Calculate the difference between open and close prices
    historical_data['Open_Close_Difference'] = (historical_data['Open'] - historical_data['Close']).abs()
    
    # Calculate the average of the difference between open and close prices
    average_difference = historical_data['Open_Close_Difference'].mean()
    
    # Count occurrences where the difference is more than 1500
    count_difference_gt_1500 = (historical_data['Open_Close_Difference'] > 1500).sum()
    
    # Return the computed values
    return {
        'average_difference': average_difference
    }

# Example usage
ticker_symbol = "DELHIVERY.NS"
result = analyze_stock_data(ticker_symbol)

# Print the result
print(result)
