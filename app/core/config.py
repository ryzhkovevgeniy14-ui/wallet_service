import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL: str | None = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in .env")