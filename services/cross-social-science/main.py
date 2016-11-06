import asyncio

from sanic import Sanic
from sanic.response import json, text, html
from sanic.exceptions import ServerError

from models import database

try:
    import uvloop as async_loop
except ImportError:
    async_loop = asyncio

import settings
from sessions import session_blueprint as sessions
from users import user_blueprint as users
from blog import blog_blueprint as blog


def make_app():
    app = Sanic(__name__)
    app.static('/static', settings.STATIC_DIR)

    @app.route("/", methods=['GET'])
    async def test_index(request):
        from templates import render
        return html(render('index.html', name='variables'))

    @app.route("/dynamic/<name>/<id:int>")
    def test_params(request, name, id:int):
        return text("yeehaww {} {}".format(name, id))

    @app.route("/exception")
    def exception(request):
        raise ServerError("It's dead jim")

    @app.route("/await")
    async def test_await(request):
        import asyncio
        await asyncio.sleep(5)
        return text("I'm feeling sleepy")

    # ----------------------------------------------- #
    # Read from request
    # ----------------------------------------------- #

    @app.route("/json")
    def post_json(request):
        return json({"received": True, "message": request.json})

    @app.route("/form")
    def post_json(request):
        return json({"received": True, "form_data": request.form,
                     "test": request.form.get('test')})

    @app.route("/query_string")
    def query_string(request):
        return json({"parsed": True, "args": request.args, "url": request.url,
                     "query_string": request.query_string})

    # ----------------------------------------------- #
    # Exceptions
    # ----------------------------------------------- #

    @app.exception(ServerError)
    async def test(request, exception):
        return json(
            {"exception": "{}".format(exception),
             "status": exception.status_code},
            status=exception.status_code)

    @app.middleware('response')
    async def halt_response(request, response):
        print('I halted the response')

    return app


# ----------------------------------------------- #
# Run Server
# ----------------------------------------------- #

if __name__ == '__main__':
    # loop
    loop = async_loop.new_event_loop()
    asyncio.set_event_loop(loop)
    # database
    database
    # app
    app = make_app()
    app.blueprint(sessions, db=database, db_name='sessions', loop=loop)
    app.blueprint(users, db=database, db_name='users', loop=loop,
                  sessions_db_name='sessions')
    app.run(host="0.0.0.0", port=8000, loop=loop, debug=True)
