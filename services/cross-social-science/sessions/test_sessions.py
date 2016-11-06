import asyncio
from peewee_async import PostgresqlDatabase
from sanic import Sanic
from sanic.response import json
from sanic.utils import sanic_endpoint_test

from sessions import get_session_service, clear_session_services
from sessions import session_blueprint as bp


DB = 'test'
DB_NAME = 'test_sessions'


def make_session_test_app():
    clear_session_services()
    app = Sanic(__name__)
    database = PostgresqlDatabase(database=DB)
    app.blueprint(bp, db=database, db_name=DB_NAME, loop=None)
    service = get_session_service()
    service.dropdb()
    service.initdb()
    database.close()
    database.allow_sync = False
    app.db = database
    return app


def get_session_value(app, key):
    session = get_session_service()
    app.db.allow_sync = True
    obj = session._model.get(key=key)
    return obj


def test_set_and_get_request_session_data():
    app = make_session_test_app()
    uid = '1ef9bf84-6ead-43ff-9a38-07222e3cb7d9'

    async def set_session_data():
        nonlocal uid
        session = get_session_service()
        await session.set_session_data(uid, {'x': 1, 'y': '2'})

    @app.route('/')
    async def handler(request):
        await set_session_data()
        session = get_session_service()
        data = await session.get_request_session_data(request)
        return json({'data': data})

    request, response = sanic_endpoint_test(
        app, uri='/', cookies={DB_NAME: uid})
    assert response.text == '{"data":{"x":1,"y":"2"}}' or \
           response.text == '{"data":{"y":"2","x":1}}'


def test_get_request_session_data_without_set():
    app = make_session_test_app()

    @app.route('/')
    async def handler(request):
        session = get_session_service()
        data = await session.get_request_session_data(request)
        return json({'data': data})

    request, response = sanic_endpoint_test(app, uri='/')
    assert response.text == '{"data":{}}'
    assert not response.cookies.get(DB_NAME)


def test_set_request_session_data():
    app = make_session_test_app()

    @app.route('/')
    async def handler(request):
        session = get_session_service()
        response = json({'status': 'ok'})
        data = {'x': 1}
        await session.set_request_session_data(request, response, data)
        return response

    request, response = sanic_endpoint_test(app, uri='/')
    assert response.text == '{"status":"ok"}'
    uid = response.cookies[DB_NAME].value
    obj = get_session_value(app, uid)
    assert obj.key == uid
    assert obj.value == '{"x": 1}'


def test_get_request_session_data_then_set_request_session_data():
    app = make_session_test_app()

    @app.route('/')
    async def handler(request):
        response = json({'status': 'ok'})
        data = await get_session_service().get_request_session_data(request)
        if not data:
            data = {'_user_id': 1}
            await get_session_service().set_request_session_data(
                request, response, data)
        return response

    request, response = sanic_endpoint_test(app, uri='/')
    assert response.text == '{"status":"ok"}'
    uid = response.cookies[DB_NAME].value
    obj = get_session_value(app, uid)
    assert obj.key == uid
    assert obj.value == '{"_user_id": 1}'


def test_update_session_data():
    make_session_test_app()
    uid = '1ef92222-6ead-43ff-9a38-07222e3cb7d9'

    async def set_and_update():
        session = get_session_service()
        await session.set_session_data(uid, {'x': 1, 'y': 2})
        await session.update_session_data(uid, {'x': 2, 'z': 2})
        return await session.get_session_data(uid)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(set_and_update())
    assert result == {'x': 2, 'y': 2, 'z': 2}
