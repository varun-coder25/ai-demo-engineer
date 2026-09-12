import asyncio
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone


RSS_URL = "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"


async def fetch_page(session, url):
    try:
        async with session.get(url, timeout=15) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as error:
        print(f"Failed: {url} - {error}")
        return None


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    article = soup.find("article")

    if article:
        text = article.get_text(separator=" ", strip=True)
    else:
        paragraphs = soup.find_all("p")
        text = " ".join(
            paragraph.get_text(strip=True)
            for paragraph in paragraphs
        )

    return text


async def scrape_news():
    feed = feedparser.parse(RSS_URL)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    news = []

    async with aiohttp.ClientSession(
        headers={"User-Agent": "Mozilla/5.0"}
    ) as session:

        for entry in feed.entries:
            if not hasattr(entry, "published_parsed"):
                continue

            published = datetime(
                *entry.published_parsed[:6],
                tzinfo=timezone.utc
            )

            if published < cutoff:
                continue

            print(f"Fetching: {entry.title}")

            html = await fetch_page(session, entry.link)

            if not html:
                continue

            text = extract_text(html)

            if len(text) < 200:
                continue

            news.append({
                "title": entry.title,
                "text": text,
                "date": published.isoformat(),
                "source_name": "The Verge AI",
                "source_url": entry.link
            })

    return news


if __name__ == "__main__":
    results = asyncio.run(scrape_news())

    print()
    print(f"Fresh news articles: {len(results)}")

    for article in results:
        print()
        print(article["title"])
        print(article["date"])
        print(article["source_url"])
        print(f"Text length: {len(article['text'])}")