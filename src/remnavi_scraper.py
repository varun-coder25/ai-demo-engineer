import json
import re
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

import requests

from models import Job, JobContent


RSS_URL = "https://remnavi.com/feed.php?q=ai&posted_within=1"
OUTPUT_FILE = "data/output/jobs_remnavi.json"


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
        return "Research"
    if "data scientist" in title or "data science" in title:
        return "Data Science"
    if "machine learning" in title or "ml engineer" in title:
        return "Machine Learning"
    if "ai engineer" in title or "artificial intelligence" in title:
        return "AI Engineering"
    if "software engineer" in title:
        return "Software Engineering"
    if "product" in title:
        return "Product"
    if "manager" in title or "director" in title:
        return "Management"

    return "Other"


def parse_date(date_text):
    return datetime.strptime(
        date_text,
        "%a, %d %b %Y %H:%M:%S %z"
    )


def main():
    response = requests.get(RSS_URL, timeout=20)
    response.raise_for_status()

    print("HTTP status:", response.status_code)

    root = ET.fromstring(response.text)
    items = root.findall(".//item")

    print("Jobs received:", len(items))

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    records = []

    for item in items:
        title = item.findtext("title", "")
        date_text = item.findtext("pubDate", "")
        url = item.findtext("link", "")

        if not title or not date_text:
            continue

        published_date = parse_date(date_text)

        if published_date < cutoff:
            continue

        if not is_ai_job(title):
            continue

        company = "Unknown"

        if " · " in title:
            title_parts = title.split(" · ", 1)
            clean_title = title_parts[0]
            company = title_parts[1]
        else:
            clean_title = title

        record = Job(
            content=JobContent(
                company=company,
                date=published_date,
                is_remote=True,
                role_family=get_role_family(clean_title),
            ),
            collectedAt=datetime.now(timezone.utc),
        )

        record_data = record.model_dump(mode="json")

        record_data["content"]["title"] = clean_title
        record_data["source_url"] = url
        record_data["source_name"] = "RemNavi"

        records.append(record_data)

    print("Fresh AI jobs:", len(records))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()