import httpx
import asyncio
import logging
from typing import Any, Dict, Optional, Union, List
from .ConfigOpenAI import OpenAISettings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class OpenAIClient:

    def __init__(self, settings: Optional[OpenAISettings] = None):
        """Initialize OpenAI client with settings.
        
        Args:
            settings: OpenAI configuration settings. If None, uses defaults from environment.
        """
        self.settings       = settings or OpenAISettings()
        self._client        = httpx.AsyncClient(
                base_url = str(self.settings.base_url),
                timeout  = float(self.settings.timeout),
                headers={
                    "Authorization": f"Bearer {str(self.settings.api_key)}",
                    "Content-Type": "application/json",
                }
        )
        self.max_retries    = int(self.settings.max_retries)
        self.backoff_factor = float(self.settings.backoff_factor)
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert, wise, and playful AI mentor. "
                    "You explain technical and scientific ideas clearly, with curiosity and intelligence. "
                    "You never produce hallucinations; if unsure, you say you don’t know. "
                    "You encourage critical thinking, prompt questions, and rigor."
                )
            }
        ]

    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        
        """
        Internal helper with retry/backoff logic.
        """

        # attempts: 0, 1, 2, … up to max_retries
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"OpenAI API request: {method} {path}")
                resp = await self._client.request(method, path, json=json, params=params)
                # Raise for HTTP error codes
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                # 429 (rate limit) or 500–599 are candidates for retry
                if attempt < self.max_retries and (status == 429 or 500 <= status < 600):
                    backoff = self.backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"OpenAIClient: request to {path} failed with status {status}, retrying after {backoff:.2f}s"
                    )
                    await asyncio.sleep(backoff)
                    continue
                # else, no more retries — rethrow
                logger.error(f"OpenAIClient: non-retriable error on {path}: {exc}")
                raise
            except (httpx.RequestError, httpx.TimeoutException) as exc:
                # network / timeout issues
                if attempt < self.max_retries:
                    backoff = self.backoff_factor * (2 ** attempt)
                    logger.warning(f"OpenAIClient: request error {exc}, retrying after {backoff:.2f}s")
                    await asyncio.sleep(backoff)
                    continue
                logger.error(f"OpenAIClient: request error final attempt {exc}")
                raise

    async def chat_completion(
        self,
        query:str ='',
        model: str = 'gpt-4.1-nano',
        temperature: float = 0.85,
        return_only_answer: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], str]:
        
        """
        Call the chat completions endpoint.
        """

        self.messages.append({'role':'user', 'content': query})
        payload  = {
                "model": model,
                "messages": self.messages,
                "temperature": temperature,
            }
        payload.update(kwargs)
        result = await self._request("POST", self.settings.base_url + "chat/completions", json=payload)

        if return_only_answer:
            return result['choices'][0]['message']['content']

        return result

    async def embeddings(self, 
                         input: str = '',
                         model: str = 'text-embedding-3-small',
                         return_only_embeddings: bool = False,
                         **kwargs) -> Union[Dict[str, Any], List]:
        
        """
        Call the embeddings endpoint.
        """

        payload = {
            "model": model,
            "input": input,
        }
        payload.update(kwargs)
        result = await self._request("POST", self.settings.base_url + "embeddings", json=payload)

        if return_only_embeddings:
            return result['data'][0]['embedding']

        return result

    async def close(self):
        await self._client.aclose()

    def chat_completion_sync(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(self.chat_completion(*args, **kwargs))

    def embeddings_sync(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(self.embeddings(*args, **kwargs))
