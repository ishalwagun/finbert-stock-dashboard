import os
from dotenv import load_dotenv
from newsapi import NewsApiClient

load_dotenv()

API_KEY = os.getenv('NEWS_API_KEY')
ticker = "stock"

newsapi = NewsApiClient(api_key=API_KEY)

top_headlines = newsapi.get_top_headlines(q=ticker)

print(top_headlines)