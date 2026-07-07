import feedparser
import requests
from datetime import datetime, timedelta, timezone
from config import NEWS_API_KEY, TOPICS, RSS_FEEDS


def fetch_newsapi_articles(query: str, max_articles: int = 10) -> list[dict]:
    if not NEWS_API_KEY:
        return []
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": yesterday,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": max_articles,
        "apiKey": NEWS_API_KEY,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("articles", [])
    except Exception as e:
        print(f"[NewsAPI] Error for '{query}': {e}")
        return []


def fetch_rss_articles(feed_url: str, max_articles: int = 5) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=1)
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        for entry in feed.entries[:max_articles]:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            if published and published < cutoff:
                continue
            articles.append({
                "title": entry.get("title", ""),
                "description": entry.get("summary", entry.get("description", "")),
                "url": entry.get("link", ""),
                "publishedAt": published.isoformat() if published else "",
                "source": {"name": feed.feed.get("title", feed_url)},
            })
        return articles
    except Exception as e:
        print(f"[RSS] Error for '{feed_url}': {e}")
        return []


def gather_all_news() -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}
    seen_urls: set[str] = set()

    for topic in TOPICS:
        topic_name = topic["name"]
        articles = []

        for query in topic["queries"]:
            for article in fetch_newsapi_articles(query, max_articles=5):
                url = article.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    articles.append(article)

        for feed_url in RSS_FEEDS.get(topic_name, []):
            for article in fetch_rss_articles(feed_url, max_articles=5):
                url = article.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    articles.append(article)

        results[topic_name] = articles[:20]

    return results
