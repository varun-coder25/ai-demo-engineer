import json
import re
from datetime import datetime, timedelta, timezone


INPUT_FILES = [
    ("data/output/jobs.json", "Himalayas"),
    ("data/output/jobs_remote_first.json", "Remote First Jobs"),
    ("data/output/jobs_jobicy.json", "Jobicy"),
    ("data/output/jobs_arbeitnow.json", "Arbeitnow"),
    ("data/output/jobs_remnavi.json", "RemNavi"),
]

OUTPUT_FILE = "data/output/jobs_final.json"


AI_KEYWORDS = [
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


def is_ai_job(title):
    title = title.lower()

    return any(
        re.search(keyword, title)
        for keyword in AI_KEYWORDS
    )


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return None


def normalize_text(value):
    if not value:
        return ""

    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)

    return " ".join(value.split())


def load_jobs(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("File not found:", filename)
        return []


def get_himalayas_company(url):
    match = re.search(
        r"himalayas\.app/companies/([^/]+)/jobs/",
        url
    )

    if match:
        return match.group(1).replace("-", " ").title()

    return "Unknown"


def main():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    unique_jobs = {}
    source_counts = {}

    for filename, source_name in INPUT_FILES:
        jobs = load_jobs(filename)

        print(filename, "->", len(jobs))

        source_counts[source_name] = {
            "fresh_collected": len(jobs),
            "accepted": 0
        }

        for job in jobs:
            content = job.get("content", {})

            title = content.get("title", "")
            company = content.get("company", "")
            date_value = content.get("date")
            source_url = job.get("source_url", "")

            if source_name == "Himalayas" and company == "Unknown":
                company = get_himalayas_company(source_url)
                job["content"]["company"] = company

            published_date = parse_datetime(date_value)

            if not published_date:
                continue

            if published_date.tzinfo is None:
                published_date = published_date.replace(
                    tzinfo=timezone.utc
                )

            if published_date < cutoff:
                continue

            if not is_ai_job(title):
                continue

            job_key = (
                normalize_text(title),
                normalize_text(company)
            )

            if job_key not in unique_jobs:
                job["content"]["date"] = published_date.isoformat()

                job["source_name"] = source_name

                job["sources"] = [
                    {
                        "name": source_name,
                        "url": source_url
                    }
                ]

                unique_jobs[job_key] = job
                source_counts[source_name]["accepted"] += 1

            else:
                existing = unique_jobs[job_key]

                existing_sources = existing.get("sources", [])

                already_exists = any(
                    source["name"] == source_name
                    for source in existing_sources
                )

                if not already_exists:
                    existing_sources.append({
                        "name": source_name,
                        "url": source_url
                    })

                existing["sources"] = existing_sources

                source_counts[source_name]["accepted"] += 1

    final_jobs = list(unique_jobs.values())

    final_jobs.sort(
        key=lambda job: job["content"]["date"],
        reverse=True
    )

    print()
    print("Unique final jobs:", len(final_jobs))
    print()
    print("Source observations:")

    for source, counts in source_counts.items():
        print(
            source,
            "->",
            counts["fresh_collected"],
            "collected,",
            counts["accepted"],
            "accepted"
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            final_jobs,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()