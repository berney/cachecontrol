from ..cache import BaseCache

from sqlalchemy import Column, String


class SQLAlchemyCacheMixin(object):
    cache_key = Column(String, nullable=False, unique=True)
    cache_value = Column(String)


class SQLAlchemyCache(BaseCache):
    def __init__(self, session, klass):
        self.session = session

        if isinstance(klass, SQLAlchemyCacheMixin):
            self.klass = klass
        else:
            raise ValueError('klass must inherit SQLAlchemyCacheMixin')

    def get(self, cache_key):
        return self.session.query(self.klass).\
            filter(self.klass.cache_key == cache_key).one_or_none()

    def set(self, cache_key, cache_value):
        obj = self.get(cache_key)

        if obj is not None:
            obj.cache_value = cache_value
        else:
            obj = self.klass()
            obj.cache_key = cache_key
            obj.cache_value = cache_value

        self.session.add(obj)
        self.session.commit()

    def delete(self, cache_key):
        obj = self.get(cache_key)

        if obj is not None:
            self.session.delete(obj)
            self.session.commit()

    def close(self):
        self.session.close()
