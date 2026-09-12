import asyncio

from github_client import get_stars_for_repositories


async def main():
    repo_urls = [
        "https://github.com/google/pwlfit"
    ]

    stars = await get_stars_for_repositories(repo_urls)

    print("Stars:", stars)


asyncio.run(main())