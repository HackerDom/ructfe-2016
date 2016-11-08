from json import loads

from peewee_async import PostgresqlDatabase
from sanic import Sanic
from sanic.response import json
from sanic.utils import sanic_endpoint_test

from sessions import clear_session_services, get_session_service
from sessions import session_blueprint
from . import get_user_service, clear_user_services
from . import user_blueprint as bp


DB = 'test'
DB_NAME = 'test_users'
DB_SESSION_NAME = DB_NAME + '_sessions'


def make_test_app():
    clear_session_services()
    clear_user_services()
    app = Sanic(__name__)
    database = PostgresqlDatabase(database=DB)
    app.blueprint(session_blueprint, db=database, db_name=DB_SESSION_NAME,
                  loop=None)
    app.blueprint(bp, db=database, db_name=DB_NAME, loop=None,
                  sessions_db_name=DB_SESSION_NAME)
    service = get_user_service()
    service.dropdb()
    service.initdb()
    service = get_session_service()
    service.dropdb()
    service.initdb()
    database.close()
    database.allow_sync = False
    app.db = database
    return app


def get_user(app, username):
    service = get_user_service()
    app.db.allow_sync = True
    obj = service._model.get(username=username)  # noqa
    return obj


def get_session_value(app, key):
    session = get_session_service()
    app.db.allow_sync = True
    obj = session._model.get(key=key)
    return obj


def get_response_session_data(app, response):
    assert response.text == '{"status":"ok"}'
    uid = response.cookies[DB_SESSION_NAME].value
    obj = get_session_value(app, uid)
    if obj.value:
        return loads(obj.value)
    return {}


def test_get_request_user_for_anonymous():
    app = make_test_app()

    @app.route('/')
    async def handler(request):
        service = get_user_service()
        obj = await service.get_request_user(request)
        return json({'user': obj})

    request, response = sanic_endpoint_test(app, uri='/')
    assert response.text == '{"user":{"username":"AnonymousUser"}}'


def test_create_and_login_user():
    app = make_test_app()

    async def register(username, password='JAFNjabwfakjBAWFJfb', meta=None):
        service = get_user_service()
        return await service.create_user(username, password, meta=meta)

    @app.route('/')
    async def handler(request):
        user = await register('pahaz')
        response = json({'status': 'ok'})
        service = get_user_service()
        await service.set_request_user(request, response, user)
        return response

    request, response = sanic_endpoint_test(app, uri='/')
    assert get_response_session_data(app, response) == {'_username': 'pahaz'}


def test_create_and_login_user_then_logout():
    app = make_test_app()

    async def register(username, password='JAFNjabwfakjBAWFJfb', meta=None):
        service = get_user_service()
        return await service.create_user(username, password, meta=meta)

    @app.route('/')
    async def handler(request):
        user = await register('pahaz')
        response = json({'status': 'ok'})
        service = get_user_service()
        await service.set_request_user(request, response, user)
        await service.set_request_user(request, response, None)
        return response

    request, response = sanic_endpoint_test(app, uri='/')
    assert get_response_session_data(app, response) == {'_username': ''}
