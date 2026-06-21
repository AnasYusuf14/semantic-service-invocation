import os
from dotenv import load_dotenv

load_dotenv()


def get_openai_api_key():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY was not found in the .env file."
        )

    return api_key