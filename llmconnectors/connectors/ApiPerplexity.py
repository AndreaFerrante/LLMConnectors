import httpx
import asyncio
import logging
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional
from .ConfigPerplexity import PerplexitySettings

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PerplexityClient:

    def __init__(self, settings: Optional[PerplexitySettings] = None):

        self.settings = settings or PerplexitySettings()
        self._client  = httpx.AsyncClient(
                base_url = str(self.settings.base_url),
                timeout  = int(self.settings.timeout),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {str(self.settings.api_key)}"
                },
        )
        self.max_retries    = int(self.settings.max_retries)
        self.backoff_factor = int(self.settings.backoff_factor)
        self.poll_interval  = int(self.settings.poll_interval)
        self.messages       = [
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

    async def _request(self, method: str, path: str, json: Optional[Dict] = None) -> Any:
        """
        Internal retry logic for HTTP calls.
        """

        for attempt in range(self.max_retries + 1):

            try:
                
                resp = await self._client.request(method, path, json=json)
                resp.raise_for_status()

                return resp.json()
            
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                
                if attempt < self.max_retries and (status == 429 or 500 <= status < 600):
                    backoff = self.backoff_factor * (2 ** attempt)
                    logger.warning(f"PerplexityClient: request to {path} failed ({status}), retrying in {backoff:.2f}s")
                    await asyncio.sleep(backoff)
                    continue
                logger.error(f"PerplexityClient: HTTP error on {path}: {status} — {exc}")
                raise

            except (httpx.RequestError, httpx.TimeoutException) as exc:
                if attempt < self.max_retries:
                    backoff = self.backoff_factor * (2 ** attempt)
                    logger.warning(f"PerplexityClient: network error {exc}, retrying in {backoff:.2f}s")
                    await asyncio.sleep(backoff)
                    continue
                logger.error(f"PerplexityClient: network error on final attempt: {exc}")
                raise

    async def chat_completion(
        self,
        query:str = '',
        model: str = 'sonar',
    ) -> str:
        
        """
        Submit an async chat completion request. Returns request_id.
        """

        self.messages.append({
            "role": "user",
            "content": query
        })

        payload = {
                "model": model,
                "messages": self.messages
            }

        resp = await self._request("POST", self.settings.base_url + "chat/completions", json=payload)
        return resp

    async def close(self):
        await self._client.aclose()

    def chat_completion_sync(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(self.chat_completion(*args, **kwargs))

    def submit_chat_completion_sync(self, *args, **kwargs) -> str:
        return asyncio.get_event_loop().run_until_complete(self.submit_chat_completion(*args, **kwargs))

    def get_chat_result_sync(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(self.get_chat_result(*args, **kwargs))
