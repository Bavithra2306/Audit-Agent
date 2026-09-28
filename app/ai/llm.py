from openai import OpenAI

from app.config import settings


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)


MODEL_NAME = "dots-studio/dots-3-note-preview:free"