from flask import Flask, request, jsonify
import yfinance as yf

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

        # Fetch data from Yahoo Finance for each symbol
        stock_data = {}
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                data = stock.history(period="1d")  # You can adjust the period as needed
                close_price = data['Close'].values[0] if not data.empty else None
                modified_string  = symbol.replace(".NS", "")
                stock_data[modified_string] = "{:.2f}".format(close_price)
            except Exception as e:
                stock_data[symbol] = {'error': str(e)}

        return jsonify(stock_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)