
import os
import sys
from dotenv import load_dotenv

# Import Google Generative AI library
try:
    import google.generativeai as genai
except Exception:
    genai = None

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.5-flash"


def configure_client(api_key: str):
    """Configure Google Gemini client."""
    if genai is None:
        raise RuntimeError("google.generativeai not installed. Run: pip install google-generativeai")

    genai.configure(api_key=api_key)
    return genai


def post(prompt: str, model: str = MODEL_NAME):
    """Send prompt to Gemini and return raw response."""
    client = configure_client(API_KEY)
    response = client.GenerativeModel(model).generate_content(prompt)
    return response


def get(response):
    """Extract plain text from Gemini response."""
    if not response:
        return ""
    if hasattr(response, "text"):
        return response.text
    return str(response)


def main():
    if not API_KEY:
        print("ERROR: No API key found. Please add GOOGLE_API_KEY in your .env file.")
        sys.exit(1)

    # Read prompt from terminal or command line
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("Enter your prompt: ").strip()

    if not prompt:
        print("No prompt provided.")
        sys.exit(0)

    print("\nSending prompt to Gemini Flash 2.5...\n")
    try:
        resp = post(prompt)
        text = get(resp)
        print("=== Gemini Response ===")
        print(text)
        print("=======================")
    except Exception as e:
        print("Error communicating with Gemini:", e)
        sys.exit(2)


if __name__ == "__main__":
    main()
