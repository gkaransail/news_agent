#!/usr/bin/env python3
"""
News Agent — fetches AI & crypto news daily, summarizes via Grok, sends email + WhatsApp.
Run: python main.py           (starts scheduler, fires at SEND_TIME daily)
Run: python main.py --now     (fire immediately, useful for testing)
"""

import argparse
import sys
import time
import pytz
import schedule
from datetime import datetime

from config import SEND_TIME, TIMEZONE
from scraper import gather_all_news
from summarizer import build_digests
from notifier import notify


def run_job(topic_filter: str | None = None, print_digest: bool = False, dry_run: bool = False) -> None:
    start = datetime.now()
    print(f"\n[{start.strftime('%Y-%m-%d %H:%M:%S')}] Starting daily news job{' (dry run)' if dry_run else ''}...")

    news = gather_all_news()
    if topic_filter:
        news = {k: v for k, v in news.items() if topic_filter.lower() in k.lower()}
        if not news:
            print(f"[Job] No topic matched '{topic_filter}'.")
            return

    total = sum(len(v) for v in news.values())
    print(f"[Scraper] Fetched {total} articles across {len(news)} topics.")

    digests = build_digests(news)

    if print_digest:
        print("\n" + "=" * 60)
        for topic, content in digests.items():
            print(f"\n{'='*60}\n  {topic.upper()}\n{'='*60}\n")
            print(content)
        print("\n" + "=" * 60)

    if not dry_run:
        notify(digests)

    elapsed = (datetime.now() - start).seconds
    print(f"\n--- Run Summary ---")
    for topic, articles in news.items():
        print(f"  {topic}: {len(articles)} articles")
    print(f"  Notifications: {'skipped (dry run)' if dry_run else 'sent'}")
    print(f"  Total time: {elapsed}s")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Job complete.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily News Agent")
    parser.add_argument("--now", action="store_true", help="Run immediately (skip scheduler)")
    parser.add_argument("--topic", type=str, default=None, help="Filter to a single topic (e.g. 'AI' or 'Crypto')")
    parser.add_argument("--print", action="store_true", dest="print_digest", help="Print digest to terminal")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run", help="Fetch and summarize but skip sending notifications")
    args = parser.parse_args()

    if args.now:
        run_job(topic_filter=args.topic, print_digest=args.print_digest, dry_run=args.dry_run)
        return

    tz = pytz.timezone(TIMEZONE)
    print(f"[Scheduler] News agent started. Will send daily at {SEND_TIME} ({TIMEZONE}).")
    print(f"[Scheduler] Current time: {datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("[Scheduler] Press Ctrl+C to stop.\n")

    schedule.every().day.at(SEND_TIME).do(run_job)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Scheduler] Stopped.")
        sys.exit(0)
