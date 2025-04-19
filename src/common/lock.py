from django.core.cache import cache


def acquire_lock(key: str, timeout: int) -> bool:
    return cache.add(key, "locked", timeout)
