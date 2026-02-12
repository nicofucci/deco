import redis
import json
import functools
import os
from datetime import datetime, date, timedelta

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
REDIS_CONNECT_TIMEOUT = float(os.getenv("REDIS_CONNECT_TIMEOUT", "1"))

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

class RedisCache:
    def __init__(self):
        self.redis = None
        try:
            client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=REDIS_CONNECT_TIMEOUT,
            )
            client.ping()
            self.redis = client
        except Exception as exc:
            # No romper si Redis no está disponible en demo/lab.
            print(f"[cache] Redis no disponible, cache deshabilitado ({exc})")

    def cache(self, expire: int = 60):
        """
        Decorator to cache function results in Redis.
        expire: Expiration time in seconds.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.redis:
                    return func(*args, **kwargs)

                # Create a unique key based on function name and arguments
                # We skip 'db' and 'current_user'/dependencies from args for key generation if possible
                # For simplicity, we'll use a basic key generation strategy
                
                # Filter out complex objects like Session from kwargs for key generation
                key_kwargs = {k: v for k, v in kwargs.items() if not hasattr(v, 'query')} 
                key_args = [a for a in args if not hasattr(a, 'query')]
                
                key = f"cache:{func.__module__}:{func.__name__}:{str(key_args)}:{str(key_kwargs)}"
                
                try:
                    cached_val = self.redis.get(key)
                    if cached_val:
                        return json.loads(cached_val)
                except Exception as e:
                    print(f"[cache] Error leyendo cache: {e}")
                    return func(*args, **kwargs)
                
                result = func(*args, **kwargs)
                
                # Only cache if result is JSON serializable
                try:
                    self.redis.setex(key, timedelta(seconds=expire), json.dumps(result, cls=DateTimeEncoder))
                except Exception as e:
                    print(f"[cache] Error escribiendo cache: {e}")
                    
                return result
            return wrapper
        return decorator

cache_service = RedisCache()
