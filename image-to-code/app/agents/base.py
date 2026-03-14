from autogen_ext.models.openai import OpenAIChatCompletionClient
from app.config import settings


def get_model_client() -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
    )
