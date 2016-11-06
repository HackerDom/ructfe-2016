from sanic.response import text
from sanic.utils import sanic_endpoint_test

from main import make_app


def test_sync():
    app = make_app()

    @app.route('/test')
    def handler(request):
        return text('Hello')

    request, response = sanic_endpoint_test(app, uri='/test')

    assert response.text == 'Hello'


def test_async():
    app = make_app()

    @app.route('/test')
    async def handler(request):
        return text('Hello')

    request, response = sanic_endpoint_test(app, uri='/test')

    assert response.text == 'Hello'
