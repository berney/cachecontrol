from ..cache import BaseCache
from ..controller import CacheController

from sqlalchemy import Column, String, LargeBinary


class SQLAlchemyCacheMixin(object):
    cache_key = Column(String, nullable=False, unique=True)
    cache_value = Column(LargeBinary)


class SQLAlchemyCache(BaseCache):
    def __init__(self, klass, session):
        if issubclass(klass, SQLAlchemyCacheMixin):
            self.klass = klass
        else:
            raise ValueError('klass must inherit from SQLAlchemyCacheMixin')

        self.session = session

    def _get_obj(self, cache_key):
        return self.session.query(self.klass).\
            filter(self.klass.cache_key == cache_key).one_or_none()

    def get(self, cache_key):
        obj = self._get_obj(cache_key)

        if obj is not None:
            return obj.cache_value

        return None

    def set(self, cache_key, cache_value):
        obj = self._get_obj(cache_key)

        if obj is not None:
            obj.cache_value = cache_value
        else:
            obj = self.klass()
            obj.cache_key = cache_key
            obj.cache_value = cache_value

        self.session.add(obj)
        self.session.commit()

    def delete(self, cache_key):
        obj = self._get_obj(cache_key)

        if obj is not None:
            self.session.delete(obj)
            self.session.commit()

    def close(self):
        self.session.close()


def url_to_model(url, cache):
    "Returns the SQLAlchemy model caching the url, or None if not cached"

    cache_key = CacheController.cache_url(url)
    return cache._get_obj(cache_key)
