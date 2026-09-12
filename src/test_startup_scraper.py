import asyncio

from startup_scraper import fetch_yc_page, parse_startups


async def main():
    html = await fetch_yc_page()

    startups = parse_startups(html)

    print("Startups found:", len(startups))

    for startup in startups[:10]:
        print(startup)


asyncio.run(main())