import streamlit as st
import plotly.express as px
from stock_data import get_stock_history


st.set_page_config(page_title="Stock Dashboard", layout="wide") #set the browser tab title anf makes the layout wider

st.title("News Sentiment & Stock Dashboard")
st.write("Explore stock data before adding news and sentiment.") #short description of the dashboard

ticker = st.text_input("Enter a stock ticker", value="MSFT").upper() #gives the user a box to type a ticker liks MSFT or AAPL
period = st.selectbox("Choose a time period", ["1mo", "3mo", "6mo", "1y"], index=0)  # lets the user choose how much history to fetch

try:
    df = get_stock_history(ticker, period) #calls the function

    st.subheader(f"{ticker} Stock Data")
    st.dataframe(df) #displays rat tablein the app

    latest_close = df["Close"].iloc[-1] #gets the latest closing price
    highest_price = df["High"].max()
    lowest_price = df["Low"].min()

    col1, col2, col3 = st.columns(3) #creates three columns 
    col1.metric("Latest Close", f"{latest_close:.2f}")
    col2.metric("Highest Price", f"{highest_price:.2f}")
    col3.metric("Lowest Price", f"{lowest_price:.2f}")

    fig = px.line(
        df,
        x="Date",
        y="Close",
        title=f"{ticker} Closing Price",
        markers=True
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Closing Price"
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as error:
    st.error(f"Could not load stock data: {error}")