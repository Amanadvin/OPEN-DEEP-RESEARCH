import os
import requests
from openai import OpenAI

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
OPENAI_MODEL = "gpt-4o-mini"

def is_lm_studio_available(timeout=1.5):
    try:
        r = requests.post(
            LM_STUDIO_URL,
            json={
                "model": "local",
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 1
            },
            timeout=timeout,
        )
        return r.status_code == 200
    except:
        return False


def generate_response(messages):
    # 1️⃣ Try LM Studio first
    if is_lm_studio_available():
        try:
            r = requests.post(
                LM_STUDIO_URL,
                json={
                    "model": "local",
                    "messages": messages,
                    "temperature": 0.7
                },
                timeout=60,
            )
            data = r.json()
            return data["choices"][0]["message"]["content"], "LM Studio"
        except:
            pass

    # 2️⃣ Fallback to OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.7,
    )

    return completion.choices[0].message.content, "OpenAI"
