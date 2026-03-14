from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")

    langfuse_public_key: str = Field(default="", env="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(default="", env="LANGFUSE_SECRET_KEY")
    langfuse_base_url: str = Field(default="http://localhost:3000", env="LANGFUSE_BASE_URL")

    environment: str = Field(default="development", env="ENVIRONMENT")
    gradio_server_port: int = Field(default=7861, env="GRADIO_SERVER_PORT")
    gradio_server_name: str = Field(default="0.0.0.0", env="GRADIO_SERVER_NAME")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
