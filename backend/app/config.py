import os

from dotenv import load_dotenv


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")


if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured.")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_URL = os.getenv(
    "GITHUB_API_URL",
    "https://api.github.com",
)