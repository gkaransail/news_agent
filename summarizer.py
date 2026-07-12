import time
from openai import OpenAI, RateLimitError, APIError
from config import GROQ_API_KEY

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)


def summarize_topic(topic_name: str, articles: list[dict]) -> str:
    if not articles:
        return f"No new articles found for {topic_name} today."

    article_text = "\n\n".join(
        f"Title: {a.get('title', '')}\nSource: {a.get('source', {}).get('name', '')}\n"
        f"Summary: {a.get('description', '')[:300]}\nURL: {a.get('url', '')}"
        for a in articles
    )

    prompt = f"""You are a sharp news analyst. Below are today's top articles about {topic_name}.

Write a concise daily digest with:
1. A 2-sentence overview of the biggest theme today
2. 3-5 bullet points — each with a bold headline, one sentence of context, and the article URL
3. One "Key Takeaway" sentence at the end

Keep it punchy and useful. No fluff.

---
{article_text}
"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.4,
            )
            return response.choices[0].message.content.strip()
        except RateLimitError:
            wait = 2 ** attempt * 5
            print(f"[Grok] Rate limited — retrying in {wait}s...")
            time.sleep(wait)
        except APIError as e:
            print(f"[Grok] API error (attempt {attempt + 1}): {e}")
            if attempt == 2:
                return f"Could not generate summary for {topic_name}: {e}"
            time.sleep(3)
    return f"Summary unavailable for {topic_name} after 3 attempts."


def build_digests(news_by_topic: dict[str, list[dict]]) -> dict[str, str]:
    digests = {}
    for topic_name, articles in news_by_topic.items():
        print(f"[Groq] Summarizing {len(articles)} articles for '{topic_name}'...")
        try:
            digests[topic_name] = summarize_topic(topic_name, articles)
        except Exception as e:
            print(f"[Groq] Failed to summarize '{topic_name}': {e}")
            digests[topic_name] = f"Summary unavailable for {topic_name} due to an error."
    return digests
