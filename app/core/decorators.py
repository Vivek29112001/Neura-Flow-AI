import time
import logging
import functools
from typing import Callable, Any

logger = logging.getLogger("NeuraFlow")

def log_execution(agent_name: str):
    """Auto logs when agent starts and finishes"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger.info(f"▶ Starting {agent_name}...")
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = round(time.time() - start, 2)
                logger.info(f"✅ {agent_name} done in {elapsed}s")
                return result
            except Exception as e:
                logger.error(f"❌ {agent_name} failed: {e}")
                return None
        return wrapper
    return decorator


def retry(max_attempts: int = 3, delay: float = 2.0):
    """Auto retries on failure"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"❌ All {max_attempts} attempts failed: {e}")
                        return None
                    logger.warning(f"⚠ Attempt {attempt}/{max_attempts} failed. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator


def timer(func: Callable) -> Callable:
    """Measures how long a function takes"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = round(time.time() - start, 2)
        logger.info(f"⏱ {func.__name__} completed in {elapsed}s")
        return result
    return wrapper


def safe_run(func: Callable) -> Callable:
    """Catches all errors — agent never crashes the whole system"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Safe run caught error in {func.__name__}: {e}")
            return None
    return wrapper