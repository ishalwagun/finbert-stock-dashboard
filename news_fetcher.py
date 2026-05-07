import os
from dotenv import load_dotenv
from newsapi import NewsApiClient
from datetime import date,  timedelta

load_dotenv()

API_KEY = os.getenv('NEWS_API_KEY')


def get_company_news(query="Microsoft", days_back=29):
    if not API_KEY:
        raise ValueError("API key not found. Please set the NEWS_API_KEY environment variable.")
    

    newsapi = NewsApiClient(api_key=API_KEY)

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


    articles= response.get('articles', [])

    if not articles:
        raise ValueError(f"No news articles found for'{query}' in the last {days_back} days.")
    
    cleaned_articles = []
    for article in articles:
        cleaned_articles.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "publishedAt": article.get("publishedAt"),
            "url": article.get("url")
        })

    return cleaned_articles


if __name__ == "__main__":
    news = get_company_news("Microsoft", 29)

    print(f"Total articles: {len(news)}\n")

    for article in news:
        print(f"Title: {article['title']}")
        print(f"Description: {article['description']}")
        print(f"Published At: {article['publishedAt']}")
        print(f"URL: {article['url']}\n")
