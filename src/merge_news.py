import asyncio
import json
import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_scraper import scrape_news as scrape_techcrunch
from news_scraper_verge import scrape_news as scrape_verge
from news_scraper_mit import scrape_news as scrape_mit
from news_scraper_infoq import scrape_news as scrape_infoq
from news_scraper_bbc import scrape_news as scrape_bbc


def normalize_title(title):
    return " ".join(title.lower().split())


def is_valid_news(item):
    title = item.get("title", "").lower()

    excluded_words = [
        "podcast",
        "side events",
        "book your exhibit",
        "exhibit table"
    ]

    for word in excluded_words:
        if word in title:
            return False

    return True


async def collect_news():
    print("Collecting TechCrunch...")
    techcrunch = await scrape_techcrunch()

    print("Collecting The Verge...")
    verge = await scrape_verge()

    print("Collecting MIT Technology Review...")
    mit = await scrape_mit()

    print("Collecting InfoQ...")
    infoq = await scrape_infoq()

    print("Collecting BBC...")
    bbc = await scrape_bbc()

    all_news = []

    for items in [techcrunch, verge, mit, infoq, bbc]:
        if items:
            all_news.extend(items)

    unique_news = []
    seen = set()

    for item in all_news:
        if not is_valid_news(item):
            continue

        title = normalize_title(item.get("title", ""))
        url = item.get("url", item.get("source_url", ""))

        key = title + "|" + url

        if key not in seen:
            seen.add(key)
            unique_news.append(item)

    return unique_news


def validate_freshness(news):
    now = datetime.now(timezone.utc)
    valid = []

    for item in news:
        date_value = item.get("date")

        if not date_value:
            continue

        try:
            published = datetime.fromisoformat(
                date_value.replace("Z", "+00:00")
            )

            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)

            age_hours = (
                now - published
            ).total_seconds() / 3600

            if 0 <= age_hours <= 24:
                valid.append(item)

        except (ValueError, TypeError):
            print(
                f"Could not parse date for: "
                f"{item.get('title', 'Unknown')}"
            )

    return valid


async def main():
    news = await collect_news()

    print(f"\nCollected after deduplication: {len(news)}")

    fresh_news = validate_freshness(news)

    print(f"Fresh news within 24 hours: {len(fresh_news)}")

    os.makedirs("data/output", exist_ok=True)

    output_file = "data/output/news_final.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            fresh_news,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved: {output_file}")

    print("\nNews by source:")

    source_counts = {}

    for item in fresh_news:
        source = item.get(
            "source_name",
            item.get("source", "Unknown")
        )

        source_counts[source] = (
            source_counts.get(source, 0) + 1
        )

    for source, count in source_counts.items():
        print(f"{source}: {count}")


if __name__ == "__main__":
    asyncio.run(main())