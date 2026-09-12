import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup

from models import Product, ProductContent, PricingModel, Source


def get_page_text(page_html):
    soup = BeautifulSoup(
        page_html,
        "html.parser"
    )

    for element in soup(
        ["script", "style", "noscript"]
    ):
        element.decompose()

    return soup.get_text(
        " ",
        strip=True
    )


def detect_pricing(page_text):
    text = page_text.lower()

    if "enterprise pricing" in text:
        return PricingModel.ENTERPRISE

    if "contact sales" in text:
        return PricingModel.ENTERPRISE

    if "free plan" in text and (
        "paid plan" in text
        or "pro plan" in text
        or "premium plan" in text
    ):
        return PricingModel.FREEMIUM

    if "free forever" in text:
        return PricingModel.FREE

    if "free plan" in text:
        return PricingModel.FREEMIUM

    if re.search(
        r"\$\s?\d+",
        page_text
    ):
        return PricingModel.PAID

    if "pricing" in text:
        return PricingModel.PAID

    return None


async def fetch_product(
    session,
    startup
):
    url = startup.get("website")

    if not url:
        return None

    try:
        async with session.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        ) as response:

            if response.status != 200:
                return None

            html = await response.text()

            text = get_page_text(html)

            pricing = detect_pricing(text)

            if pricing is None:
                return None

            return Product(
                source=Source(
                    name=startup["name"],
                    url=url
                ),
                content=ProductContent(
                    startupName=startup["name"],
                    pricingModel=pricing
                ),
                collectedAt=datetime.now(
                    timezone.utc
                )
            )

    except Exception:
        return None


async def main():
    with open(
        "data/output/startups.json",
        "r",
        encoding="utf-8"
    ) as file:
        startups = json.load(file)

    print(
        "Startups to check:",
        len(startups)
    )

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    connector = aiohttp.TCPConnector(
        limit=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector
    ) as session:

        tasks = [
            fetch_product(
                session,
                startup
            )
            for startup in startups
        ]

        results = await asyncio.gather(
            *tasks
        )

    products = [
        product.model_dump(mode="json")
        for product in results
        if product is not None
    ]

    print(
        "Verified products:",
        len(products)
    )

    output_dir = Path(
        "data/output"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir / "products.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            products,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        "Saved:",
        output_file
    )


if __name__ == "__main__":
    asyncio.run(main())