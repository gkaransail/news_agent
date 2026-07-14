import json
import time
import hashlib
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from config import NEWS_API_KEY, TOPICS, RSS_FEEDS

_CACHE_FILE = Path(__file__).parent / ".article_cache.json"
_CACHE_TTL_HOURS = 6


def _load_cache() -> dict:
    if _CACHE_FILE.exists():
        try:
            data = json.loads(_CACHE_FILE.read_text())
            cutoff = datetime.now(timezone.utc).timestamp() - _CACHE_TTL_HOURS * 3600
            return {k: v for k, v in data.items() if v.get("ts", 0) > cutoff}
        except Exception:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    try:
        _CACHE_FILE.write_text(json.dumps(cache))
    except Exception:
        pass


def _cache_key(query: str, lookback_days: int) -> str:
    return hashlib.md5(f"{query}:{lookback_days}".encode()).hexdigest()


def fetch_newsapi_articles(query: str, max_articles: int = 10, lookback_days: int = 1) -> list[dict]:
    if not NEWS_API_KEY:
        return []

    cache = _load_cache()
    key = _cache_key(query, lookback_days)
    if key in cache:
        return cache[key]["articles"]

    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": since,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": max_articles,
        "apiKey": NEWS_API_KEY,
    }
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            articles = resp.json().get("articles", [])
            cache[key] = {"articles": articles, "ts": datetime.now(timezone.utc).timestamp()}
            _save_cache(cache)
            return articles
        except requests.exceptions.Timeout:
            print(f"[NewsAPI] Timeout for '{query}' (attempt {attempt + 1})")
            time.sleep(2 ** attempt)
        except Exception as e:
            print(f"[NewsAPI] Error for '{query}': {e}")
            return []
    return []


def fetch_rss_articles(feed_url: str, max_articles: int = 5, lookback_days: int = 1) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
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


def _title_key(title: str) -> str:
    """Normalise a title to a short fingerprint for deduplication."""
    stop = {"a", "an", "the", "in", "on", "at", "to", "of", "and", "is", "for", "with"}
    words = [w.lower() for w in title.split() if w.lower() not in stop]
    return " ".join(words[:6])


def gather_all_news(lookback_days: int = 1) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()

    for topic in TOPICS:
        topic_name = topic["name"]
        articles = []

        for query in topic["queries"]:
            for article in fetch_newsapi_articles(query, max_articles=5, lookback_days=lookback_days):
                url = article.get("url", "")
                title_key = _title_key(article.get("title", ""))
                if url and url not in seen_urls and title_key not in seen_titles:
                    seen_urls.add(url)
                    seen_titles.add(title_key)
                    articles.append(article)

        for feed_url in RSS_FEEDS.get(topic_name, []):
            for article in fetch_rss_articles(feed_url, max_articles=5, lookback_days=lookback_days):
                url = article.get("url", "")
                title_key = _title_key(article.get("title", ""))
                if url and url not in seen_urls and title_key not in seen_titles:
                    seen_urls.add(url)
                    seen_titles.add(title_key)
                    articles.append(article)

        results[topic_name] = articles[:20]

    return results
