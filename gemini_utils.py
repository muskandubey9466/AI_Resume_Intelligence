
import os
import time
import streamlit as st

from google import genai


def screen_resume(prompt):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            raise ValueError(
                "Gemini API key not found. Check your .env file."
            )

    client = genai.Client(api_key=api_key)

    # Primary and fallback models
    models = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite"
    ]

    last_error = None

    for model in models:

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response.text:
                    return response.text

                raise ValueError("Gemini returned an empty response.")

            except Exception as e:

                last_error = e

                error_message = str(e)

                # Retry only temporary server/rate-limit errors
                if any(code in error_message for code in [
                    "503", "UNAVAILABLE",
                    "429", "RESOURCE_EXHAUSTED",
                    "500", "INTERNAL",
                    "504", "DEADLINE_EXCEEDED"
                ]):

                    if attempt < 2:

                        wait_time = 2 ** (attempt + 1)

                        time.sleep(wait_time)
                        continue

                    # Try the fallback model
                    break

                else:
                    raise RuntimeError(
                        f"Gemini API failed: {error_message}"
                    ) from e

    raise RuntimeError(
        "Gemini models are temporarily unavailable. "
        "Please try again after some time. "
        f"Last error: {last_error}"
    )
