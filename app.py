import plotly.express as px
import streamlit as st

from stock_data import get_stock_history
from news_fetcher import get_company_news


st.set_page_config(page_title="News Sentiment & Stock Dashboard", layout="wide")

st.title("News Sentiment & Stock Dashboard")
st.write("Step 1: show stock data and raw news together before adding sentiment.")

ticker = st.text_input("Enter stock ticker", value="MSFT").upper()
company_name = st.text_input("Enter company name for news search", value="Microsoft")
period = st.selectbox("Choose stock period", ["1mo", "3mo", "6mo", "1y"], index=0)

st.header(f"Stock Data for {ticker}")

try:
    stock_df = get_stock_history(ticker, period)

    st.dataframe(stock_df)

    latest_close = stock_df["Close"].iloc[-1]
    highest_price = stock_df["High"].max()
    lowest_price = stock_df["Low"].min()

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Close", f"{latest_close:.2f}")
    col2.metric("Highest Price", f"{highest_price:.2f}")
    col3.metric("Lowest Price", f"{lowest_price:.2f}")

    fig = px.line(
        stock_df,
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


st.header(f"Latest News for {company_name}")

try:
    articles = get_company_news(company_name, 29)

    st.write(f"Total articles found: {len(articles)}")

    for article in articles:
        st.subheader(article["title"])
        st.write(f"Published At: {article['publishedAt']}")

        if article["description"]:
            st.write(article["description"])

        st.markdown(f"[Read full article]({article['url']})")
        st.markdown("---")

except Exception as error:
    st.error(f"Could not load news: {error}")
