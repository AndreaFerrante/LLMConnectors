# LLMConnectors

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/llmconnectors.svg)](https://badge.fury.io/py/llmconnectors)

A unified, production-ready Python client library for multiple LLM providers with async support, automatic retry logic, and comprehensive type safety.

## Features

- 🚀 **Async-First Design**: Built on `httpx` for high-performance async/await operations
- 🔄 **Automatic Retry Logic**: Exponential backoff for transient failures (rate limits, network issues)
- 🛡️ **Type Safe**: Full Pydantic validation for configurations and responses
- 🔌 **Multiple Providers**: Unified interface for OpenAI, Anthropic Claude, and Perplexity
- ⚙️ **Flexible Configuration**: Environment variables or direct instantiation
- 📝 **Conversation Memory**: Built-in message history management
- 🐍 **Modern Python**: Supports Python 3.9+

## Supported Providers

| Provider | Chat Completion | Embeddings | Streaming |
|----------|----------------|------------|-----------|
| OpenAI | ✅ | ✅ | 🔜 |
| Anthropic Claude | ✅ | ❌ | 🔜 |
| Perplexity | ✅ | ❌ | 🔜 |

## Installation

```bash
pip install llmconnectors
```

### Development Installation

```bash
git clone https://github.com/yourusername/llmconnectors.git
cd llmconnectors
pip install -e ".[dev]"
```

## Quick Start

### OpenAI

```python
import asyncio
from llmconnectors import OpenAIClient, OpenAISettings

async def main():
    # Option 1: Use environment variables (OPENAI_API_KEY)
    client = OpenAIClient()
    
    # Option 2: Direct configuration
    settings = OpenAISettings(api_key="sk-...")
    client = OpenAIClient(settings=settings)
    
    try:
        # Chat completion
        response = await client.chat_completion(
            query="Explain quantum computing in simple terms",
            model="gpt-4",
            temperature=0.7,
            return_only_answer=True
        )
        print(response)
        
        # Get embeddings
        embeddings = await client.embeddings(
            input="Hello world",
            model="text-embedding-3-small",
            return_only_embeddings=True
        )
        print(f"Embedding dimension: {len(embeddings)}")
        
    finally:
        await client.close()

asyncio.run(main())
```

### Anthropic Claude

```python
import asyncio
from llmconnectors import AnthropicClient, AnthropicSettings

async def main():
    settings = AnthropicSettings(api_key="sk-ant-...")
    client = AnthropicClient(settings=settings)
    
    try:
        response = await client.chat_completion(
            query="Write a haiku about Python programming",
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            temperature=0.8
        )
        print(response['content'][0]['text'])
        
    finally:
        await client.close()

asyncio.run(main())
```

### Perplexity

```python
import asyncio
from llmconnectors import PerplexityClient, PerplexitySettings

async def main():
    settings = PerplexitySettings(api_key="pplx-...")
    client = PerplexityClient(settings=settings)
    
    try:
        response = await client.chat_completion(
            query="What are the latest developments in AI?",
            model="sonar-pro"
        )
        print(response['choices'][0]['message']['content'])
        
    finally:
        await client.close()

asyncio.run(main())
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_API_BASE=https://api.openai.com/v1/
OPENAI_TIMEOUT=120
OPENAI_MAX_RETRIES=5
OPENAI_BACKOFF_FACTOR=2

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_API_BASE_URL=https://api.anthropic.com/v1/
ANTHROPIC_API_VERSION=2023-06-01
ANTHROPIC_TIMEOUT=120
ANTHROPIC_MAX_RETRIES=5
ANTHROPIC_BACKOFF_FACTOR=2

# Perplexity
PPLX_API_KEY=pplx-...
PPLX_API_BASE_URL=https://api.perplexity.ai/
PPLX_TIMEOUT=120
PPLX_MAX_RETRIES=5
PPLX_BACKOFF_FACTOR=2
PPLX_POLL_INTERVAL=1
```

### Programmatic Configuration

```python
from llmconnectors import OpenAISettings

settings = OpenAISettings(
    api_key="sk-...",
    base_url="https://api.openai.com/v1/",
    timeout=120.0,
    max_retries=5,
    backoff_factor=2.0
)
```

## Advanced Usage

### Custom System Prompts (Anthropic)

```python
client = AnthropicClient(
    system_prompt="You are a helpful coding assistant specialized in Python.",
    settings=settings
)
```

### Conversation History

All clients maintain conversation history automatically:

```python
# First message
await client.chat_completion(query="What is Python?")

# Follow-up (context preserved)
await client.chat_completion(query="What are its main features?")
```

### Synchronous Wrappers

If you need synchronous calls:

```python
from llmconnectors import OpenAIClient

client = OpenAIClient()
response = client.chat_completion_sync(query="Hello!")
```

### Error Handling

```python
import httpx
from llmconnectors import OpenAIClient

client = OpenAIClient()

try:
    response = await client.chat_completion(query="Test")
except httpx.HTTPStatusError as e:
    print(f"HTTP error: {e.response.status_code}")
except httpx.TimeoutException:
    print("Request timed out")
except ValueError as e:
    print(f"Configuration error: {e}")
finally:
    await client.close()
```

## API Reference

### OpenAIClient

#### Methods

- `chat_completion(query, model='gpt-4', temperature=0.85, return_only_answer=False, **kwargs)` 
  - Async chat completion
  - Returns: `Dict` or `str` (if `return_only_answer=True`)

- `embeddings(input, model='text-embedding-3-small', return_only_embeddings=False, **kwargs)`
  - Generate embeddings
  - Returns: `Dict` or `List[float]` (if `return_only_embeddings=True`)

- `close()`
  - Close the HTTP client connection

### AnthropicClient

#### Methods

- `chat_completion(query, model='claude-sonnet-4-5-20250929', max_tokens=4096, temperature=None, stop_sequences=None, **kwargs)`
  - Async chat completion
  - Returns: `Dict`

- `close()`
  - Close the HTTP client connection

### PerplexityClient

#### Methods

- `chat_completion(query, model='sonar')`
  - Async chat completion
  - Returns: `Dict`

- `close()`
  - Close the HTTP client connection

## Examples

Check the `examples/` directory for complete working examples:

- `examples/openai_basic.py` - Basic OpenAI usage
- `examples/anthropic_conversation.py` - Multi-turn conversation
- `examples/perplexity_research.py` - Research queries
- `examples/error_handling.py` - Comprehensive error handling
- `examples/batch_processing.py` - Process multiple requests

## Development

### Running Tests

```bash
pytest tests/ -v --cov=llmconnectors
```

### Code Formatting

```bash
black llmconnectors/
isort llmconnectors/
```

### Type Checking

```bash
mypy llmconnectors/
```

### Linting

```bash
ruff check llmconnectors/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- All tests pass
- Code is formatted with Black
- Type hints are included
- Documentation is updated

## Roadmap

- [ ] Streaming support for all providers
- [ ] Google Gemini integration
- [ ] Token usage tracking and cost estimation
- [ ] Rate limiting and queuing
- [ ] Caching layer
- [ ] Structured output validation
- [ ] Function calling support
- [ ] More comprehensive examples

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [httpx](https://www.python-httpx.org/) for robust async HTTP
- Configuration powered by [Pydantic](https://docs.pydantic.dev/)
- Inspired by the need for a unified LLM client interface

## Support

- 📧 Email: nonicknamethankyou@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/AndreaFerrante/llmconnectors/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/AndreaFerrante/llmconnectors/discussions)

## Citation

If you use this library in your research or project, please cite:

```bibtex
@software{llmconnectors2025,
  author = {Ferrante, Andrea},
  title = {LLMConnectors: A Unified Python Client for Multiple LLM Providers},
  year = {2025},
  url = {https://github.com/yourusername/llmconnectors}
}
```

---

Made with ❤️ by Andrea Ferrante
