import json
import os
import re
import unicodedata


INPUT_FILE = "data/output/futurepedia_tools.json"
OUTPUT_FILE = "data/output/entity_mapping.json"


KNOWN_ENTITIES = {
    "openai": "OpenAI",
    "openai inc": "OpenAI",
    "open ai": "OpenAI",
    "anthropic": "Anthropic",
    "anthropic ai": "Anthropic",
    "google deepmind": "Google DeepMind",
    "deepmind": "Google DeepMind",
    "microsoft": "Microsoft",
    "microsoft ai": "Microsoft",
    "meta": "Meta",
    "meta ai": "Meta",
    "xai": "xAI",
    "x ai": "xAI",
    "mistral": "Mistral AI",
    "mistral ai": "Mistral AI",
    "cohere": "Cohere",
    "hugging face": "Hugging Face",
    "huggingface": "Hugging Face",
    "perplexity": "Perplexity",
    "perplexity ai": "Perplexity",
    "scale ai": "Scale AI",
    "databricks": "Databricks",
    "nvidia": "NVIDIA",
    "stability ai": "Stability AI",
    "stability": "Stability AI",
    "runway": "Runway",
    "runway ml": "Runway",
    "character ai": "Character AI",
    "character.ai": "Character AI",
    "jasper": "Jasper",
    "jasper ai": "Jasper",
    "grammarly": "Grammarly",
    "cursor": "Cursor",
    "replit": "Replit",
    "midjourney": "Midjourney",
    "elevenlabs": "ElevenLabs",
    "eleven labs": "ElevenLabs"
}


def normalize_name(name):
    if not name:
        return ""

    name = unicodedata.normalize("NFKD", str(name))
    name = name.lower().strip()

    name = re.sub(
        r"\b(incorporated|inc|corp|corporation|llc|ltd|limited|co|company)\b",
        "",
        name
    )

    name = re.sub(r"[^a-z0-9]+", " ", name)
    name = re.sub(r"\s+", " ", name)

    return name.strip()


def resolve_entity(name):
    normalized = normalize_name(name)

    if normalized in KNOWN_ENTITIES:
        return KNOWN_ENTITIES[normalized], "known_alias"

    return None, "unresolved"


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        products = json.load(file)

    mappings = []

    for product in products:
        product_name = product.get("name", "")

        canonical_name, method = resolve_entity(product_name)

        mappings.append({
            "rawName": product_name,
            "canonicalName": canonical_name,
            "method": method,
            "sourceUrl": product.get("sourceUrl")
        })

    os.makedirs("data/output", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            mappings,
            file,
            indent=2,
            ensure_ascii=False
        )

    known_aliases = sum(
        1
        for mapping in mappings
        if mapping["method"] == "known_alias"
    )

    unresolved = len(mappings) - known_aliases

    print(f"Total mappings: {len(mappings)}")
    print(f"Known aliases resolved: {known_aliases}")
    print(f"Unresolved mappings: {unresolved}")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()