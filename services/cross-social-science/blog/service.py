from json import dumps, loads
from uuid import uuid4

import peewee
from slugify import slugify

_blogs = {}
_last = None


def get_blog_service(db_name=None):
    if db_name is None and _last:
        return _blogs[_last]
    elif db_name is None and _last is None:
        raise ValueError("DefaultSessionService is not registered")
    return _blogs[db_name]


def clear_blog_services():
    global _blogs, _last
    _blogs = {}
    _last = None


def _has_blog_service(db_name):
    return db_name in _blogs


def _set_default_blog_service(db_name):
    if not isinstance(db_name, str):
        raise TypeError('db_name is not a str')
    if db_name not in _blogs:
        raise ValueError('this db_name is not registered yet')
    global _last
    _last = db_name


def _register_blog_service(db_name, service):
    global _blogs
    if db_name in _blogs:
        raise RuntimeError('service with same name is already registered')
    _blogs[db_name] = service


class BlogService:
    def __init__(self, app, db_name, initdb, dropdb, manager, model):
        self.app = app
        self.manager = manager
        self._db_name = db_name
        self._initdb = initdb
        self._dropdb = dropdb
        self._model = model

    def initdb(self):
        self._initdb()

    def dropdb(self):
        self._dropdb()

    async def get_blog_entries(self, limit=100, **kwargs):
        query = self._model.select()
        conditions = [getattr(self._model, k) == v for k, v in kwargs.items()]
        if conditions:
            query = query.where(*conditions)
        return await self.manager.execute(query.limit(limit))

    async def create_blog_entry(self, title, content, meta=None,
                                slug=None, is_published=False):
        if meta and not isinstance(meta, dict):
            raise TypeError('meta is not a dict')
        raw_meta = dumps(meta) if meta else ''
        if not slug:
            slug = slugify(title.lower())
        obj = await self.manager.create(
            self._model, title=title, content=content, raw_meta=raw_meta,
            slug=slug, is_published=is_published)
        return obj
