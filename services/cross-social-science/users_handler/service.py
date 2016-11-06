from hashlib import sha256
import re

from sanic.response import json
from peewee import DoesNotExist

import datetime

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


class RegistrationService:
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

    async def registration(self, request):
        private_info = self.handle_form(request, "username", "password")

        if "error" not in private_info:
            if not self.username_correct(private_info["username"]):
                return json({"error": "bad username formatting"})

            try:
                user = await self.manager.select(
                    self._model, key=private_info["username"]
                )
                return {"error": "this username already exists"}
            except DoesNotExist:
                user = await self.manager.create(
                    usename=private_info["username"],
                    password_hash=self.get_sha256(private_info["password"]),
                    registration_date=datetime.datetime.now()
                )
                success = await user.save()
                if success:
                    return json({"success": 'user "{}" created!'.format(private_info["username"])})
        else:
            return json({"error": "Not enough params for POST request!"})

    @staticmethod
    def get_sha256(string):
        return sha256(string.encode("utf-8")).hexdigest()

    @staticmethod
    def username_correct(username):
        return re.fullmatch(r'[a-zA-Z0-9_]{1,16}', username) is not None

    @staticmethod
    def handle_form(request, *post_params):
        try:
            parsed_form = {
                param: request.form.get(param) for param in post_params
                }
        except TypeError as e:
            return {"error": e}
        return parsed_form

    async def authorization(self, request):
        private_info = self.handle_form(request, "username", "password")

        if "error" not in private_info:
            if not self.username_correct(private_info["username"]):
                return json({"error": "bad username formatting"})
            try:
                user_obj, _ = await  self.manager.get(self._model, key=private_info["username"])
            except DoesNotExist:
                return json({"error": "can't find such user"})

            if user_obj.password_hash == self.get_sha256(private_info["password"]):
                return json({"success": 'User "{}" authorized'.format(private_info["password"])})
            else:
                return json({"error": "bad auth data"})
        else:
            return "Backend error: {}".format(private_info["error"])
