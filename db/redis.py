import logging

from redis import Redis

from config import settings

try:
    redis_client = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30,
    )
except Exception as e:
    logging.error(f"Failed to connect to Redis: {e}")
    raise RuntimeError("Failed to connect to Redis")
