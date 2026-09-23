import redis

from .config import Config


def build_client(config: Config) -> redis.Redis:
    """Build a Redis client backed by a connection pool.

    decode_responses=True keeps keys as plain str for pattern matching and
    logging; SCAN/DEL both operate fine on decoded keys.
    """
    pool = redis.ConnectionPool.from_url(config.redis_url, decode_responses=True)
    return redis.Redis(connection_pool=pool)
