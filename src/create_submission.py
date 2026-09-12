import json
import os

import pandas as pd


OUTPUT_DIR = "data/output"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "final_submission.xlsx"
)


def load_json(filename):
    path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(path):
        print(f"Warning: {filename} not found")
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def flatten_startups(records):
    rows = []

    for record in records:
        content = record.get("content", {})
        source = record.get("source", {})

        rows.append({
            "schemaVersion": record.get("schemaVersion"),
            "recordType": record.get("recordType"),
            "entityName": content.get("entityName"),
            "employeeCount": content.get("employeeCount"),
            "sourceName": source.get("name"),
            "sourceUrl": source.get("url"),
            "collectedAt": record.get("collectedAt")
        })

    return rows


def flatten_products(records):
    rows = []

    for record in records:
        content = record.get("content", {})
        source = record.get("source", {})

        rows.append({
            "schemaVersion": record.get("schemaVersion"),
            "recordType": record.get("recordType"),
            "productName": record.get("productName"),
            "startupName": content.get("startupName"),
            "pricingModel": content.get("pricingModel"),
            "category": record.get("category"),
            "sourceName": source.get("name"),
            "sourceUrl": source.get("url"),
            "collectedAt": record.get("collectedAt")
        })

    return rows


def flatten_papers(records):
    rows = []

    for record in records:
        content = record.get("content", {})

        rows.append({
            "schemaVersion": record.get("schemaVersion"),
            "recordType": record.get("recordType"),
            "title": content.get("title"),
            "authors": ", ".join(content.get("authors", [])),
            "paper_url": content.get("paper_url"),
            "github_url": content.get("github_url"),
            "github_stars": content.get("github_stars"),
            "published_date": content.get("published_date"),
            "collectedAt": record.get("collectedAt")
        })

    return rows


def flatten_jobs(records):
    rows = []

    for record in records:
        content = record.get("content", {})

        rows.append({
            "schemaVersion": record.get("schemaVersion"),
            "recordType": record.get("recordType"),
            "company": content.get("company"),
            "date": content.get("date"),
            "is_remote": content.get("is_remote"),
            "role_family": content.get("role_family"),
            "collectedAt": record.get("collectedAt")
        })

    return rows


def flatten_news(records):
    rows = []

    for record in records:
        content = record.get("content", {})
        source = record.get("source", {})

        rows.append({
            "schemaVersion": record.get("schemaVersion"),
            "recordType": record.get("recordType"),
            "title": content.get("title"),
            "text": content.get("text"),
            "date": content.get("date"),
            "sourceName": source.get("name"),
            "sourceUrl": source.get("url"),
            "collectedAt": record.get("collectedAt")
        })

    return rows


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    startups = load_json("startups.json")
    products = load_json("products.json")
    papers = load_json("research_papers.json")
    jobs = load_json("jobs_final.json")
    news = load_json("news_validated.json")
    entity_mapping = load_json("entity_mapping.json")

    sheets = {
        "Startups": flatten_startups(startups),
        "Products": flatten_products(products),
        "Research Papers": flatten_papers(papers),
        "Jobs": flatten_jobs(jobs),
        "News": flatten_news(news),
        "Entity Mapping Log": entity_mapping
    }

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl"
    ) as writer:

        for sheet_name, rows in sheets.items():
            dataframe = pd.DataFrame(rows)

            if dataframe.empty:
                dataframe = pd.DataFrame(
                    [{"status": "No records"}]
                )

            dataframe.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )

    print(f"Saved: {OUTPUT_FILE}")

    print("\nSheet counts:")

    for sheet_name, rows in sheets.items():
        print(f"{sheet_name}: {len(rows)}")


if __name__ == "__main__":
    main()