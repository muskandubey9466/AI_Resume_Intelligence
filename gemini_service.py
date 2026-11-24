
import os
import time
import random

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

PRIMARY_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

FALLBACK_MODEL = os.getenv(
    "GEMINI_FALLBACK_MODEL",
    "gemini-3.8-flash"
)


def get_gemini_client():

    if not API_KEY:
        raise ValueError(
            "Gemini API key not found in .env"
        )

    return genai.Client(api_key=API_KEY)


def generate_ai_response(prompt, retries=2):

    client = get_gemini_client()

    models = list(dict.fromkeys([
        PRIMARY_MODEL,
        FALLBACK_MODEL
    ]))

    last_error = None

    for model in models:

        for attempt in range(retries):

            try:

                print(f"Trying Gemini model: {model}")

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response.text:
                    return response.text.strip()

                raise ValueError(
                    "Gemini returned an empty response."
                )

            except errors.APIError as error:

                last_error = error

                if error.code == 503:

                    print(
                        f"{model} is overloaded."
                    )

                    if attempt < retries - 1:

                        wait_time = (
                            2 ** attempt
                            + random.uniform(0, 1)
                        )

                        time.sleep(wait_time)

                    continue

                elif error.code in [429, 500, 502, 504]:

                    if attempt < retries - 1:

                        time.sleep(2 ** attempt)

                    continue

                else:
                    raise RuntimeError(
                        f"Gemini API Error: {error}"
                    )

    raise RuntimeError(
        "Both Gemini models are currently unavailable. "
        "Please try again after some time. "
        f"Last error: {last_error}"
    )
