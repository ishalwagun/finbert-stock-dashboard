# News Sentiment Stock Dashboard

This is a Streamlit dashboard that combines stock price data with headline sentiment so you can explore how news coverage lines up with market movement.

The app pulls stock history from Yahoo Finance, fetches recent company news from NewsAPI, and runs each headline through FinBERT for sentiment analysis. It then shows summary metrics, sentiment charts, price charts, and a combined closing-price-versus-sentiment view.

## What it does

- Looks up stock data for a selected ticker
- Supports multi-ticker price comparison
- Fetches recent company news
- Scores each headline as positive, negative, or neutral
- Aggregates daily average sentiment
- Compares daily sentiment with stock returns

## Tech stack

- Streamlit
- Pandas
- Plotly
- yfinance
- NewsAPI
- Hugging Face Transformers
- FinBERT

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your NewsAPI key to a `.env` file:

```env
NEWS_API_KEY=your_key_here
```

4. Start the app:

```bash
streamlit run app.py
```

## Streamlit deployment

For Streamlit Community Cloud, add your key in the app's `Secrets` settings:

```toml
NEWS_API_KEY = "your_key_here"
```

You do not need to commit a real `secrets.toml` file. The repo includes `.streamlit/secrets.toml.example` only as a template.

## Notes

- NewsAPI's free tier has a limited lookback window and article count.
- Full sentiment analysis runs on the first ticker only.
- The sentiment model may take a little time to load on first run.
