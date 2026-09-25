import os
import json
from decimal import Decimal

from dotenv import load_dotenv

load_dotenv()


def convert_for_json(value):
    """
    Converts MySQL Decimal and other non-JSON-friendly
    values into normal Python values.
    """

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, list):
        return [
            convert_for_json(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: convert_for_json(val)
            for key, val in value.items()
        }

    return value


def format_database_result(database_result):
    """
    Converts database results into clean JSON text
    before sending them to Gemini.
    """

    if database_result is None:
        return "No database result was provided."

    cleaned_result = convert_for_json(
        database_result
    )

    try:
        return json.dumps(
            cleaned_result,
            indent=2,
            ensure_ascii=False
        )
    except Exception:
        return str(cleaned_result)


def get_gemini_model():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    try:
        from google import genai

        client = genai.Client(
            api_key=api_key
        )

        return client

    except ImportError:

        raise RuntimeError(
            "Google Gemini SDK is not installed. "
            "Install it using: pip install google-genai"
        )


def generate_final_answer(
    question,
    database_result=None,
    policy_context=None
):
    """
    Uses Gemini to convert database/RAG information
    into a concise natural-language answer.

    Gemini is only called when this function is explicitly
    requested by the query engine.
    """

    database_text = format_database_result(
        database_result
    )

    if policy_context:
        policy_text = policy_context
    else:
        policy_text = (
            "No policy information was provided."
        )

    prompt = f"""
You are InsightFlow AI, an AI-powered customer
intelligence assistant.

Answer the user's question using ONLY the information
provided in the database result and policy context.

USER QUESTION:
{question}

DATABASE RESULT:
{database_text}

POLICY CONTEXT:
{policy_text}

INSTRUCTIONS:

1. Answer in natural human-readable language.
2. Never return raw Python dictionaries.
3. Never return Decimal(...) values.
4. Never return SQL queries unless the user explicitly
   asks for the SQL query.
5. Convert monetary values into Indian Rupees using ₹.
6. Keep the answer concise and useful.
7. Do not invent information that is not present
   in the provided data.
8. If the question asks for business insights, explain
   the insight briefly.
9. If multiple records are provided, summarize the
   important findings instead of dumping all records.
10. If the information is insufficient, clearly say so.

Return ONLY the final answer.
"""

    try:

        client = get_gemini_model()

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        answer = response.text.strip()

        if not answer:
            return (
                "I found the relevant information, "
                "but I couldn't generate a final answer."
            )

        return answer

    except Exception as e:

        print(
            "Gemini answer generation error:",
            e
        )

        return (
            "I found the relevant data, but the AI "
            "explanation service is temporarily unavailable."
        )