from contextlib import contextmanager
from django_redis import get_redis_connection


@contextmanager
def redis_lock(key, timeout=20, blocking_timeout=20):
    """
    Lock distribuído no Redis por chave.
    Ideal para garantir exclusividade por worker_id.
    """

    redis_client = get_redis_connection("default")

    lock = redis_client.lock(
        f"lock:{key}",
        timeout=timeout,
        blocking_timeout=blocking_timeout
    )

    acquired = lock.acquire(blocking=True)

    try:
        yield
    finally:
        if acquired:
            lock.release()