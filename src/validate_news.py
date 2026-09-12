import json
import os
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import News


INPUT_FILE = "data/output/news_normalized.json"
OUTPUT_FILE = "data/output/news_validated.json"


def parse_date(date_value):
    if not date_value:
        return None

    if isinstance(date_value, datetime):
        return date_value

    value = str(date_value).strip()

    formats = [
        "%B %d, %Y",
        "%b %d, %Y",
        "%b %d, %Y, %I:%M %p UTC",
        "%B %d, %Y, %I:%M %p UTC",
        "%A, %B %d"
    ]

    for date_format in formats:
        try:
            parsed = datetime.strptime(value, date_format)

            if date_format == "%A, %B %d":
                parsed = parsed.replace(
                    year=datetime.now(timezone.utc).year
                )

            return parsed.replace(tzinfo=timezone.utc)

        except ValueError:
            continue

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed

    except ValueError:
        pass

    try:
        return parsedate_to_datetime(value)

    except (TypeError, ValueError):
        return None


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    valid_records = []
    invalid_records = []

    for index, record in enumerate(records, start=1):
        try:
            parsed_date = parse_date(record.get("date"))

            if parsed_date is None:
                raise ValueError(
                    f"Could not parse date: {record.get('date')}"
                )

            record["date"] = parsed_date

            news = News(
                source=record["source"],
                content={
                    "title": record.get("title", "Unknown"),
                    "text": record.get("text", ""),
                    "date": parsed_date
                },
                collectedAt=datetime.now(timezone.utc)
            )

            valid_records.append(
                news.model_dump(mode="json")
            )

        except Exception as error:
            invalid_records.append({
                "index": index,
                "error": str(error)
            })

    os.makedirs("data/output", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            valid_records,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Total records: {len(records)}")
    print(f"Valid records: {len(valid_records)}")
    print(f"Invalid records: {len(invalid_records)}")
    print(f"Saved: {OUTPUT_FILE}")

    if invalid_records:
        print("\nInvalid records:")

        for record in invalid_records:
            print(
                f"Record {record['index']}: "
                f"{record['error']}"
            )


if __name__ == "__main__":
    main()