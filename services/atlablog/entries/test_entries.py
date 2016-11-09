from json import loads

from peewee_async import PostgresqlDatabase
from sanic import Sanic
from sanic.response import json
from sanic.utils import sanic_endpoint_test

from . import get_entry_service, clear_entry_services
from . import entry_blueprint as bp


DB = 'test'
DB_NAME = 'test_entries'


def make_test_app():
    clear_entry_services()
    app = Sanic(__name__)
    database = PostgresqlDatabase(database=DB)
    app.blueprint(bp, db=database, db_name=DB_NAME, loop=None)
    service = get_entry_service()
    service.dropdb()
    service.initdb()
    database.close()
    database.allow_sync = False
    app.db = database
    return app


def get_entry(app, slug):
    service = get_entry_service()
    app.db.allow_sync = True
    obj = service._model.get(slug=slug)
    return obj


def test_get_entries_0th():
    app = make_test_app()

    @app.route('/')
    async def handler(request):
        service = get_entry_service()
        entries = await service.get_entries()
        return json({'entries': entries})

    request, response = sanic_endpoint_test(app, uri='/')
    assert response.text == '{"entries":[]}'


def test_get_entries_4th():
    app = make_test_app()

    async def create_4th_entries():
        service = get_entry_service()
        await service.create_entry('hello1!', '*some* _content_')
        await service.create_entry('hello2!', '*some* _content_')
        await service.create_entry('hello3!', '*some* _content_')
        await service.create_entry('hello4!', '*some* _content_')

    @app.route('/')
    async def handler(request):
        await create_4th_entries()
        service = get_entry_service()
        entries = await service.get_entries()
        return json({'entries': entries})

    request, response = sanic_endpoint_test(app, uri='/')
    # fix timestamps (hardcoded)
    fix_timestamp_data = loads(response.text)
    assert len(fix_timestamp_data['entries']) == 4
    for x in fix_timestamp_data['entries']:
        x['created'] = 1478433519
    assert fix_timestamp_data == {'entries': [
        {'created': 1478433519, 'raw_meta': '', 'meta': None,
         'slug': 'hello1', 'id': 1, 'is_published': False, 'title': 'hello1!',
         'html_content': '<p><em>some</em> <em>content</em></p>',
         'content': '*some* _content_', 'dirty_fields': []},
        {'created': 1478433519, 'raw_meta': '', 'meta': None,
         'slug': 'hello2', 'id': 2, 'is_published': False, 'title': 'hello2!',
         'html_content': '<p><em>some</em> <em>content</em></p>',
         'content': '*some* _content_', 'dirty_fields': []},
        {'created': 1478433519, 'raw_meta': '', 'meta': None,
         'slug': 'hello3', 'id': 3, 'is_published': False, 'title': 'hello3!',
         'html_content': '<p><em>some</em> <em>content</em></p>',
         'content': '*some* _content_', 'dirty_fields': []},
        {'created': 1478433519, 'raw_meta': '', 'meta': None,
         'slug': 'hello4', 'id': 4, 'is_published': False, 'title': 'hello4!',
         'html_content': '<p><em>some</em> <em>content</em></p>',
         'content': '*some* _content_', 'dirty_fields': []}
    ]}


def test_get_entries_with_only_2th_of_4th_published():
    app = make_test_app()

    async def create_4th_entries():
        service = get_entry_service()
        await service.create_entry('hello1!', '*some*', is_published=False)
        await service.create_entry('hello2!', '*some*', is_published=False)
        await service.create_entry('hello3!', '*some*', is_published=True)
        await service.create_entry('hello4!', '*some*', is_published=True)

    @app.route('/')
    async def handler(request):
        await create_4th_entries()
        service = get_entry_service()
        entries = await service.get_entries(is_published=True)
        return json({'entries': entries})

    request, response = sanic_endpoint_test(app, uri='/')
    # fix timestamps (hardcoded)
    fix_timestamp_data = loads(response.text)
    assert len(fix_timestamp_data['entries']) == 2
    for x in fix_timestamp_data['entries']:
        x['created'] = 1478433519
    assert fix_timestamp_data == {'entries': [
        {'created': 1478433519, 'raw_meta': '', 'meta': None,
         'slug': 'hello3', 'id': 3, 'is_published': True, 'title': 'hello3!',
         'html_content': '<p><em>some</em></p>',
         'content': '*some*', 'dirty_fields': []},
        {'created': 1478433519, 'raw_meta': '', 'meta': None,
         'slug': 'hello4', 'id': 4, 'is_published': True, 'title': 'hello4!',
         'html_content': '<p><em>some</em></p>',
         'content': '*some*', 'dirty_fields': []}
    ]}
