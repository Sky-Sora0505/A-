"""
Simple Redis-like Cache Server
Based on building a simple Redis server concepts
"""
import socket
import json
from io import BytesIO


class CacheServer:
    """Simple in-memory cache server with Redis-like protocol"""
    
    def __init__(self, host='127.0.0.1', port=6379):
        self.host = host
        self.port = port
        self.cache = {}
        self.socket = None
    
    def start(self):
        """Start the cache server (in-process mode)"""
        # CacheClient はインプロセスで直接メソッドを呼ぶため
        # ソケットバインドは不要。インメモリキャッシュとして動作。
        print(f"Cache server started (in-process mode)")
    
    def stop(self):
        """Stop the cache server"""
        self.cache.clear()
    
    def get(self, key):
        """Get value from cache"""
        return self.cache.get(key)
    
    def set(self, key, value, ttl=None):
        """Set value in cache"""
        self.cache[key] = value
        return True
    
    def delete(self, key):
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def exists(self, key):
        """Check if key exists"""
        return key in self.cache
    
    def keys(self, pattern="*"):
        """Get all keys matching pattern"""
        if pattern == "*":
            return list(self.cache.keys())
        # Simple pattern matching
        import re
        regex_pattern = pattern.replace("*", ".*")
        return [k for k in self.cache.keys() if re.match(regex_pattern, k)]
    
    def flush(self):
        """Clear all cache"""
        count = len(self.cache)
        self.cache.clear()
        return count
    
    def mget(self, *keys):
        """Get multiple values"""
        return [self.cache.get(k) for k in keys]
    
    def mset(self, **kwargs):
        """Set multiple values"""
        self.cache.update(kwargs)
        return len(kwargs)


class CacheClient:
    """Simple cache client for in-process communication"""
    
    def __init__(self, server):
        self.server = server
    
    def get(self, key):
        return self.server.get(key)
    
    def set(self, key, value):
        return self.server.set(key, value)
    
    def delete(self, key):
        return self.server.delete(key)
    
    def exists(self, key):
        return self.server.exists(key)
    
    def keys(self, pattern="*"):
        return self.server.keys(pattern)
    
    def flush(self):
        return self.server.flush()
    
    def mget(self, *keys):
        return self.server.mget(*keys)
    
    def mset(self, **kwargs):
        return self.server.mset(**kwargs)
