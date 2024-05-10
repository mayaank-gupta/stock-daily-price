import yfinance as yf

# Define the ticker symbol for BANKNIFTY
ticker_symbol = "^NSEBANK"

# Set the start and end dates for historical data
start_date = "2022-01-05"
end_date = "2024-05-05"

# Fetch historical data
historical_data = yf.download(ticker_symbol,
                              start=start_date,
                              end=end_date,
                              interval="1wk")

# Calculate the average of open and close prices
historical_data['Average_Open_Close'] = (historical_data['Open'] +
                                         historical_data['Close']) / 2

historical_data['Difference'] = (historical_data['Open'] +
                                         historical_data['Close']) / 2

# Calculate the difference between open and close prices
historical_data['Open_Close_Difference'] = (historical_data[
    'Open'] - historical_data['Close']).abs()

# Display the result
print(historical_data[[
    'Open', 'Close', 'Average_Open_Close', 'Open_Close_Difference'
]])


# Calculate the average of the difference between open and close prices
average_difference = historical_data['Open_Close_Difference'].mean()
# Assuming historical_data is your DataFrame

# Count occurrences where the difference is more than 1000
count_difference_gt_1000 = (historical_data['Open_Close_Difference'] > 1600).sum()

# Display the count
print("Number of times the difference is more than 1000:", count_difference_gt_1000)


# Display the correct result
print(f'Average Open-Close Difference: {average_difference:.2f}')

