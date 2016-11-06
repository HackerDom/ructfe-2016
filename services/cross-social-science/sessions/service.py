from json import dumps, loads
from uuid import uuid4

import peewee

_sessions = {}
_last = None


def get_session_service(db_name=None):
    if db_name is None and _last:
        return _sessions[_last]
    elif db_name is None and _last is None:
        raise ValueError("DefaultSessionService is not registered")
    return _sessions[db_name]


def clear_session_services():
    global _sessions, _last
    _sessions = {}
    _last = None


def _has_session_service(db_name):
    return db_name in _sessions


def _set_default_session_service(db_name):
    if not isinstance(db_name, str):
        raise TypeError('db_name is not a str')
    if db_name not in _sessions:
        raise ValueError('this db_name is not registered yet')
    global _last
    _last = db_name


def _register_session_service(db_name, service):
    global _sessions
    if db_name in _sessions:
        raise RuntimeError('service with same name is already registered')
    _sessions[db_name] = service


class SessionService:
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

    async def get_request_session_data(self, request):
        uid = request.cookies.get(self._db_name)
        return await self.get_session_data(uid)

    async def set_request_session_data(self, request, response, data):
        uid = request.cookies.get(self._db_name)
        if not uid:
            uid = str(uuid4())
        response.cookies[self._db_name] = uid
        await self.set_session_data(uid, data)

    async def update_request_session_data(self, request, response, data):
        uid = request.cookies.get(self._db_name)
        if not uid:
            uid = str(uuid4())
        response.cookies[self._db_name] = uid
        await self.update_session_data(uid, data)

    async def get_session_data(self, uid):
        if not uid:
            return None
        if not isinstance(uid, str):
            raise TypeError('uid is not a str')
        data = None
        if uid:
            try:
                obj = await self.manager.get(self._model, key=uid)
                if obj.value:
                    try:
                        data = loads(obj.value)
                    except (ValueError, TypeError):
                        pass
            except peewee.DoesNotExist:
                pass
        return data

    async def set_session_data(self, uid, data):
        if not uid:
            raise ValueError('bad uid')
        if not isinstance(uid, str):
            raise TypeError('uid is not a str')

        data = dumps(data)
        obj, _ = await self.manager.get_or_create(self._model, key=uid)
        if obj.value != data:
            obj.value = data
            await self.manager.update(obj, only=['value'])

    async def update_session_data(self, uid, data):
        if not uid:
            raise ValueError('bad uid')
        if not isinstance(uid, str):
            raise TypeError('uid is not a str')
        if not isinstance(data, dict):
            raise TypeError('data is not a dict')
        current_data = await self.get_session_data(uid)
        current_data.update(data)
        await self.set_session_data(uid, current_data)
        return current_data
