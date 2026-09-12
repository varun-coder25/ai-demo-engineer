import json
from datetime import datetime, timezone, timedelta


FILE = "data/output/jobs_final.json"


with open(FILE, "r", encoding="utf-8") as file:
    jobs = json.load(file)


cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

print("Total jobs:", len(jobs))
print()

for i, job in enumerate(jobs, 1):
    content = job["content"]

    date = datetime.fromisoformat(
        content["date"].replace("Z", "+00:00")
    )

    fresh = date >= cutoff

    print(
        f"{i}. {content.get('title', 'NO TITLE')}"
    )
    print(
        f"   Company: {content.get('company', 'NO COMPANY')}"
    )
    print(
        f"   Date: {date.isoformat()}"
    )
    print(
        f"   Fresh: {fresh}"
    )
    print(
        f"   Source: {job.get('source_name', 'NO SOURCE')}"
    )
    print(
        f"   URL: {job.get('source_url', 'NO URL')}"
    )
    print()


print("Validation complete.")