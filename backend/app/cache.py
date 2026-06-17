"""
Tiny async-safe in-memory TTL cache.

Keeps the dependency footprint minimal. For multi-instance production you'd
swap this for Redis behind the same get/set interface.
"""
import asyncio
import time
from typing import Any, Callable, Optional


class TTLCache:
    def __init__(self, default_ttl: int = 60):
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = asyncio.Lock()
        self._default_ttl = default_ttl

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            expires_at, value = item
            if time.time() > expires_at:
                self._store.pop(key, None)
                return None
            return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        async with self._lock:
            self._store[key] = (time.time() + (ttl or self._default_ttl), value)

    async def get_or_set(
        self, key: str, factory: Callable, ttl: Optional[int] = None
    ) -> Any:
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await factory()
        if value is not None:
            await self.set(key, value, ttl)
        return value

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()


cache = TTLCache()
