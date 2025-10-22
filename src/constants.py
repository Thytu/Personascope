import os

from pydantic import SecretStr
from dotenv import load_dotenv


load_dotenv()


OPENROUTER_API_KEY = SecretStr(os.getenv("OPENROUTER_API_KEY"))

if OPENROUTER_API_KEY.get_secret_value() is None:
    raise ValueError("OPENROUTER_API_KEY is not set")
