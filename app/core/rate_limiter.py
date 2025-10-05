
from starlette import status
from starlette.exceptions import HTTPException

from app.core.redis import redis


async def rate_limiter(
        user_id: int,
        endpoint: str,
        limit: int = 10,
        period: int = 60,
):
    key = f"rate_limit {user_id}: {endpoint}"
    current = await redis.incr(key)

    if current == 1:
        await redis.expire(key, period)

    if current > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {limit} requests per {period} seconds."
        )