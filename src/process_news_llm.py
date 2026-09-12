import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_orchestrator import LLMOrchestrator


INPUT_FILE = "data/output/news_final.json"
OUTPUT_FILE = "data/output/news_normalized.json"


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        news = json.load(file)

    orchestrator = LLMOrchestrator()
    normalized_news = []

    print(f"Processing {len(news)} news articles...\n")

    for index, article in enumerate(news, start=1):
        print(
            f"[{index}/{len(news)}] "
            f"{article.get('title', 'Unknown')}"
        )

        source_url = article.get(
            "url",
            article.get("source_url")
        )

        text = article.get("text", "")

        if not text:
            print("Skipped: no article text")
            continue

        try:
            results = orchestrator.generate(text)

            for result in results:
                result["source_url"] = source_url

                if not result.get("title"):
                    result["title"] = article.get("title")

                if not result.get("date"):
                    result["date"] = article.get("date")

                result["source"] = {
                    "name": article.get(
                        "source_name",
                        article.get("source", "Unknown")
                    ),
                    "url": source_url
                }

                normalized_news.append(result)

            print("Success")

        except Exception as error:
            print(f"Failed: {error}")

    os.makedirs("data/output", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            normalized_news,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\nSaved {len(normalized_news)} normalized records "
        f"to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()