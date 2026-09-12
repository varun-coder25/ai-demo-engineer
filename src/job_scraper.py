import asyncio
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import aiohttp
from bs4 import BeautifulSoup

from models import Job, JobContent


RSS_URL = "https://himalayas.app/jobs/rss"
OUTPUT_FILE = "data/output/jobs.json"


def is_ai_job(title):
    keywords = [
        r"\bai\b",
        r"\bartificial intelligence\b",
        r"\bmachine learning\b",
        r"\bml engineer\b",
        r"\bllm\b",
        r"\bgenerative ai\b",
        r"\bgenai\b",
        r"\bdeep learning\b",
        r"\bnlp\b",
        r"\bnatural language processing\b",
        r"\bcomputer vision\b",
        r"\bdata scientist\b",
        r"\bdata science\b",
        r"\bai researcher\b",
        r"\bai research\b",
        r"\bprompt engineer\b",
        r"\bapplied ai\b",
    ]

    title = title.lower()

    return any(re.search(keyword, title) for keyword in keywords)


def get_role_family(title):
    title = title.lower()

    if "research" in title:
        return "RESEARCH"
    if "data scientist" in title or "data science" in title:
        return "DATA SCIENCE"
    if "machine learning" in title or "ml engineer" in title:
        return "MACHINE LEARNING"
    if "ai engineer" in title or "artificial intelligence" in title:
        return "ENGINEERING"
    if "software engineer" in title:
        return "ENGINEERING"
    if "product" in title:
        return "PRODUCT"
    if "manager" in title or "director" in title:
        return "MANAGEMENT"

    return "OTHER"


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    return soup.get_text(separator=" ", strip=True)


def parse_date(date_text):
    return datetime.strptime(
        date_text,
        "%a, %d %b %Y %H:%M:%S %Z"
    ).replace(tzinfo=timezone.utc)


async def fetch_rss():
    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(RSS_URL) as response:
            response.raise_for_status()
            return await response.text()


async def main():
    xml_text = await fetch_rss()

    root = ET.fromstring(xml_text)
    items = root.findall(".//item")

    print("Jobs received:", len(items))

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    records = []

    for item in items:
        title = item.findtext("title", "")
        date_text = item.findtext("pubDate", "")
        url = item.findtext("link", "")
        description = item.findtext("description", "")
        company = item.findtext("companyName", "")

        if not title or not date_text:
            continue

        published_date = parse_date(date_text)

        if published_date < cutoff:
            continue

        if not is_ai_job(title):
            continue

        if not company:
            company = "Unknown"

        description = extract_text(description)

        record = Job(
            content=JobContent(
                company=company,
                date=published_date,
                is_remote=True,
                role_family=get_role_family(title),
            ),
            collectedAt=datetime.now(timezone.utc),
        )

        record_data = record.model_dump(mode="json")

        record_data["content"]["title"] = title
        record_data["content"]["description"] = description
        record_data["source_url"] = url
        record_data["source_name"] = "Himalayas"

        records.append(record_data)

    print("Fresh AI jobs:", len(records))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.run(main())