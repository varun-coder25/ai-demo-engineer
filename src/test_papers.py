import asyncio

from paper_scraper import fetch_papers, parse_papers, find_github_url
from github_client import get_repository_stars


async def main():
    xml_data = await fetch_papers(max_results=5)
    papers = parse_papers(xml_data)

    for paper in papers:
        github_url = await find_github_url(paper.content.paper_url)

        if github_url:
            stars = await get_repository_stars(github_url)
            paper.content.github_url = github_url
            paper.content.github_stars = stars

        print("\n" + "=" * 60)
        print("Title:", paper.content.title)
        print("GitHub:", paper.content.github_url)
        print("Stars:", paper.content.github_stars)


asyncio.run(main())