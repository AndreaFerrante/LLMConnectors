import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator

load_dotenv()

class PerplexitySettings(BaseModel):
    """Configuration settings for Perplexity API client.
    
    Attributes:
        api_key: Perplexity API key (required)
        base_url: Base URL for Perplexity API
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff factor for retries
        poll_interval: Polling interval for async requests
    """

    api_key: str = Field(default="", description="Perplexity API key")
    base_url: str = Field(
        default=os.getenv('PPLX_API_BASE_URL', 'https://api.perplexity.ai/'),
        description="Base URL for Perplexity API"
    )
    timeout: float = Field(
        default=float(os.getenv('PPLX_TIMEOUT', '120')),
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=int(os.getenv('PPLX_MAX_RETRIES', '5')),
        description="Maximum number of retry attempts"
    )
    backoff_factor: float = Field(
        default=float(os.getenv('PPLX_BACKOFF_FACTOR', '2')),
        description="Exponential backoff factor for retries"
    )
    poll_interval: float = Field(
        default=float(os.getenv('PPLX_POLL_INTERVAL', '1')),
        description="Polling interval for async requests"
    )

    @model_validator(mode='after')
    def validate_api_key(self):
        """Validate that API key is provided either directly or via environment."""
        if not self.api_key:
            self.api_key = os.getenv('PPLX_API_KEY', '')
        if not self.api_key:
            raise ValueError(
                "PPLX_API_KEY must be provided either as parameter or environment variable"
            )
        return self
