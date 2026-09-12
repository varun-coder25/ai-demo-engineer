import asyncio
import json
import re
from datetime import datetime, timedelta, timezone

import aiohttp
from bs4 import BeautifulSoup

from models import Job, JobContent


API_URL = "https://www.arbeitnow.com/api/job-board-api"
OUTPUT_FILE = "data/output/jobs_arbeitnow.json"


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


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    return soup.get_text(separator=" ", strip=True)


async def fetch_jobs():
    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(API_URL) as response:
            response.raise_for_status()
            return await response.json()


async def main():
    data = await fetch_jobs()

    jobs = data.get("data", [])

    print("Jobs received:", len(jobs))

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    records = []

    for job in jobs:
        title = job.get("title", "")
        created_at = job.get("created_at")

        if not title or not created_at:
            continue

        published_date = datetime.fromtimestamp(
            created_at,
            tz=timezone.utc
        )

        if published_date < cutoff:
            continue

        if not is_ai_job(title):
            continue

        description = extract_text(job.get("description", ""))

        company = job.get("company_name", "Unknown")

        record = Job(
            content=JobContent(
                company=company,
                date=published_date,
                is_remote=bool(job.get("remote", False)),
                role_family=get_role_family(title),
            ),
            collectedAt=datetime.now(timezone.utc),
        )

        record_data = record.model_dump(mode="json")

        record_data["content"]["title"] = title
        record_data["content"]["description"] = description
        record_data["source_url"] = job.get("url")
        record_data["source_name"] = "Arbeitnow"

        records.append(record_data)

    print("Fresh AI jobs:", len(records))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.run(main())