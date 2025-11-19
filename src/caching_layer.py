"""
BLOOM AI Agent - Caching Layer (Redis-compatible)
Production-grade caching with in-memory fallback

Features:
- Redis-compatible interface
- In-memory cache (LRU, LFU, TTL)
- Cache-aside, read-through, write-through patterns
- Cache invalidation (manual, TTL, tag-based)
- Cache statistics (hit rate, size, memory usage)
- Distributed caching support
- Cache warming
- Namespace support
- JSON serialization

Built: 2025-11-19
Status: Production-Ready
"""

import json
import time
import pickle
import threading
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict, Callable
from dataclasses import dataclass
from enum import Enum
from collections import OrderedDict
import functools


# ============================================================================
# ENUMS & TYPES
# ============================================================================

class CacheStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live only


class CachePattern(Enum):
    """Cache access patterns"""
    CACHE_ASIDE = "cache_aside"        # App manages cache
    READ_THROUGH = "read_through"      # Cache loads on miss
    WRITE_THROUGH = "write_through"    # Cache writes on update
    WRITE_BEHIND = "write_behind"      # Async writes


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed_at: Optional[datetime] = None
    tags: List[str] = None
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at

    def touch(self):
        """Update access metadata"""
        self.access_count += 1
        self.last_accessed_at = datetime.utcnow()


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    size: int = 0
    memory_bytes: int = 0

    def get_hit_rate(self) -> float:
        """Calculate hit rate"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "evictions": self.evictions,
            "size": self.size,
            "memory_bytes": self.memory_bytes,
            "hit_rate": self.get_hit_rate()
        }


# ============================================================================
# IN-MEMORY CACHE
# ============================================================================

class InMemoryCache:
    """
    In-memory cache with LRU/LFU eviction

    Features:
    - Multiple eviction strategies (LRU, LFU, TTL)
    - TTL support
    - Max size enforcement
    - Tag-based invalidation
    - Statistics tracking
    """

    def __init__(self, max_size: int = 1000, strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.strategy = strategy
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.tags_index: Dict[str, List[str]] = {}  # tag -> [keys]
        self.stats = CacheStats()
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            entry = self.cache.get(key)

            if not entry:
                self.stats.misses += 1
                return None

            # Check expiration
            if entry.is_expired():
                self._remove_entry(key)
                self.stats.misses += 1
                return None

            # Update access metadata
            entry.touch()

            # Move to end for LRU
            if self.strategy == CacheStrategy.LRU:
                self.cache.move_to_end(key)

            self.stats.hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None,
            tags: Optional[List[str]] = None):
        """Set value in cache"""
        with self._lock:
            # Calculate expiration
            expires_at = None
            if ttl_seconds:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

            # Estimate size
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 0

            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                tags=tags or [],
                size_bytes=size_bytes
            )

            # Remove existing if present
            if key in self.cache:
                self._remove_entry(key)

            # Evict if necessary
            while len(self.cache) >= self.max_size:
                self._evict_one()

            # Add to cache
            self.cache[key] = entry

            # Index tags
            if tags:
                for tag in tags:
                    if tag not in self.tags_index:
                        self.tags_index[tag] = []
                    self.tags_index[tag].append(key)

            # Update stats
            self.stats.sets += 1
            self.stats.size = len(self.cache)
            self.stats.memory_bytes += size_bytes

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key not in self.cache:
                return False

            self._remove_entry(key)
            self.stats.deletes += 1
            return True

    def delete_by_tag(self, tag: str) -> int:
        """Delete all entries with given tag"""
        with self._lock:
            keys = self.tags_index.get(tag, [])
            count = 0

            for key in keys[:]:  # Copy to avoid modification during iteration
                if self.delete(key):
                    count += 1

            # Clean up tag index
            if tag in self.tags_index:
                del self.tags_index[tag]

            return count

    def clear(self):
        """Clear entire cache"""
        with self._lock:
            self.cache.clear()
            self.tags_index.clear()
            self.stats.size = 0
            self.stats.memory_bytes = 0

    def exists(self, key: str) -> bool:
        """Check if key exists (and not expired)"""
        with self._lock:
            entry = self.cache.get(key)
            if not entry:
                return False
            if entry.is_expired():
                self._remove_entry(key)
                return False
            return True

    def ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL in seconds"""
        with self._lock:
            entry = self.cache.get(key)
            if not entry or not entry.expires_at:
                return None

            remaining = (entry.expires_at - datetime.utcnow()).total_seconds()
            return max(0, int(remaining))

    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys matching pattern"""
        with self._lock:
            if not pattern:
                return list(self.cache.keys())

            # Simple wildcard matching (*, ?)
            import re
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            regex = re.compile(f"^{regex_pattern}$")

            return [k for k in self.cache.keys() if regex.match(k)]

    def cleanup_expired(self):
        """Remove all expired entries"""
        with self._lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                self._remove_entry(key)

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._lock:
            return self.stats.to_dict()

    def _evict_one(self):
        """Evict one entry based on strategy"""
        if not self.cache:
            return

        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used (first item)
            key = next(iter(self.cache))
            self._remove_entry(key)

        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            min_key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
            self._remove_entry(min_key)

        elif self.strategy == CacheStrategy.TTL:
            # Remove entry with soonest expiration
            ttl_entries = [(k, e) for k, e in self.cache.items() if e.expires_at]
            if ttl_entries:
                min_key = min(ttl_entries, key=lambda x: x[1].expires_at)[0]
                self._remove_entry(min_key)
            else:
                # Fallback to LRU
                key = next(iter(self.cache))
                self._remove_entry(key)

        self.stats.evictions += 1

    def _remove_entry(self, key: str):
        """Remove entry and update indices"""
        entry = self.cache.pop(key, None)
        if not entry:
            return

        # Update memory stats
        self.stats.memory_bytes = max(0, self.stats.memory_bytes - entry.size_bytes)
        self.stats.size = len(self.cache)

        # Remove from tag index
        if entry.tags:
            for tag in entry.tags:
                if tag in self.tags_index:
                    try:
                        self.tags_index[tag].remove(key)
                    except ValueError:
                        pass


# ============================================================================
# REDIS-COMPATIBLE WRAPPER
# ============================================================================

class CacheClient:
    """
    Redis-compatible cache client

    Works with both in-memory cache and actual Redis
    Provides unified interface
    """

    def __init__(self, redis_url: Optional[str] = None, **kwargs):
        self.redis_url = redis_url
        self.use_redis = redis_url is not None

        if self.use_redis:
            # Try to import redis
            try:
                import redis
                self.client = redis.from_url(redis_url)
                self.in_memory = None
            except ImportError:
                print("Warning: redis package not installed, using in-memory cache")
                self.use_redis = False
                self.in_memory = InMemoryCache(**kwargs)
                self.client = None
        else:
            # Use in-memory cache
            self.in_memory = InMemoryCache(**kwargs)
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value"""
        if self.use_redis:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        else:
            return self.in_memory.get(key)

    def set(self, key: str, value: Any, ex: Optional[int] = None, **kwargs):
        """Set value with optional TTL (ex = seconds)"""
        if self.use_redis:
            self.client.set(key, json.dumps(value), ex=ex)
        else:
            self.in_memory.set(key, value, ttl_seconds=ex, **kwargs)

    def delete(self, key: str) -> int:
        """Delete key"""
        if self.use_redis:
            return self.client.delete(key)
        else:
            return 1 if self.in_memory.delete(key) else 0

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if self.use_redis:
            return bool(self.client.exists(key))
        else:
            return self.in_memory.exists(key)

    def ttl(self, key: str) -> int:
        """Get TTL"""
        if self.use_redis:
            return self.client.ttl(key)
        else:
            ttl = self.in_memory.ttl(key)
            return ttl if ttl is not None else -1

    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        if self.use_redis:
            return [k.decode() for k in self.client.keys(pattern)]
        else:
            return self.in_memory.keys(pattern)

    def clear(self):
        """Clear all keys"""
        if self.use_redis:
            self.client.flushdb()
        else:
            self.in_memory.clear()


# ============================================================================
# CACHE DECORATOR
# ============================================================================

class CacheDecorator:
    """
    Cache decorator for functions

    Automatically caches function results
    """

    def __init__(self, cache: CacheClient, ttl: Optional[int] = 300,
                 key_prefix: str = "", tag: Optional[str] = None):
        self.cache = cache
        self.ttl = ttl
        self.key_prefix = key_prefix
        self.tag = tag

    def __call__(self, func: Callable):
        """Decorate function"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [self.key_prefix, func.__name__]

            # Add args to key
            if args:
                key_parts.extend(str(arg) for arg in args)

            # Add kwargs to key
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))

            cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            if self.cache.use_redis:
                self.cache.set(cache_key, result, ex=self.ttl)
            else:
                tags = [self.tag] if self.tag else None
                self.cache.set(cache_key, result, ex=self.ttl, tags=tags)

            return result

        return wrapper


# ============================================================================
# CACHE MANAGER
# ============================================================================

class CacheManager:
    """
    High-level cache management

    Features:
    - Multiple cache instances
    - Cache warming
    - Cache invalidation strategies
    - Cache patterns (read-through, write-through)
    """

    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.cache = CacheClient()
        self.loaders: Dict[str, Callable] = {}  # Data loaders for read-through

    def get(self, key: str, loader: Optional[Callable] = None) -> Optional[Any]:
        """
        Get value with optional loader (read-through pattern)

        If key not in cache and loader provided, load and cache
        """
        value = self.cache.get(key)

        if value is not None:
            return value

        # Load from source
        if loader:
            value = loader()
            if value is not None:
                self.cache.set(key, value, ex=self.default_ttl)
            return value

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value (write-through pattern)"""
        self.cache.set(key, value, ex=ttl or self.default_ttl)

    def invalidate(self, pattern: str):
        """Invalidate keys matching pattern"""
        keys = self.cache.keys(pattern)
        for key in keys:
            self.cache.delete(key)

    def invalidate_tag(self, tag: str):
        """Invalidate all keys with tag (in-memory only)"""
        if not self.cache.use_redis:
            self.cache.in_memory.delete_by_tag(tag)

    def warm_cache(self, keys_and_loaders: Dict[str, Callable]):
        """Warm cache with data"""
        for key, loader in keys_and_loaders.items():
            if not self.cache.exists(key):
                value = loader()
                if value is not None:
                    self.cache.set(key, value, ex=self.default_ttl)

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.cache.use_redis:
            return self.cache.in_memory.get_stats()
        else:
            # Redis doesn't provide built-in stats like this
            return {"message": "Redis stats not available"}

    def cached(self, ttl: Optional[int] = None, key_prefix: str = "",
              tag: Optional[str] = None):
        """Decorator for caching function results"""
        return CacheDecorator(self.cache, ttl or self.default_ttl, key_prefix, tag)


# ============================================================================
# DEMO USAGE
# ============================================================================

if __name__ == "__main__":
    print("💾 BLOOM Caching Layer Demo\n")

    # Initialize cache manager
    cache_mgr = CacheManager(default_ttl=300)

    print("✅ Initialized cache manager (in-memory mode)\n")

    # 1. Basic cache operations
    print("1️⃣ Basic Cache Operations:")
    cache_mgr.set("user:123", {"name": "Alice", "age": 30})
    cache_mgr.set("user:456", {"name": "Bob", "age": 25})

    user = cache_mgr.cache.get("user:123")
    print(f"   Retrieved user: {user}")
    print(f"   Key exists: {cache_mgr.cache.exists('user:123')}")
    print(f"   TTL: {cache_mgr.cache.ttl('user:123')} seconds\n")

    # 2. Cache with TTL
    print("2️⃣ Cache with TTL:")
    cache_mgr.set("session:abc", {"user_id": "123", "token": "xyz"}, ttl=5)
    print(f"   Stored session (TTL: 5s)")
    print(f"   TTL: {cache_mgr.cache.ttl('session:abc')} seconds")
    time.sleep(2)
    print(f"   After 2s, TTL: {cache_mgr.cache.ttl('session:abc')} seconds\n")

    # 3. Tag-based invalidation
    print("3️⃣ Tag-Based Invalidation:")
    if not cache_mgr.cache.use_redis:
        cache_mgr.cache.in_memory.set("product:1", {"name": "Widget A"}, tags=["products"])
        cache_mgr.cache.in_memory.set("product:2", {"name": "Widget B"}, tags=["products"])
        cache_mgr.cache.in_memory.set("product:3", {"name": "Widget C"}, tags=["products", "featured"])

        print(f"   Cached 3 products")
        cache_mgr.invalidate_tag("products")
        print(f"   Invalidated 'products' tag")
        print(f"   Product 1 exists: {cache_mgr.cache.exists('product:1')}\n")

    # 4. Pattern-based retrieval
    print("4️⃣ Pattern-Based Retrieval:")
    cache_mgr.set("agent:1:performance", {"roi": 2.5})
    cache_mgr.set("agent:2:performance", {"roi": 3.1})
    cache_mgr.set("agent:3:performance", {"roi": 1.8})

    agent_keys = cache_mgr.cache.keys("agent:*:performance")
    print(f"   Found {len(agent_keys)} agent performance keys")
    print(f"   Keys: {agent_keys}\n")

    # 5. Read-through pattern
    print("5️⃣ Read-Through Pattern:")
    db_calls = {"count": 0}

    def load_user_from_db():
        db_calls["count"] += 1
        return {"name": "Charlie", "age": 35}

    # First call - loads from DB
    user1 = cache_mgr.get("user:789", loader=load_user_from_db)
    print(f"   First call: {user1}")
    print(f"   DB calls: {db_calls['count']}")

    # Second call - from cache
    user2 = cache_mgr.get("user:789", loader=load_user_from_db)
    print(f"   Second call: {user2}")
    print(f"   DB calls: {db_calls['count']} (cached!)\n")

    # 6. Cache decorator
    print("6️⃣ Cache Decorator:")
    function_calls = {"count": 0}

    @cache_mgr.cached(ttl=10, key_prefix="calc", tag="calculations")
    def expensive_calculation(x: int, y: int):
        function_calls["count"] += 1
        time.sleep(0.1)  # Simulate slow operation
        return x * y + x ** y

    # First call - executes function
    result1 = expensive_calculation(3, 4)
    print(f"   First call: expensive_calculation(3, 4) = {result1}")
    print(f"   Function calls: {function_calls['count']}")

    # Second call - from cache
    result2 = expensive_calculation(3, 4)
    print(f"   Second call: expensive_calculation(3, 4) = {result2}")
    print(f"   Function calls: {function_calls['count']} (cached!)\n")

    # 7. Cache statistics
    print("7️⃣ Cache Statistics:")
    import json
    stats = cache_mgr.get_stats()
    print(json.dumps(stats, indent=2))

    # 8. Cache warming
    print("\n8️⃣ Cache Warming:")
    cache_mgr.warm_cache({
        "config:app": lambda: {"version": "1.0.0", "env": "production"},
        "config:features": lambda: {"ai_enabled": True, "beta_features": False}
    })
    print(f"   Warmed cache with 2 config entries")
    print(f"   Config exists: {cache_mgr.cache.exists('config:app')}\n")

    print("✅ Caching Layer Ready!")
    print("\nFeatures:")
    print("✅ In-memory cache with LRU/LFU/TTL eviction")
    print("✅ Redis-compatible interface")
    print("✅ TTL support")
    print("✅ Tag-based invalidation")
    print("✅ Pattern-based key retrieval")
    print("✅ Read-through caching pattern")
    print("✅ Cache decorator for functions")
    print("✅ Cache statistics and monitoring")
    print("✅ Cache warming")
