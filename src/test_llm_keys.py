import os
import requests
from dotenv import load_dotenv

load_dotenv()


def test_gemini():
    key = os.getenv("GEMINI_API_KEY")

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
                        {"text": "Reply with exactly: GEMINI_OK"}
                    ]
                }
            ]
        },
        timeout=30
    )

    print("Gemini:", response.status_code)

    if response.ok:
        data = response.json()
        print(data["candidates"][0]["content"]["parts"][0]["text"])
    else:
        print(response.text)


def test_groq():
    key = os.getenv("GROQ_API_KEY")

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
                    "content": "Reply with exactly: GROQ_OK"
                }
            ]
        },
        timeout=30
    )

    print("Groq:", response.status_code)

    if response.ok:
        data = response.json()
        print(data["choices"][0]["message"]["content"])
    else:
        print(response.text)


def test_deepseek():
    key = os.getenv("DEEPSEEK_API_KEY")

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
                    "content": "Reply with exactly: DEEPSEEK_OK"
                }
            ]
        },
        timeout=30
    )

    print("DeepSeek:", response.status_code)

    if response.ok:
        data = response.json()
        print(data["choices"][0]["message"]["content"])
    else:
        print(response.text)


if __name__ == "__main__":
    test_gemini()
    test_groq()
    test_deepseek()