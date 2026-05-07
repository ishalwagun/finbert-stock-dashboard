import pandas as pd
import yfinance as yf

def get_stock_history(ticker= "MSFT", period="1mon"):
    stock= yf.Ticker(ticker)
    df= stock.history(period=period)


    if df.empty:
        raise ValueError(f"No stock data found for ticker '{ticker}'.")
    

    return df.reset_index() #sends the stock data back 


if __name__ == "__main__":
    df= get_stock_history("MSFT", "1mo")
    print(df.to_string())