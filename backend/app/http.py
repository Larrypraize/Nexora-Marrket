"""
Shared async HTTP client with retry, timeout and graceful error handling.

A single httpx.AsyncClient is reused across the app for connection pooling.
"""
import asyncio
import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger("nexora.http")

_client: Optional[httpx.AsyncClient] = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(12.0, connect=6.0),
            headers={"User-Agent": "NexoraMarket/1.0 (+https://nexora.market)"},
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        )
    return _client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


class ProviderError(Exception):
    """Raised when an upstream provider call fails after retries."""

    def __init__(self, provider: str, message: str, status: int | None = None):
        self.provider = provider
        self.status = status
        super().__init__(f"[{provider}] {message}")


async def fetch_json(
    provider: str,
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    retries: int = 2,
) -> Any:
    """GET JSON with retries and exponential backoff. Raises ProviderError."""
    client = get_client()
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 429:
                # Rate limited — back off and retry
                wait = 1.5 * (attempt + 1)
                logger.warning("%s rate limited, retrying in %.1fs", provider, wait)
                await asyncio.sleep(wait)
                last_exc = ProviderError(provider, "rate limited", 429)
                continue
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            last_exc = ProviderError(
                provider, f"HTTP {e.response.status_code}", e.response.status_code
            )
            if e.response.status_code < 500:
                break  # client error — don't retry
        except (httpx.RequestError, ValueError) as e:
            last_exc = ProviderError(provider, str(e))
        if attempt < retries:
            await asyncio.sleep(0.6 * (attempt + 1))
    raise last_exc or ProviderError(provider, "unknown error")
