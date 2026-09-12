import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from paper_code_mapping import (
    load_paper_code_mapping,
    get_papers_with_repositories,
)
from paper_scraper import fetch_papers_by_ids, parse_papers
from github_client import get_stars_for_repositories
from models import ResearchPaper, ResearchPaperContent


async def main():
    df = load_paper_code_mapping()

    papers = get_papers_with_repositories(df, limit=1000)

    print("Selected papers:", len(papers))

    arxiv_ids = papers["paper_arxiv_id"].tolist()

    print("Fetching arXiv metadata...")

    xml_batches = await fetch_papers_by_ids(arxiv_ids)

    metadata = []

    for xml_data in xml_batches:
        metadata.extend(parse_papers(xml_data))

    print("Metadata received:", len(metadata))

    metadata_by_id = {
        paper["arxiv_id"]: paper
        for paper in metadata
    }

    repo_urls = papers["repo_url"].tolist()

    print("Fetching GitHub stars...")

    stars = await get_stars_for_repositories(
        repo_urls,
        max_concurrent=10
    )

    records = []

    for (_, paper), star_count in zip(papers.iterrows(), stars):
        arxiv_id = paper["paper_arxiv_id"]
        arxiv_paper = metadata_by_id.get(arxiv_id)

        if not arxiv_paper:
            continue

        record = ResearchPaper(
            content=ResearchPaperContent(
                title=arxiv_paper["title"],
                authors=arxiv_paper["authors"],
                paper_url=arxiv_paper["paper_url"],
                github_url=paper["repo_url"],
                github_stars=star_count,
                published_date=arxiv_paper["published_date"],
            ),
            collectedAt=datetime.now(timezone.utc),
        )

        records.append(record)

    print("Created records:", len(records))

    records_with_stars = sum(
        record.content.github_stars is not None
        for record in records
    )

    print(
        "Records with GitHub star data:",
        records_with_stars
    )

    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "research_papers.json"

    data = [
        record.model_dump(mode="json")
        for record in records
    ]

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print("Saved:", output_file)
    print("Saved records:", len(data))


asyncio.run(main())