# -*- coding: utf-8 -*-
"""
    Библиотека для кеширования данных в редис

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import uuid
import hashlib
import functools

from flask import request, current_app
from werkzeug.contrib.cache import RedisCache


class SimpleRedisCache(RedisCache):

    def __init__(self, app):
        self.app = app
        self.config = app.config
        self.default_timeout = self.config.get('CACHE_DEFAULT_TIMEOUT')

        kwargs = dict(
            host=self.config.get('CACHE_REDIS_HOST', 'localhost'),
            port=self.config.get('CACHE_REDIS_PORT', 6379),
        )
        password = self.config.get('CACHE_REDIS_PASSWORD')
        if password:
            kwargs['password'] = password

        db_number = self.config.get('CACHE_REDIS_DB')
        if db_number:
            kwargs['db'] = db_number

        self.cache = RedisCache(**kwargs)

    def get_key(self, *args, **kwargs):

        args_key = ''.join(str(args))
        kwargs_values_key = ''.join(str(kwargs.values()))
        kwargs_keys = ''.join(str(kwargs.keys()))
        key = '%s%s%s' % (args_key, kwargs_values_key, kwargs_keys)
        return hashlib.md5(key).hexdigest().encode('utf-8')

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout

        self.cache.set(key, value, timeout)

    def get(self, key):
        return self.cache.get(key)

    def delete(self, key):
        return self.cache.delete(key)

    def clear(self):
        self.cache.clear()

    def cached(self, timeout=None, key_prefix='view/%s', unless=None):
        def decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                #: Bypass the cache entirely.
                if callable(unless) and unless() is True:
                    return f(*args, **kwargs)

                try:
                    cache_key = self.get_key(
                        key_prefix=key_prefix,
                        *args,
                        **kwargs)
                    rv = self.cache.get(cache_key)
                except Exception:
                    if current_app.debug:
                        raise
                    logger.exception(
                        "Exception possibly due to cache backend.")
                    return f(*args, **kwargs)

                if rv is None:
                    rv = f(*args, **kwargs)
                    try:
                        self.cache.set(cache_key, rv,
                                       timeout=decorated_function.cache_timeout)
                    except Exception:
                        if current_app.debug:
                            raise
                        logger.exception(
                            "Exception possibly due to cache backend.")
                        return f(*args, **kwargs)
                return rv

            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout

            return decorated_function
        return decorator
