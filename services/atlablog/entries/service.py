from json import dumps

from slugify import slugify

_entries = {}
_last = None


def get_entry_service(db_name=None):
    if db_name is None and _last:
        return _entries[_last]
    elif db_name is None and _last is None:
        raise ValueError("DefaultSessionService is not registered")
    service = _entries[db_name]
    assert isinstance(service, EntryService)
    return service


def clear_entry_services():
    global _entries, _last
    _entries = {}
    _last = None


def _has_entry_service(db_name):
    return db_name in _entries


def _set_default_entry_service(db_name):
    if not isinstance(db_name, str):
        raise TypeError('db_name is not a str')
    if db_name not in _entries:
        raise ValueError('this db_name is not registered yet')
    global _last
    _last = db_name


def _register_entry_service(db_name, service):
    global _entries
    if db_name in _entries:
        raise RuntimeError('service with same name is already registered')
    _entries[db_name] = service


class EntryService:
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

    async def get_entries(self, limit=100, **kwargs):
        query = self._model.select()
        conditions = []
        for key, value in kwargs.items():
            if key.endswith('__startswith'):
                key = key[:-len('__startswith')]
                conditions.append(getattr(self._model, key).startswith(value))
            else:
                conditions.append(getattr(self._model, key) == value)
        if conditions:
            query = query.where(*conditions)
        return await self.manager.execute(query.limit(limit))

    async def create_entry(self, title, content, meta=None,
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
