import os

from pydantic import SecretStr
from dotenv import load_dotenv


load_dotenv()


SECRET_OPENROUTER_API_KEY = SecretStr(os.getenv("OPENROUTER_API_KEY"))

if SECRET_OPENROUTER_API_KEY.get_secret_value() is None:
    raise ValueError("OPENROUTER_API_KEY is not set")


MODELS_TO_ANALYZE = [
    # Mini / Flash
    # "google/gemini-2.5-flash-lite-preview-06-17",
    # "openai/gpt-4.1-mini",
    # "openai/gpt-5-mini",

    # "anthropic/claude-sonnet-4.5",
    "openai/gpt-4.1",
    # "openai/gpt-5",
    # "google/gemini-2.5-pro",
]

NUM_RUBRICS_PER_MODEL = 2
NUM_EVALUATIONS_PER_MODEL = 3
MAX_STD_DEVIATION = 1
