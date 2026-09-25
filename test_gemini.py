from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", bool(api_key))

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=120000
    )
)

response = client.interactions.create(
    model="gemini-3.6-flash",
    input="Say hello in one sentence."
)

print(response.output_text)