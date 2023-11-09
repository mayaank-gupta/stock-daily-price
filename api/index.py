from flask import Flask, request, jsonify
import yfinance as yf
import datetime

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, world!'

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Check if the 'symbols' key exists in the JSON data
        if 'symbols' not in data:
            return jsonify({'error': 'Missing key "symbols" in JSON data'}), 400

        # Retrieve the array of stock symbols from the JSON data
        symbols = data['symbols']
        date = data.get('date', None)

        # Fetch data from Yahoo Finance for each symbol
        stock_data = {}
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                third_trading_day = None
                sixth_trading_day = None
                next_day = None

                if date:
                    start_date = datetime.datetime.strptime(date, "%Y-%m-%d")
                    end_date = start_date + datetime.timedelta(days=15)
                    data = stock.history(start=date, end=end_date)
                    lastest_data = stock.history(period="1d")

                    if len(data) >= 2:
                        next_day = data.iloc[1]

                    if len(data) >= 3:
                        third_trading_day = data.iloc[2]  # 0-based indexing, so 2 means the 3rd trading day

                    if len(data) >= 6:
                        sixth_trading_day = data.iloc[5]
                else:
                    data = stock.history(period="1d")
                close_price = data['Close'].values[0] if not data.empty else None
                open_price = data['Open'].values[0] if not data.empty else None
                day_change = data['Close'].values[0] - data['Open'].values[0] if not data.empty else None
                day_change_percentage = (day_change / data['Open'].values[0]) * 100 if not data.empty else None
                modified_string  = symbol.replace(".NS", "")
                if date:
                    latest_price = lastest_data['Close'].values[0] if not data.empty else None
                    third_day_close = third_trading_day['Close'] if third_trading_day is not None else None
                    sixth_trading_day = sixth_trading_day['Close'] if sixth_trading_day is not None else None
                    next_day = next_day['Close'] if sixth_trading_day is not None else None
                    stock_data[modified_string] = {
                        'date_price': "{:.2f}".format(close_price),
                        'latest_price': "{:.2f}".format(latest_price),
                        'change_percentage': "{:.2f}".format(((latest_price - close_price)/close_price) * 100),
                        'next_day': "{:.2f}".format(next_day) if next_day is not None else None,
                        'third_trading_day': "{:.2f}".format(third_day_close) if third_day_close is not None else None,
                        'sixth_trading_day': "{:.2f}".format(sixth_trading_day) if sixth_trading_day is not None else None,
                    }
                    # Calculate percentage change for 'third_trading_day' if it's not None
                    if stock_data[modified_string]['third_trading_day'] is not None:
                        stock_data[modified_string]['third_day_change_percentage'] = "{:.2f}".format(
                            ((third_day_close - close_price) / close_price) * 100
                        )

                    # Calculate percentage change for 'sixth_trading_day' if it's not None
                    if stock_data[modified_string]['sixth_trading_day'] is not None:
                        stock_data[modified_string]['sixth_day_change_percentage'] = "{:.2f}".format(
                            ((sixth_trading_day - close_price) / close_price) * 100
                        )
                else:
                    stock_data[modified_string] = {
                    'open': "{:.2f}".format(open_price),
                    'close': "{:.2f}".format(close_price),
                    'day_change_percentage': "{:.2f}".format(day_change_percentage)
                    }
            except Exception as e:
                stock_data[symbol] = {'error': str(e)}

        return jsonify(stock_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)