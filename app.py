import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from stock_data import get_stock_history
from news_fetcher import get_company_news
from sentiment_analyser import analyse_sentiment


st.set_page_config(page_title="News Sentiment & Stock Dashboard", layout="wide")
st.title("News Sentiment & Stock Dashboard")



#  Streamlit secrets + .env fallback

# When deployed on Streamlit Cloud, there is no .env file.
# Instead, secrets are stored in the Streamlit dashboard and accessed via st.secrets.
# Locally we fall back to .env so development still works normally.
def get_news_api_key():
    try:
        return st.secrets["NEWS_API_KEY"]
    except Exception:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("NEWS_API_KEY")

NEWS_API_KEY = get_news_api_key()



# INPUTS

# Multi-ticker: user can type "MSFT, AAPL, TSLA" separated by commas.
# We always do the full sentiment analysis on the FIRST ticker only,
# because NewsAPI is searched by company name, not by ticker symbol.
ticker_input = st.text_input(
    "Enter stock ticker(s) - comma-separated to compare (e.g. MSFT, AAPL)",
    value="MSFT"
)
tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
primary_ticker = tickers[0]  # full analysis always runs on the first one

company_name = st.text_input("Company name for news search", value="Microsoft")
period = st.selectbox("Stock period", ["1mo", "3mo", "6mo", "1y"], index=0)



#  Cached data fetchers

# @st.cache_data caches the RETURN VALUE of the function.
# If you call fetch_stock("MSFT", "1mo") twice with the same args,
# the second call returns the cached result instantly — no API call made.
# The cache resets when the function arguments change or the app restarts.
@st.cache_data
def fetch_stock(ticker, period):
    return get_stock_history(ticker, period)

@st.cache_data
def fetch_news(company, days_back, api_key):
    return get_company_news(company, days_back, api_key=api_key)



# STOCK SECTION — primary ticker

st.header(f"Stock Data — {primary_ticker}")

try:
    stock_df = fetch_stock(primary_ticker, period)
except Exception:
    st.error(
        f"Could not load data for **{primary_ticker}**. "
        "Check that the ticker symbol is valid (e.g. MSFT, AAPL, TSLA)."
    )
    st.stop()
# st.stop() halts the rest of the app from running if there's an error here.
# Without it, all the code below would still try to run and crash with
# confusing errors even though the root cause was the bad ticker.

latest_close  = stock_df["Close"].iloc[-1]
highest_price = stock_df["High"].max()
lowest_price  = stock_df["Low"].min()

col1, col2, col3 = st.columns(3)
col1.metric("Latest Close",  f"${latest_close:.2f}")
col2.metric("Highest Price", f"${highest_price:.2f}")
col3.metric("Lowest Price",  f"${lowest_price:.2f}")

# Price change % column added to the data table
# pct_change() calculates (today - yesterday) / yesterday for each row.
# Multiplying by 100 converts it from a decimal (0.02) to a percentage (2.0).
stock_df["Daily Return %"] = stock_df["Close"].pct_change().mul(100).round(2)
st.dataframe(stock_df)



#  Multi-ticker comparison chart

# We normalise all prices to % change from day 1 so tickers are comparable.
# A stock at $900 and one at $50 can't be compared on the same raw price axis —
# normalising them to "how much have they moved since the start" fixes that.
if len(tickers) > 1:
    st.subheader("Multi-Ticker Price Comparison (normalised to % change from start)")

    comparison_fig = go.Figure()
    all_fetched = True

    for t in tickers:
        try:
            df = fetch_stock(t, period)
            df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
            # Normalise: each value expressed as % change from first day's close
            normalised = (df["Close"] / df["Close"].iloc[0] - 1) * 100
            comparison_fig.add_trace(go.Scatter(
                x=df["Date"], y=normalised, name=t, mode="lines"
            ))
        except Exception:
            st.warning(f"Could not load data for {t} — skipping from comparison.")
            all_fetched = False

    comparison_fig.update_layout(
        xaxis_title="Date",
        yaxis_title="% Change from Start",
        legend=dict(x=0, y=1.1, orientation="h")
    )
    st.plotly_chart(comparison_fig, use_container_width=True)



# NEWS + SENTIMENT SECTION

st.header(f"News & Sentiment — {company_name}")
st.caption("Free NewsAPI tier: max 29 days lookback, 20 articles.")

try:
    articles = fetch_news(company_name, 29, NEWS_API_KEY)
except ValueError:
    st.warning(
        f"No articles found for **{company_name}**. "
        "Try a broader or different company name."
    )
    st.stop()
except Exception:
    st.error(
        "Could not connect to NewsAPI. "
        "Check that NEWS_API_KEY is set correctly in your .env file."
    )
    st.stop()



#  Per-article progress bar

# st.progress() renders a live progress bar in the UI.
# We update it after each article so the user can see it moving,
# rather than staring at a frozen spinner for 10+ seconds.
progress_bar = st.progress(0, text="Analysing sentiment — article 0 of 0...")

for i, article in enumerate(articles):
    article["sentiment"] = analyse_sentiment(article["title"])
    progress_bar.progress(
        (i + 1) / len(articles),
        text=f"Analysing sentiment — article {i + 1} of {len(articles)}..."
    )

progress_bar.empty()  # removes the bar from the UI once done


# Map label to a numeric score so we can do maths on it:
# positive = +1, neutral = 0, negative = -1
SCORE_MAP = {"positive": 1, "neutral": 0, "negative": -1}
for article in articles:
    article["score_numeric"] = SCORE_MAP[article["sentiment"]["label"]]



# SUMMARY METRICS

labels   = [a["sentiment"]["label"] for a in articles]
positive = labels.count("positive")
negative = labels.count("negative")
neutral  = labels.count("neutral")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Articles", len(articles))
c2.metric("Positive", positive)
c3.metric("Negative", negative)
c4.metric("Neutral",  neutral)

st.markdown("---")



#  Sentiment breakdown bar chart

st.subheader("Sentiment Breakdown")

bar_df = pd.DataFrame({
    "Sentiment": ["Positive", "Negative", "Neutral"],
    "Count":     [positive,   negative,   neutral]
})
bar_fig = px.bar(
    bar_df, x="Sentiment", y="Count", color="Sentiment",
    color_discrete_map={"Positive": "green", "Negative": "red", "Neutral": "gray"}
)
bar_fig.update_layout(showlegend=False)
st.plotly_chart(bar_fig, use_container_width=True)



# Build daily sentiment DataFrame (used in multiple charts below)

# Group all articles by date and average their numeric sentiment score.
# e.g. if there were 3 articles on a day with scores +1, -1, +1 → avg = 0.33
sentiment_rows = [
    {"Date": pd.to_datetime(a["publishedAt"][:10]), "score": a["score_numeric"]}
    for a in articles
]
sentiment_df = (
    pd.DataFrame(sentiment_rows)
    .groupby("Date")["score"]
    .mean()
    .reset_index()
    .rename(columns={"score": "AvgSentiment"})
)

# Make sure stock Date column is plain date (no timezone) so merging works
stock_df["Date"] = pd.to_datetime(stock_df["Date"]).dt.tz_localize(None)



#  Sentiment over time line chart

st.subheader("Sentiment Score Over Time")
# This shows how market mood around the company has shifted day by day.
# A value near +1 = all positive news, near -1 = all negative news.

sentiment_line_fig = px.line(
    sentiment_df, x="Date", y="AvgSentiment",
    markers=True, title="Daily Average Sentiment Score"
)
sentiment_line_fig.add_hline(y=0, line_dash="dash", line_color="gray")  # neutral baseline
sentiment_line_fig.update_layout(yaxis=dict(range=[-1.2, 1.2], title="Avg Sentiment"))
st.plotly_chart(sentiment_line_fig, use_container_width=True)



# Stock price + sentiment overlay chart

# Dual-axis chart: left axis = closing price, right axis = avg sentiment.
# Use a line for sentiment so it remains visible even when the stock period
# is longer than the 29-day NewsAPI window.
st.subheader(f"{primary_ticker} Closing Price vs Daily Sentiment")

price_sentiment_fig = go.Figure()

price_sentiment_fig.add_trace(go.Scatter(
    x=stock_df["Date"], y=stock_df["Close"],
    name="Close Price", line=dict(color="royalblue"), yaxis="y1"
))

sentiment_colors = [
    "green" if v > 0 else "red" if v < 0 else "gray"
    for v in sentiment_df["AvgSentiment"]
]

price_sentiment_fig.add_trace(go.Scatter(
    x=sentiment_df["Date"], y=sentiment_df["AvgSentiment"],
    name="Avg Sentiment",
    yaxis="y2",
    mode="lines+markers",
    line=dict(color="darkorange", width=3),
    marker=dict(size=8, color=sentiment_colors)
))

price_sentiment_fig.update_layout(
    xaxis_title="Date",
    yaxis =dict(title="Close Price ($)", side="left"),
    yaxis2=dict(
        title="Avg Sentiment", side="right",
        overlaying="y", range=[-1.2, 1.2], showgrid=False
    ),
    legend=dict(x=0, y=1.1, orientation="h")
)
st.plotly_chart(price_sentiment_fig, use_container_width=True)



# Price change % alongside sentiment table

# Merge stock daily returns with daily sentiment on matching dates.
# This lets the user see: "on days when sentiment was positive, did the price go up?"
st.subheader("Daily Return vs Sentiment")

stock_df["DateOnly"] = stock_df["Date"].dt.date
sentiment_df["DateOnly"] = sentiment_df["Date"].dt.date

merged_df = stock_df[["DateOnly", "Close", "Daily Return %"]].merge(
    sentiment_df[["DateOnly", "AvgSentiment"]],
    on="DateOnly", how="inner"
)
merged_df = merged_df.rename(columns={"DateOnly": "Date"})
st.dataframe(merged_df.sort_values("Date", ascending=False).reset_index(drop=True))



#  1 (part 2): Correlation analysis

# Pearson correlation measures the linear relationship between two variables.
# Range: -1.0 (perfect inverse) to +1.0 (perfect match), 0 = no relationship.
# We correlate the daily average sentiment score with that same day's price return.
# NOTE: This is same-day correlation. In practice, sentiment might predict
# the NEXT day's movement — that's called a lagged correlation and is more useful
# for prediction, but same-day still shows whether they move together.
if len(merged_df) >= 3:  # need at least a few data points for correlation to mean anything
    correlation = merged_df["Daily Return %"].corr(merged_df["AvgSentiment"])

    st.subheader("Sentiment vs Price Return Correlation")

    st.metric(
        label="Pearson Correlation (sentiment ↔ daily return)",
        value=f"{correlation:.3f}",
        help="Ranges from -1 (opposite) to +1 (aligned). Near 0 means no relationship."
    )

    # Scatter plot makes the correlation visual — each dot is one day
    scatter_fig = px.scatter(
        merged_df, x="AvgSentiment", y="Daily Return %",
        trendline="ols",  # adds a best-fit regression line
        title="Sentiment Score vs Same-Day Price Return (%)",
        labels={"AvgSentiment": "Avg Sentiment Score", "Daily Return %": "Price Return (%)"}
    )
    scatter_fig.add_vline(x=0, line_dash="dash", line_color="gray")
    scatter_fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(scatter_fig, use_container_width=True)
else:
    st.info("Not enough overlapping dates between news and stock data to calculate correlation.")



#  Export to CSV

st.subheader("Export Data")

export_df = pd.DataFrame([{
    "Title":      a["title"],
    "Published":  a["publishedAt"],
    "Sentiment":  a["sentiment"]["label"],
    "Confidence": round(a["sentiment"]["score"], 4),
    "Score":      a["score_numeric"],
    "URL":        a["url"]
} for a in articles])

csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download articles + sentiment as CSV",
    data=csv,
    file_name=f"{company_name}_sentiment.csv",
    mime="text/csv"
)

st.markdown("---")



# PER-ARTICLE DISPLAY

st.subheader("All Articles")

for article in articles:
    label = article["sentiment"]["label"]
    score = article["sentiment"]["score"]

    color = {"positive": "green", "negative": "red", "neutral": "gray"}.get(label, "gray")
    badge = f":{color}[**{label.upper()}** ({score:.2f})]"

    st.subheader(article["title"])
    st.write(badge)
    st.write(f"Published: {article['publishedAt']}")
    if article["description"]:
        st.write(article["description"])
    st.markdown(f"[Read full article]({article['url']})")
    st.markdown("---")
