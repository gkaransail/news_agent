# News Agent

A daily AI-powered news digest that fetches the latest headlines across **Artificial Intelligence** and **Crypto & Web3**, summarizes them using Groq's LLM, and delivers a formatted brief to your email every morning.

## What it does

1. Pulls articles from **NewsAPI** and **RSS feeds** (TechCrunch, VentureBeat, CoinDesk, Decrypt, etc.)
2. Summarizes each topic into a punchy digest using **Groq** (`llama-3.3-70b-versatile`)
3. Sends a styled **HTML email** via **Resend** — no SMTP password needed
4. Optionally sends a **WhatsApp summary** via Twilio
5. Runs on a daily schedule at **10 AM** (configurable timezone)

---

## Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/gkaransail/news_agent.git
cd news_agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.template .env
```

Edit `.env` with your keys:

```env
# Groq API — groq.com (free)
GROQ_API_KEY=gsk_...

# NewsAPI — newsapi.org (free)
NEWS_API_KEY=your_key_here

# Resend — resend.com (free, no SMTP password needed)
RESEND_API_KEY=re_...
RECIPIENT_EMAIL=you@gmail.com

# Twilio WhatsApp (optional)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:
RECIPIENT_WHATSAPP=whatsapp:

# Schedule
SEND_TIME=10:00
TIMEZONE=Australia/Sydney
```

---

## Usage

**Test immediately** (prints digest + sends email):
```bash
python main.py --now --print
```

**Run for a single topic:**
```bash
python main.py --now --topic AI
python main.py --now --topic Crypto
```

**Start the daily scheduler** (fires every day at `SEND_TIME`):
```bash
python main.py
```

---

## Adding topics or RSS feeds

Edit `config.py`:

```python
TOPICS = [
    {"name": "Artificial Intelligence", "queries": ["AI agents", "LLM", "OpenAI", ...]},
    {"name": "Crypto & Web3",           "queries": ["Bitcoin", "DeFi", "blockchain", ...]},
    # Add a new topic here
    {"name": "Startups", "queries": ["startup funding", "YCombinator", "venture capital"]},
]

RSS_FEEDS = {
    "Startups": [
        "https://techcrunch.com/startups/feed/",
    ],
}
```

---

## Stack

| Component | Service |
|---|---|
| LLM summarization | [Groq](https://groq.com) — `llama-3.3-70b-versatile` |
| News articles | [NewsAPI](https://newsapi.org) + RSS via `feedparser` |
| Email delivery | [Resend](https://resend.com) |
| WhatsApp | [Twilio](https://twilio.com) |
| Scheduler | `schedule` library |

---

## Getting API keys

| Key | Where to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) → API Keys |
| `NEWS_API_KEY` | [newsapi.org/register](https://newsapi.org/register) |
| `RESEND_API_KEY` | [resend.com](https://resend.com) → Dashboard → API Keys |
