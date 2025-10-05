from datetime import timedelta


from app.core.redis import redis

ONLINE_USERS_KEY = "online_users"


async def set_user_online(user_id: int):
    """
    Mark a user as online.
    """
    # store in a hash with TTL
    await redis.hset(ONLINE_USERS_KEY, user_id, "online")
    await redis.expire(ONLINE_USERS_KEY, timedelta(minutes=5))

async def set_user_offline(user_id: int):
    """
    Remove a user from online users.
    """
    await redis.hdel(ONLINE_USERS_KEY, user_id)

async def get_online_users() -> list[int]:
    """
    Returns a list of online user IDs.
    """
    return [int(uid) for uid in await redis.hkeys(ONLINE_USERS_KEY)]