from json import dumps

import peewee
from hashlib import sha256
import re

from sanic.response import json
from peewee import DoesNotExist

import datetime

from users.models import AnonymousUser

_users = {}
_last = None
USERNAME_RE = re.compile('^[a-zA-Z0-9.-_@]{3,20}$')
WEAK_PASSWORDS = {
    'qwerty', '123456', 'asdfgh', 'password', 'admin123', 'qweasdzxc',
    'qweqwe123', '123123123',
}


def get_user_service(db_name=None):
    if db_name is None and _last:
        return _users[_last]
    elif db_name is None and _last is None:
        raise ValueError("DefaultUserService is not registered")
    service = _users[db_name]
    assert isinstance(service, UserService)
    return service


def clear_user_services():
    global _users, _last
    _users = {}
    _last = None


def _has_user_service(db_name):
    return db_name in _users


def _set_default_user_service(db_name):
    if not isinstance(db_name, str):
        raise TypeError('db_name is not a str')
    if db_name not in _users:
        raise ValueError('this db_name is not registered yet')
    global _last
    _last = db_name


def _register_user_service(db_name, service):
    global _users
    if db_name in _users:
        raise RuntimeError('service with same name is already registered')
    _users[db_name] = service


class UserService:
    sessions_db_name = None
    sessions_key = '_username'

    class UserServiceError(Exception):
        pass

    def __init__(self, app, db_name, init_db, drop_db, manager, model):
        self.app = app
        self.manager = manager
        self._db_name = db_name
        self._initdb = init_db
        self._dropdb = drop_db
        self._model = model

    def initdb(self):
        self._initdb()

    def dropdb(self):
        self._dropdb()

    def clean_username(self, username):
        if not USERNAME_RE.fullmatch(username):
            raise self.UserServiceError('Invalid username pattern')
        return username.lower()

    def clean_password(self, password):
        if len(password) <= 5:
            raise self.UserServiceError('Password is too short')
        if len(password) > 100:
            raise self.UserServiceError('Password is too large')
        if password in WEAK_PASSWORDS:
            raise self.UserServiceError('Password is too weak')
        return password

    def hashing_password(self, password, salt=''):
        return str(sha256((password + salt).encode("utf-8")).hexdigest())

    async def get_user(self, username):
        username = self.clean_username(username)
        try:
            return await self.manager.get(self._model, username=username)
        except peewee.DoesNotExist:
            raise self.UserServiceError('Username does not exist')

    async def create_user(self, username, password, meta=None):
        if meta and not isinstance(meta, dict):
            raise TypeError('meta is not a dict')

        username = self.clean_username(username)
        password = self.clean_password(password)
        password_hash = self.hashing_password(password)
        raw_meta = dumps(meta) if meta else ''
        if await self.has_username(username):
            raise self.UserServiceError('Username already used')
        try:
            obj = await self.manager.create(
                self._model,
                username=username,
                password_hash=password_hash,
                raw_meta=raw_meta
            )
        except peewee.IntegrityError:
            raise self.UserServiceError('Username is recently already used')
        return obj

    async def has_username(self, username):
        try:
            await self.manager.get(self._model, username=username)
        except peewee.DoesNotExist:
            return False
        return True

    async def validate_credentials_and_get_user(self, username, password):
        username = self.clean_username(username)
        password = self.clean_password(password)
        password_hash = self.hashing_password(password)
        try:
            obj = await self.get_user(username)
        except peewee.DoesNotExist:
            raise self.UserServiceError('Username is not registered yet')
        if obj.password_hash != password_hash:
            raise self.UserServiceError('Wrong password')
        return obj

    async def get_request_user(self, request):
        from sessions import get_session_service
        sessions = get_session_service(self.sessions_db_name)

        data = await sessions.get_request_session_data(request)
        if self.sessions_key in data:
            username = data[self.sessions_key]
            if username:
                return await self.get_user(username)
        return AnonymousUser()

    async def set_request_user(self, request, response, user):
        from sessions import get_session_service
        sessions = get_session_service(self.sessions_db_name)

        username = user.username if user and user.is_authenticated() else ''
        await sessions.update_request_session_data(request, response, {
            self.sessions_key: username
        })
