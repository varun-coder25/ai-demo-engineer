import json
import os
import random
import time

import requests
from dotenv import load_dotenv

load_dotenv()


class LLMOrchestrator:
    def __init__(self):
        self.providers = [
            {
                "name": "gemini",
                "key": os.getenv("GEMINI_API_KEY"),
                "model": "gemini-3.5-flash"
            },
            {
                "name": "groq",
                "key": os.getenv("GROQ_API_KEY"),
                "model": "openai/gpt-oss-120b"
            },
            {
                "name": "deepseek",
                "key": os.getenv("DEEPSEEK_API_KEY"),
                "model": "deepseek-chat"
            }
        ]

    def chunk_text(self, text, max_chars=8000):
        if len(text) <= max_chars:
            return [text]

        paragraphs = text.split("\n")
        chunks = []
        current = ""

        for paragraph in paragraphs:
            if len(current) + len(paragraph) + 1 <= max_chars:
                current += paragraph + "\n"
            else:
                if current:
                    chunks.append(current.strip())
                current = paragraph + "\n"

        if current:
            chunks.append(current.strip())

        return chunks

    def build_prompt(self, text):
        return f"""
Extract structured information from the text below.

Return ONLY valid JSON.
Do not use markdown.
Do not invent information.
If a field is not present, use null.
Preserve names, dates and URLs exactly when they are available.

Required JSON format:
{{
    "title": null,
    "text": null,
    "date": null,
    "company": null,
    "source_url": null
}}

TEXT:
{text}
"""

    def call_gemini(self, prompt):
        key = self.providers[0]["key"]

        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-3.5-flash:generateContent"
            f"?key={key}"
        )

        response = requests.post(
            url,
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            },
            timeout=60
        )

        if response.status_code == 429:
            raise RuntimeError("429")

        if response.status_code == 413:
            raise RuntimeError("413")

        response.raise_for_status()

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def call_groq(self, prompt):
        key = self.providers[1]["key"]

        url = "https://api.groq.com/openai/v1/chat/completions"

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0
            },
            timeout=60
        )

        if response.status_code == 429:
            raise RuntimeError("429")

        if response.status_code == 413:
            raise RuntimeError("413")

        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def call_deepseek(self, prompt):
        key = self.providers[2]["key"]

        url = "https://api.deepseek.com/chat/completions"

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0
            },
            timeout=60
        )

        if response.status_code == 429:
            raise RuntimeError("429")

        if response.status_code == 413:
            raise RuntimeError("413")

        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def call_provider(self, provider_name, prompt):
        if provider_name == "gemini":
            return self.call_gemini(prompt)

        if provider_name == "groq":
            return self.call_groq(prompt)

        if provider_name == "deepseek":
            return self.call_deepseek(prompt)

        raise ValueError(f"Unknown provider: {provider_name}")

    def parse_json(self, response):
        response = response.strip()

        if response.startswith("```"):
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

        return json.loads(response)

    def generate(self, text):
        chunks = self.chunk_text(text)
        results = []

        for chunk in chunks:
            current_chunk = chunk

            while True:
                prompt = self.build_prompt(current_chunk)
                result = None
                request_too_large = False

                for provider in self.providers:
                    if not provider["key"]:
                        continue

                    for attempt in range(3):
                        try:
                            print(
                                f"Trying {provider['name']} "
                                f"(attempt {attempt + 1})"
                            )

                            response = self.call_provider(
                                provider["name"],
                                prompt
                            )

                            result = self.parse_json(response)
                            break

                        except RuntimeError as error:
                            if str(error) == "429":
                                delay = (
                                    (2 ** attempt)
                                    + random.uniform(0, 1)
                                )

                                print(
                                    f"{provider['name']} rate limited. "
                                    f"Retrying in {delay:.2f}s"
                                )

                                time.sleep(delay)

                            elif str(error) == "413":
                                print(
                                    f"{provider['name']} request too large."
                                )

                                request_too_large = True
                                break

                            else:
                                break

                        except (
                            requests.RequestException,
                            json.JSONDecodeError
                        ) as error:
                            print(
                                f"{provider['name']} failed: {error}"
                            )

                            break

                    if result is not None:
                        break

                    if request_too_large:
                        break

                if result is not None:
                    results.append(result)
                    break

                if request_too_large and len(current_chunk) > 1000:
                    new_size = max(
                        1000,
                        len(current_chunk) // 2
                    )

                    print(
                        f"Reducing chunk size from "
                        f"{len(current_chunk)} to {new_size}"
                    )

                    smaller_chunks = self.chunk_text(
                        current_chunk,
                        max_chars=new_size
                    )

                    for smaller_chunk in smaller_chunks:
                        smaller_result = self.generate(
                            smaller_chunk
                        )

                        results.extend(smaller_result)

                    break

                raise RuntimeError(
                    "All LLM providers failed for this chunk."
                )

        return results


if __name__ == "__main__":
    orchestrator = LLMOrchestrator()

    test_text = """
    OpenAI announced a new AI research initiative on September 11, 2026.
    The company said the project focuses on improving artificial intelligence.
    """

    result = orchestrator.generate(test_text)

    print("\nFinal result:")
    print(json.dumps(result, indent=2))