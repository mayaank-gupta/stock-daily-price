import numpy as np
import yfinance as yf

import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default='svg'
TICKER = 'IRFC.NS'
BEST_FIT_LENGTH = 25
PLOT_LENGTH = 75

def best_fit(y: np.array):
    '''
    Find the line of best fit gradient and intercept parameters via simple
    Linear Regression
    Parameters
    ----------
    y : np.array
        The time-series to find the linear regression line for
    Returns
    -------
    [m, c] : floats
        The gradient and intercept parameters, respectively
    '''
    
    x = np.arange(0, y.shape[0])
    
    x_bar = np.mean(x)
    y_bar = np.mean(y)
    
    m = np.sum((x-x_bar)*(y-y_bar))/np.sum((x-x_bar)**2)
    c = y_bar - m*x_bar
    
    return m, c
    
if __name__ == '__main__':
    
    df = yf.download(TICKER).reset_index()
    
    m_high, c_high = best_fit(df['High'].values[-BEST_FIT_LENGTH:])
    m_low, c_low = best_fit(df['Low'].values[-BEST_FIT_LENGTH:])
    
    df = df[-PLOT_LENGTH:]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Candlestick(
            x = df['Date'],
            open = df['Open'],
            high = df['High'],
            low = df['Low'],
            close = df['Close'],
            showlegend = False
        )
    )
    
    fig.add_trace(
        go.Line(
            x = df['Date'][-BEST_FIT_LENGTH:],
            y = m_high*np.arange(0, BEST_FIT_LENGTH) + c_high,
            name = 'High price trend line',
            line = {'color': 'rgba(163, 12, 187, 1)'},
        )    
    )
    
    fig.add_trace(
        go.Line(
            x = df['Date'][-BEST_FIT_LENGTH:],
            y = m_low*np.arange(0, BEST_FIT_LENGTH) + c_low,
            name = 'Low price trend line',
            line = {'color': 'rgba(61, 12, 187, 1)'},
        )    
    )
    
    fig.update_xaxes(
        rangebreaks = [{'bounds': ['sat', 'mon']}],
        rangeslider_visible = False,
    )
    
    fig.update_layout(
        yaxis = {'title': 'Price ($)'},
        xaxis = {'title': 'Date'},
        legend = {'x': 0, 'y': -0.1, 'orientation': 'h'},
        margin = {'l': 50, 'r': 50, 'b': 50, 't': 25},
        title = f'{TICKER} Price Chart',
        width = 800,
        height = 800,
    )
    fig.show()