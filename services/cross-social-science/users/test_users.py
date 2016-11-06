from json import loads

from peewee_async import PostgresqlDatabase
from sanic import Sanic
from sanic.response import json
from sanic.utils import sanic_endpoint_test

from sessions import clear_session_services
from sessions import session_blueprint
from . import get_user_service, clear_user_services
from . import user_blueprint as bp


DB = 'test'
DB_NAME = 'test_users'
DB_SESSION_NAME = DB_NAME + '_session'


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
    database.close()
    database.allow_sync = False
    app.db = database
    return app


def get_user(app, username):
    service = get_user_service()
    app.db.allow_sync = True
    obj = service._model.get(username=username)  # noqa
    return obj


def test_get_request_user_for_anonymous():
    app = make_test_app()

    @app.route('/')
    async def handler(request):
        service = get_user_service()
        obj = await service.get_request_user(request)
        return json({'user': obj})

    request, response = sanic_endpoint_test(app, uri='/')
    assert response.text == '{"user":{"username":"AnonymousUser"}}'
