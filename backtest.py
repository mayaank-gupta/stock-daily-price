import yfinance as yf
import pandas as pd

def backtest(stock_symbols, start_date, end_date, stop_loss_percent, target_percent, trailing_percent):
    results = {}

    for symbol in stock_symbols:
        # Fetch historical data for the stock
        data = yf.download(symbol, start=start_date, end=end_date)
        # Initialize variables for tracking positions
        position_opened = False
        entry_price = 0
        stop_loss_percent = 15
        target_percent = 10
        trailing_percent = 10
        stop_loss_price = 0
        target_price = 0
        trailed_stop_loss_price = 0
        trailed_target_price = 0
        highest_close_after_entry = 0

        # Iterate through historical data
        for i in range(1, len(data)):
            current_close = data['Close'][i]
            previous_close = data['Close'][i - 1]

            if not position_opened:
                # Check if the current day meets the entry conditions
                # For example, entering if the close price increases by a certain percentage
                if current_close > previous_close * 1.01:
                    entry_price = current_close
                    stop_loss_price = entry_price * (1 - stop_loss_percent / 100)
                    target_price = entry_price * (1 + target_percent / 100)
                    trailed_stop_loss_price = stop_loss_price
                    trailed_target_price = target_price
                    highest_close_after_entry = current_close
                    position_opened = True
            else:
                # Update the highest close price after entry
                highest_close_after_entry = max(highest_close_after_entry, current_close)

                # Check if the stop loss or target is hit
                if current_close <= stop_loss_price or current_close >= target_price:
                    position_opened = False
                    result = {
                        'entry_date': str(data.index[i]),
                        'entry_price': entry_price,
                        'exit_date': str(data.index[i]),
                        'exit_price': current_close,
                        'result': 'Stop Loss Hit' if current_close <= stop_loss_price else 'Open',
                        'profit': current_close - entry_price,
                        'trailed_stop_loss': trailed_stop_loss_price,
                        'trailed_target': trailed_target_price
                    }
                    
                    # If the target is hit, adjust stop-loss and target based on trailing percent
                    if current_close >= target_price:
                        stop_loss_percent += trailing_percent
                        target_percent += trailing_percent
                    
                    results[symbol] = result
                    break

                # Adjust stop-loss based on trailing highest close
                stop_loss_price = highest_close_after_entry * (1 - stop_loss_percent / 100)
                # Adjust trailed stop-loss and target
                trailed_stop_loss_price = highest_close_after_entry * (1 - stop_loss_percent / 100)
                trailed_target_price = highest_close_after_entry * (1 + target_percent / 100)

    return results

# Example usage
stock_symbols = ['ASIANHOTNR.NS', 'TRENT.NS','MANGLMCEM.NS','HIRECT.NS','TEXINFRA.NS','MODISONLTD.NS','IVP.NS','CDSL.NS','APOLLO.NS','SUNDARMHLD.NS'
,'MADHUCON.NS','KDDL.NS','MBLINFRA.NS','OBEROIRLTY.NS','SPYL.NS','MCX.NS','SIGACHI.NS','ANANDRATHI.NS','GREENLAM.NS','ALKEM.NS']  # Add your list of stock symbols
start_date = '2023-10-30'
end_date = '2023-12-12'
stop_loss_percent = 15
target_percent = 10
trailing_percent = 10

backtest_results = backtest(stock_symbols, start_date, end_date, stop_loss_percent, target_percent, trailing_percent)
print(backtest_results)
