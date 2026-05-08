import os
from dotenv import load_dotenv
from newsapi import NewsApiClient
from datetime import date, timedelta

load_dotenv()

# Now accepts an optional api_key argument so app.py can pass it in
# from Streamlit secrets (needed for deployment) instead of only .env
def get_company_news(query="Microsoft", days_back=29, api_key=None):
    key = api_key or os.getenv('NEWS_API_KEY')

    if not key:
        raise ValueError("API key not found. Set NEWS_API_KEY in .env or pass it directly.")

    newsapi = NewsApiClient(api_key=key)

    to_date = date.today()
    from_date = to_date - timedelta(days=days_back)

    response = newsapi.get_everything(
        q=query,
        from_param=from_date.isoformat(),
        to=to_date.isoformat(),
        language='en',
        sort_by='publishedAt',
        page_size=20
    )

    articles = response.get('articles', [])

    if not articles:
        raise ValueError(f"No news articles found for '{query}' in the last {days_back} days.")

    return [{
        "title": article.get("title"),
        "description": article.get("description"),
        "publishedAt": article.get("publishedAt"),
        "url": article.get("url")
    } for article in articles]


if __name__ == "__main__":
    news = get_company_news("Microsoft", 29)
    print(f"Total articles: {len(news)}\n")
    for article in news:
        print(f"Title: {article['title']}")
        print(f"Published At: {article['publishedAt']}\n")
