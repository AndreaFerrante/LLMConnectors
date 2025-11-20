"""LLMConnectors - A unified Python client library for multiple LLM providers.

This package provides async-first API clients for:
- OpenAI (GPT models, embeddings)
- Anthropic Claude (chat completion)
- Perplexity (chat completion)

Features:
- Async/await support with httpx
- Automatic retry logic with exponential backoff
- Type-safe configuration with Pydantic
- Environment variable support
- Consistent API across providers
- Comprehensive error handling

Example:
    ```python
    import asyncio
    from llmconnectors import OpenAIClient, OpenAISettings
    
    async def main():
        settings = OpenAISettings(api_key="your-api-key")
        client = OpenAIClient(settings=settings)
        
        try:
            response = await client.chat_completion(
                query="Hello, how are you?",
                return_only_answer=True
            )
            print(response)
        finally:
            await client.close()
    
    asyncio.run(main())
    ```
"""

__version__ = "1.0.0"
__author__ = "Andrea Ferrante"
__license__ = "MIT"

# Import main classes for convenience
from .connectors import (
    OpenAIClient,
    AnthropicClient,
    PerplexityClient,
    OpenAISettings,
    AnthropicSettings,
    PerplexitySettings,
)

from .logger import setup_logging

__all__ = [
    # Clients
    "OpenAIClient",
    "AnthropicClient",
    "PerplexityClient",
    # Settings
    "OpenAISettings",
    "AnthropicSettings",
    "PerplexitySettings",
    # Utilities
    "setup_logging",
    # Metadata
    "__version__",
    "__author__",
    "__license__",
]
