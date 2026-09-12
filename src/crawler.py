import asyncio
import random
import aiohttp


async def fetch_url(session, url, semaphore, max_retries=3):
    async with semaphore:
        for attempt in range(max_retries):
            try:
                async with session.get(url) as response:
                    if response.status == 429 or response.status >= 500:
                        if attempt < max_retries - 1:
                            delay = (2 ** attempt) + random.uniform(0, 1)
                            print(f"Retrying {url} in {delay:.2f}s")
                            await asyncio.sleep(delay)
                            continue

                    response.raise_for_status()
                    return await response.text()

            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Retrying {url} in {delay:.2f}s")
                    await asyncio.sleep(delay)
                else:
                    print(f"Timeout: {url}")

            except aiohttp.ClientError as error:
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Retrying {url} in {delay:.2f}s")
                    await asyncio.sleep(delay)
                else:
                    print(f"Request failed: {url} - {error}")

    return None


async def fetch_all(urls, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [
            fetch_url(session, url, semaphore)
            for url in urls
        ]

        return await asyncio.gather(*tasks)