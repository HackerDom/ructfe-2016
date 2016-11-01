from sanic.response import text
from sanic.utils import sanic_endpoint_test

from main import make_app


def test_sync():
    app = make_app()

    @app.route('/')
    def handler(request):
        return text('Hello')

    request, response = sanic_endpoint_test(app, uri='/')

    assert response.text == 'Hello'


def test_text():
    app = make_app()

    @app.route('/')
    async def handler(request):
        return text('Hello')

    request, response = sanic_endpoint_test(app, uri='/')

    assert response.text == 'Hello'
