import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator

load_dotenv()

class AnthropicSettings(BaseModel):
    """Configuration settings for Anthropic Claude API client.
    
    Attributes:
        api_key: Anthropic API key (required)
        base_url: Base URL for Anthropic API
        version: API version string
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff factor for retries
    """

    api_key: str = Field(default="", description="Anthropic API key")
    base_url: str = Field(
        default=os.getenv("ANTHROPIC_API_BASE_URL", "https://api.anthropic.com/v1/"),
        description="Base URL for Anthropic API"
    )
    version: str = Field(
        default=os.getenv("ANTHROPIC_API_VERSION", "2023-06-01"),
        description="API version string"
    )
    timeout: float = Field(
        default=float(os.getenv("ANTHROPIC_TIMEOUT", "120")),
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=int(os.getenv("ANTHROPIC_MAX_RETRIES", "5")),
        description="Maximum number of retry attempts"
    )
    backoff_factor: float = Field(
        default=float(os.getenv("ANTHROPIC_BACKOFF_FACTOR", "2")),
        description="Exponential backoff factor for retries"
    )

    @model_validator(mode='after')
    def validate_api_key(self):
        """Validate that API key is provided either directly or via environment."""
        if not self.api_key:
            self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY must be provided either as parameter or environment variable"
            )
        return self
