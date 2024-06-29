from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

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

def analyze_stock_reversals(ticker, start_date, end_date, tolerance_percentage, num_reversals=3):
    """Fetch data and find potential support or reversal points for a given stock."""
    data = get_stock_data(ticker, start_date, end_date)
    reversal_levels = find_reversal_points(data, tolerance_percentage)
    highest_count_reversals = reversal_levels[:num_reversals]
    data_with_sma = calculate_recent_sma(data)
    return highest_count_reversals, data_with_sma

@app.route('/api/reversal', methods=['GET'])
def get_reversal_points():
    ticker = request.args.get('ticker')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    tolerance_percentage = float(request.args.get('tolerance_percentage', 3.0))
    num_reversals = int(request.args.get('num_reversals', 3))

    try:
        reversal_points, sma_values = analyze_stock_reversals(ticker, start_date, end_date, tolerance_percentage, num_reversals)
        response = {
            'ticker': ticker,
            'reversal_points': reversal_points,
            '20SMA': sma_values['20SMA'],
            '50SMA': sma_values['50SMA'],
            '200SMA': sma_values['200SMA']
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 400