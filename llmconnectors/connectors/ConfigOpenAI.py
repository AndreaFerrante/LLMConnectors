import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator

load_dotenv()

class OpenAISettings(BaseModel):
    """Configuration settings for OpenAI API client.
    
    Attributes:
        api_key: OpenAI API key (required)
        base_url: Base URL for OpenAI API
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff factor for retries
    """

    api_key: str = Field(default="", description="OpenAI API key")
    base_url: str = Field(
        default=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1/'),
        description="Base URL for OpenAI API"
    )
    timeout: float = Field(
        default=float(os.getenv('OPENAI_TIMEOUT', '120')),
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=int(os.getenv('OPENAI_MAX_RETRIES', '5')),
        description="Maximum number of retry attempts"
    )
    backoff_factor: float = Field(
        default=float(os.getenv('OPENAI_BACKOFF_FACTOR', '2')),
        description="Exponential backoff factor for retries"
    )

    @model_validator(mode='after')
    def validate_api_key(self):
        """Validate that API key is provided either directly or via environment."""
        if not self.api_key:
            self.api_key = os.getenv('OPENAI_API_KEY', '')
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY must be provided either as parameter or environment variable"
            )
        return self
