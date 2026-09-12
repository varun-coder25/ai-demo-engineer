import asyncio
import aiohttp
import html
import json
import re
from pathlib import Path


YC_AI_URL = "https://www.ycombinator.com/companies/industry/ai"


async def fetch_page(session, page_number):
    url = YC_AI_URL

    if page_number > 1:
        url = f"{YC_AI_URL}?page={page_number}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    async with session.get(
        url,
        headers=headers
    ) as response:
        response.raise_for_status()
        return await response.text()


def parse_startups(page_html):
    page_html = html.unescape(page_html)

    pattern = r'\{"_type":"company".*?"ycdc_company_url":".*?"\}'

    matches = re.findall(
        pattern,
        page_html
    )

    startups = []

    for match in matches:
        try:
            company = json.loads(match)

            source_url = company.get(
                "ycdc_company_url"
            )

            if not source_url:
                continue

            startups.append({
                "name": company.get("name"),
                "employeeCount": company.get("team_size"),
                "location": company.get("location"),
                "website": company.get("website"),
                "description": company.get("long_description"),
                "tags": company.get("tags", []),
                "batch": company.get("batch_name"),
                "status": company.get("ycdc_status"),
                "sourceUrl": (
                    "https://www.ycombinator.com"
                    + source_url
                )
            })

        except json.JSONDecodeError:
            continue

    return startups


async def main():
    all_startups = {}

    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        for page_number in range(1, 21):
            print(
                f"Fetching YC page {page_number}..."
            )

            page_html = await fetch_page(
                session,
                page_number
            )

            startups = parse_startups(
                page_html
            )

            print(
                f"Page {page_number}: "
                f"{len(startups)} startups"
            )

            for startup in startups:
                all_startups[
                    startup["sourceUrl"]
                ] = startup

            print(
                f"Total unique startups: "
                f"{len(all_startups)}"
            )

    startups = list(all_startups.values())

    output_dir = Path("data/output")
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir / "startups.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            startups,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\nFinal startups: {len(startups)}"
    )

    print(
        f"Saved: {output_file}"
    )


if __name__ == "__main__":
    asyncio.run(main())