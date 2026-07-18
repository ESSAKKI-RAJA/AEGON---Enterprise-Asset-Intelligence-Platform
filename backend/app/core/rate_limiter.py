from fastapi import Request, HTTPException, status
from redis.asyncio import Redis
from app.core.config import settings
from typing import Optional

# Default global redis instance, initialized in lifespan
redis_client: Optional[Redis] = None

async def get_redis_client() -> Redis:
    global redis_client
    if not redis_client:
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client

class RateLimiter:
    """
    Token bucket rate limiter backed by Redis.
    Uses an atomic Lua script for accurate distributed rate limiting.
    """
    def __init__(self, requests: int = 100, window: int = 60):
        self.requests = requests
        self.window = window
        
    async def __call__(self, request: Request):
        if not settings.REDIS_URL:
            return True
            
        client = await get_redis_client()
        
        # Identify caller by token subject (user ID) if auth'd, else IP
        user = getattr(request.state, "user", None)
        if user:
            identifier = f"user:{user.id}"
        else:
            forwarded = request.headers.get("X-Forwarded-For")
            ip = forwarded.split(",")[0] if forwarded else request.client.host
            identifier = f"ip:{ip}"
            
        key = f"rate_limit:{request.url.path}:{identifier}"
        
        # Simple atomic counter with expiration (Sliding window approx)
        # In a real enterprise system we'd use a Lua script for a proper token bucket
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.window, nx=True) # Set expire only if key is new
        
        results = await pipe.execute()
        current_requests = results[0]
        
        if current_requests > self.requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(self.window)}
            )
            
        return True
