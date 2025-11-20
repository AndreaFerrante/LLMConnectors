import httpx
import asyncio
import logging
from typing import Any, Dict, List, Optional
from .ConfigAnthropic import AnthropicSettings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AnthropicClient:

    def __init__(self, system_prompt: str = '', settings: Optional[AnthropicSettings] = None):

        '''
        ATTENTION: Anthropic does not accept as a role system (for system prompt).
                   It must be given as if system would be a payload parameter.
                   Look at payload defintion, below.

        See here (search for system): https://docs.claude.com/en/api/messages
        '''

        self.system_prompt  = system_prompt or self._get_claude_system_prompt()
        self.settings       = settings or AnthropicSettings()
        self._client        = httpx.AsyncClient(
                base_url = str(self.settings.base_url) or "https://api.anthropic.com/v1/",
                timeout  = int(self.settings.timeout),
                headers  = {
                            "x-api-key":         str(self.settings.api_key),
                            "anthropic-version": str(self.settings.version),
                            "Content-Type":      "application/json"
                        },
            )
        self.max_retries    = int(self.settings.max_retries)
        self.backoff_factor = int(self.settings.backoff_factor)
        self.messages       = list()

    def _get_claude_system_prompt(self):

        return (
                    f"You are an expert, wise, and playful AI mentor. "
                    f"You explain technical and scientific ideas clearly, with curiosity and intelligence. "
                    f"You never produce hallucinations; if unsure, you say you don’t know. "
                    f"You encourage critical thinking, prompt questions, and rigor."
                )

    async def _request(self, method: str, path: str, json: Optional[Dict] = None) -> Any:

        for attempt in range(self.max_retries + 1):

            try:
                logger.debug(f"Anthropic API request: {method} {path}")
                resp = await self._client.request(method, path, json=json)
                resp.raise_for_status()
                return resp.json()
            
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if attempt < self.max_retries and (status == 429 or 500 <= status < 600):
                    backoff = self.backoff_factor * (2 ** attempt)
                    logger.warning(f"Anthropic HTTP {method} {path} status {status}, retry in {backoff:.2f}s")
                    await asyncio.sleep(backoff)
                    continue
                logger.error(f"Anthropic HTTP error at {path}: {status} — {exc}")
                raise

            except (httpx.RequestError, httpx.TimeoutException) as exc:
                if attempt < self.max_retries:
                    backoff = self.backoff_factor * (2 ** attempt)
                    logger.warning(f"Anthropic request error {exc}, retry in {backoff:.2f}s")
                    await asyncio.sleep(backoff)
                    continue
                logger.error("Anthropic network error final attempt", exc_info=True)
                raise

    async def chat_completion(
        self,
        query: str,
        model: str = 'claude-sonnet-4-5-20250929',
        max_tokens: Optional[int] = 4096,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        
        self.messages.append(
            {
                "role": "user",
                "content": str(query)
            }
        )

        payload = {
            "model": model,
            "system": self.system_prompt,
            "messages": self.messages,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if stop_sequences is not None:
            payload["stop_sequences"] = stop_sequences
        payload.update(kwargs)

        logger.debug(f"Anthropic chat request with model: {model}")
        result = await self._request("POST", str(self.settings.base_url) + "messages", json=payload)

        return result

    async def close(self):
        await self._client.aclose()

    def chat_sync(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(self.chat(*args, **kwargs))
