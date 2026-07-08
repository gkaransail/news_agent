import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "gkaransail@gmail.com")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
RECIPIENT_WHATSAPP = os.getenv("RECIPIENT_WHATSAPP")

SEND_TIME = os.getenv("SEND_TIME", "10:00")
TIMEZONE = os.getenv("TIMEZONE", "Australia/Sydney")

# Topics to track — add or remove freely
TOPICS = [
    {"name": "Artificial Intelligence", "queries": ["artificial intelligence", "AI agents", "LLM", "ChatGPT", "Claude AI", "OpenAI"]},
    {"name": "Crypto & Web3",           "queries": ["cryptocurrency", "Bitcoin", "Ethereum", "DeFi", "Web3", "blockchain"]},
]

# RSS feeds per topic
RSS_FEEDS = {
    "Artificial Intelligence": [
        "https://feeds.feedburner.com/oreilly/radar",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://venturebeat.com/category/ai/feed/",
        "https://www.technologyreview.com/feed/",
    ],
    "Crypto & Web3": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://decrypt.co/feed",
        "https://cointelegraph.com/rss",
        "https://bitcoinmagazine.com/.rss/full/",
    ],
}
