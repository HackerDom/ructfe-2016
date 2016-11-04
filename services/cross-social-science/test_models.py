from sanic.response import json
from sanic.utils import sanic_endpoint_test

from main import make_app
from models import initdb, KeyValue, make_manager


def test_sync():
    app = make_app()
    models = make_manager()
    initdb()

    async def clean_db():
        objs = await models.execute(KeyValue.select())
        for obj in objs:
            await models.delete(obj)

    @app.route('/post/<key>/<value>')
    async def handler(request, key, value):
        await clean_db()
        obj = await models.create(KeyValue, key=key, value=value)
        return json({'object_id': obj.key})

    request, response = sanic_endpoint_test(app, uri='/post/key1/value')

    assert response.text == '{"object_id":"key1"}'
