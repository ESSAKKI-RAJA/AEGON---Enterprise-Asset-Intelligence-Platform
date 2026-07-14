import json
import logging
from typing import Any, Optional
from redis.asyncio import Redis
from app.core.config import settings
from app.repositories.base import CacheHook
logger = logging.getLogger(__name__)

# Global redis instance for caching
_redis_cache: Optional[Redis] = None

async def get_cache() -> Redis:
    global _redis_cache
    if not _redis_cache:
        _redis_cache = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_cache

class CacheService:
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        if not settings.REDIS_URL:
            return None
        try:
            cache = await get_cache()
            val = await cache.get(key)
            if val:
                return json.loads(val)
            return None
        except Exception as e:
            logger.error(f"Redis get error for {key}: {e}")
            return None

    @staticmethod
    async def set(key: str, value: Any, ttl: int = 300) -> bool:
        """Set cache with TTL (default 5 mins)"""
        if not settings.REDIS_URL:
            return False
        try:
            cache = await get_cache()
            await cache.set(key, json.dumps(value), ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Redis set error for {key}: {e}")
            return False

    @staticmethod
    async def delete(key: str) -> bool:
        if not settings.REDIS_URL:
            return False
        try:
            cache = await get_cache()
            await cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error for {key}: {e}")
            return False

    @staticmethod
    async def clear_pattern(pattern: str) -> bool:
        """Clear all keys matching pattern (e.g. 'users:*')"""
        if not settings.REDIS_URL:
            return False
        try:
            cache = await get_cache()
            cursor = '0'
            while cursor != 0:
                cursor, keys = await cache.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    await cache.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Redis clear pattern error for {pattern}: {e}")
            return False

class RedisCacheHook(CacheHook):
    """Implementation of CacheHook for repository integration."""
    
    async def invalidate(self, entity_type: str, entity_id: Any):
        await CacheService.delete(f"{entity_type}:{entity_id}")
    
    async def invalidate_pattern(self, pattern: str):
        await CacheService.clear_pattern(pattern)
    
    async def get(self, key: str) -> Optional[Any]:
        return await CacheService.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        await CacheService.set(key, value, ttl)
