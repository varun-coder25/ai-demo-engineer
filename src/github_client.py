import asyncio
import os
import random

import aiohttp
from dotenv import load_dotenv


load_dotenv()

GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


async def get_repository_stars(
    session,
    repo_url,
    semaphore,
    max_retries=3
):
    if not repo_url:
        return None

    parts = repo_url.rstrip("/").split("/")

    if len(parts) < 2:
        return None

    owner = parts[-2]
    repo = parts[-1]

    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}"

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    async with semaphore:
        for attempt in range(max_retries):
            try:
                async with session.get(
                    url,
                    headers=headers
                ) as response:

                    if response.status in (403, 429):
                        remaining = response.headers.get(
                            "X-RateLimit-Remaining"
                        )

                        if remaining == "0":
                            reset_time = response.headers.get(
                                "X-RateLimit-Reset"
                            )

                            if reset_time:
                                import time

                                wait_time = max(
                                    int(reset_time) - int(time.time()),
                                    1
                                )
                            else:
                                wait_time = (2 ** attempt) + random.uniform(0, 1)
                        else:
                            wait_time = (2 ** attempt) + random.uniform(0, 1)

                        if attempt < max_retries - 1:
                            print(
                                f"GitHub rate limit. "
                                f"Retrying in {wait_time:.2f}s"
                            )
                            await asyncio.sleep(wait_time)
                            continue

                        return None

                    if response.status >= 500:
                        if attempt < max_retries - 1:
                            delay = (2 ** attempt) + random.uniform(0, 1)
                            await asyncio.sleep(delay)
                            continue

                        return None

                    if response.status != 200:
                        return None

                    data = await response.json()

                    return data.get("stargazers_count")

            except (aiohttp.ClientError, asyncio.TimeoutError):
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)

    return None


async def get_stars_for_repositories(
    repo_urls,
    max_concurrent=10
):
    semaphore = asyncio.Semaphore(max_concurrent)
    timeout = aiohttp.ClientTimeout(total=15)

    completed = 0
    total = len(repo_urls)

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        async def fetch_one(url):
            nonlocal completed

            stars = await get_repository_stars(
                session,
                url,
                semaphore
            )

            completed += 1

            if completed % 50 == 0 or completed == total:
                print(f"GitHub: {completed}/{total}")

            return stars

        tasks = [
            fetch_one(url)
            for url in repo_urls
        ]

        return await asyncio.gather(*tasks)