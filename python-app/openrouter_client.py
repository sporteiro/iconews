import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "openrouter/free"

class OpenRouterClient:
    def __init__(self, api_key=None, url=None, model=None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.url = url or OPENROUTER_URL
        self.model = model or AI_MODEL
        if not self.api_key:
            raise EnvironmentError("OPENROUTER_API_KEY not found in .env")
        self.cache = {}
        self._client = None

    async def _get_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15.0)
        return self._client

    async def get_icon_keywords(self, title: str) -> list:
        cache_key = title.strip().lower()
        if cache_key in self.cache:
            return self.cache[cache_key]

        prompt = (
            "You are a visual icon selector for a news app. "
            "You have access to all icons available on Iconify. "
            "Given a news headline, return a JSON array of 1 to 7 English single-word keywords "
            "that best represent the news content visually and have clear, unambiguous icon representations. "
            "Resolve word sense according to news context (e.g., 'Pope' for 'Papa' when it refers to the Vatican, "
            "not 'patata'). Use common English words for clarity. "
            "Example: 'The Pope met with President Biden' -> ['pope', 'president', 'meeting'].\n\n"
            f"Headline: {title}\n"
            "Output only the JSON array, nothing else."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
            "temperature": 0.3,
        }

        try:
            client = await self._get_client()
            response = await client.post(self.url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            keywords = json.loads(content)
            if isinstance(keywords, list) and 1 <= len(keywords) <= 7:
                self.cache[cache_key] = keywords
                return keywords
            else:
                return []
        except Exception:
            return []

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None