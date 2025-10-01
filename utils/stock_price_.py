import yfinance as yf


def get_price(ticker):
    ticker = yf.Ticker(ticker)
    price = ticker.history(period="1d")["Close"].iloc[-1]
    return price
