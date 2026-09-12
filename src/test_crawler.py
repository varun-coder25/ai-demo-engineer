import asyncio
from crawler import fetch_all
from parser import extract_text


async def main():
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net"
    ]

    results = await fetch_all(urls)

    for url, html in zip(urls, results):
        if html:
            text = extract_text(html)
            print(f"\n{url}")
            print(text[:300])


asyncio.run(main())