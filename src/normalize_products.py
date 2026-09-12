import json
import os
from datetime import datetime, timezone


INPUT_FILE = "data/output/futurepedia_tools.json"
OUTPUT_FILE = "data/output/products.json"


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        products = json.load(file)

    normalized = []

    for product in products:
        source_url = product.get("sourceUrl")
        product_name = product.get("name")

        record = {
            "schemaVersion": "1.0",
            "recordType": "PRODUCT",
            "source": {
                "name": "Futurepedia",
                "url": source_url
            },
            "content": {
                "startupName": None,
                "pricingModel": product.get("pricingModel")
            },
            "productName": product_name,
            "category": product.get("category"),
            "collectedAt": product.get(
                "collectedAt",
                datetime.now(timezone.utc).isoformat()
            )
        }

        normalized.append(record)

    os.makedirs("data/output", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            normalized,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Products normalized: {len(normalized)}")
    print(f"Saved: {OUTPUT_FILE}")

    with_startup = sum(
        1
        for product in normalized
        if product["content"]["startupName"]
    )

    print(f"Products with verified startup: {with_startup}")
    print(
        f"Products without startup mapping: "
        f"{len(normalized) - with_startup}"
    )


if __name__ == "__main__":
    main()