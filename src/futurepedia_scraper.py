import asyncio
import json
import re
from datetime import datetime, timezone

from playwright.async_api import async_playwright


BASE_URL = "https://www.futurepedia.io"

TARGET = 1200


CATEGORIES = [
    "productivity",
    "business",
    "research-assistant",
    "code",
    "chatbots",
    "marketing",
    "ai-agents",
    "workflows",
    "image-generators",
    "image-editing",
    "design-generators",
    "text-to-image",
    "video-generators",
    "video-editing",
    "text-to-video",
    "writing-generators",
    "copywriting-assistant",
    "presentations",
    "personal-assistant",
    "project-management",
    "social-media",
    "finance",
    "website-builders",
    "audio-editing",
    "text-to-speech",
    "transcriber",
    "prompt-generators",
    "students",
    "fitness",
    "logo-generator",
    "education",
    "search-engine",
    "startup-assistant",
    "seo",
    "no-code",
    "sales-assistant",
    "fun-tools",
    "technology-and-it",
    "operations",
    "back-office",
    "growth-and-marketing"
]


PRICING = {
    "Free": "FREE",
    "Freemium": "FREEMIUM",
    "Free Trial": "FREEMIUM",
    "Paid": "PAID",
    "Contact for Pricing": "ENTERPRISE"
}


BAD_NAMES = {
    "why you can trust us",
    "ai tools",
    "filters",
    "trending",
    "popular",
    "new",
    "visit",
    "editor's pick",
    "featured",
    "get deal",
    "active deal",
    "home",
    "research",
    "spreadsheets",
    "translator",
    "search engine",
    "presentations",
    "marketing",
    "finance",
    "project management",
    "social media",
    "education",
    "e-commerce",
    "seo",
    "human resources",
    "sales assistant",
    "stock trading",
    "legal",
    "teachers",
    "startup tools",
    "real estate"
}


def normalize_name(name):
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-")


def is_bad_name(name):
    lower = name.lower().strip()

    if lower in BAD_NAMES:
        return True

    if len(name) > 100:
        return True

    if name.endswith("."):
        return True

    bad_phrases = [
        "with these ",
        "with ai-driven",
        "ai-powered ",
        "ai-driven ",
        "streamline ",
        "revolutionize ",
        "publish timely",
        "unleash insights",
        "task-specific ai apps",
        "the most powerful ai",
        "helps you quickly",
        "optimizing recruitment"
    ]

    for phrase in bad_phrases:
        if phrase in lower:
            return True

    return False


async def get_tool_links(page):
    links = await page.locator(
        "a[href*='/tool/']"
    ).evaluate_all(
        """
        elements => elements.map(element => ({
            href: element.href,
            text: element.innerText.trim()
        }))
        """
    )

    result = {}

    for link in links:
        href = link["href"]

        if "/tool/" not in href:
            continue

        slug = href.rstrip("/").split("/tool/")[-1]

        if slug:
            result[slug.lower()] = href

    return result


async def scrape_category(
    page,
    category,
    page_number
):
    url = (
        f"{BASE_URL}/ai-tools/"
        f"{category}?page={page_number}"
    )

    print(
        f"Fetching {category} "
        f"page {page_number}..."
    )

    try:
        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        await page.wait_for_timeout(2000)

    except Exception as error:
        print(
            f"Failed: {error}"
        )
        return []

    lines = await page.locator(
        "body"
    ).inner_text()

    lines = [
        line.strip()
        for line in lines.splitlines()
        if line.strip()
    ]

    tool_links = await get_tool_links(page)

    tools = []

    i = 0

    while i < len(lines):

        name = lines[i]

        if is_bad_name(name):
            i += 1
            continue

        if name.startswith("#"):
            i += 1
            continue

        pricing = None
        pricing_index = None

        for j in range(
            i + 1,
            min(i + 8, len(lines))
        ):
            if lines[j] in PRICING:
                pricing = PRICING[lines[j]]
                pricing_index = j
                break

        if pricing is None:
            i += 1
            continue

        section = " ".join(
            lines[i:pricing_index]
        )

        if "Rated" not in section:
            i += 1
            continue

        slug = normalize_name(name)

        source_url = tool_links.get(slug)

        if source_url is None:
            i += 1
            continue

        tools.append({
            "name": name,
            "pricingModel": pricing,
            "category": category,
            "sourceUrl": source_url,
            "collectedAt": datetime.now(
                timezone.utc
            ).isoformat()
        })

        i = pricing_index + 1

    return tools


def clean_existing_tools(tools):
    cleaned = {}
    removed = 0

    for tool in tools:

        name = tool.get("name", "").strip()
        source_url = tool.get("sourceUrl", "")
        pricing = tool.get("pricingModel")

        if not name:
            removed += 1
            continue

        if is_bad_name(name):
            removed += 1
            continue

        if not source_url:
            removed += 1
            continue

        if pricing not in [
            "FREE",
            "FREEMIUM",
            "PAID",
            "ENTERPRISE"
        ]:
            removed += 1
            continue

        key = name.lower()

        if key not in cleaned:
            cleaned[key] = tool
        else:
            removed += 1

    return list(cleaned.values()), removed


def save_tools(tools):
    with open(
        "data/output/futurepedia_tools.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            tools,
            file,
            indent=2,
            ensure_ascii=False
        )


async def main():

    try:
        with open(
            "data/output/futurepedia_tools.json",
            "r",
            encoding="utf-8"
        ) as file:
            existing = json.load(file)

    except FileNotFoundError:
        existing = []

    tools, removed = clean_existing_tools(
        existing
    )

    print(
        "Existing records:",
        len(existing)
    )

    print(
        "Removed bad records:",
        removed
    )

    print(
        "Clean records:",
        len(tools)
    )

    if len(tools) >= TARGET:
        print()
        print(
            f"Already have {len(tools)} "
            f"clean products."
        )
        save_tools(tools)
        return

    unique = {
        tool["name"].lower().strip(): tool
        for tool in tools
    }

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        try:

            for category in CATEGORIES:

                if len(unique) >= TARGET:
                    break

                seen_in_category = set()

                for page_number in range(1, 31):

                    if len(unique) >= TARGET:
                        break

                    tools_found = await scrape_category(
                        page,
                        category,
                        page_number
                    )

                    if not tools_found:
                        print(
                            f"  No more tools in "
                            f"{category}."
                        )
                        break

                    new_count = 0

                    for tool in tools_found:

                        name = tool["name"].strip()
                        key = name.lower()

                        if is_bad_name(name):
                            continue

                        if key in seen_in_category:
                            continue

                        seen_in_category.add(key)

                        if key not in unique:
                            unique[key] = tool
                            new_count += 1

                    print(
                        f"  Found {new_count} "
                        f"new clean tools"
                    )

                    print(
                        f"  Total clean: "
                        f"{len(unique)}/{TARGET}"
                    )

                    if new_count == 0:
                        break

                tools = list(unique.values())

                save_tools(tools)

                print(
                    f"  Saved progress: "
                    f"{len(tools)} records"
                )

        except KeyboardInterrupt:
            print()
            print("Stopped by user.")
            print(
                "Saving current progress..."
            )

        finally:
            tools = list(unique.values())
            save_tools(tools)
            await browser.close()

    print()
    print(
        "FINAL CLEAN COUNT:",
        len(tools)
    )

    print(
        "Saved: "
        "data/output/futurepedia_tools.json"
    )


if __name__ == "__main__":
    asyncio.run(main())