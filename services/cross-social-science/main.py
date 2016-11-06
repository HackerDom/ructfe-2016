import asyncio

from peewee_async import PostgresqlDatabase
from sanic import Sanic
from sanic.response import json, text, html
from sanic.exceptions import ServerError

try:
    import uvloop as async_loop
except ImportError:
    async_loop = asyncio

from sessions import session_blueprint as sessions
from users import user_blueprint as users
from blog import blog_blueprint as blog
from views import View
import settings


def make_app(view=None, database=None):
    if not view:
        view = View({"HTML_TEMPLATES_DIR": settings.TEMPLATES_DIR})
    if not database:
        database = PostgresqlDatabase(database=settings.DATABASE)

    app = Sanic(__name__)
    app.static('/static', settings.STATIC_DIR)

    @app.route("/", methods=['GET'])
    async def test_index(request):
        return html(view.render('index', {'name': 'variables'}))

    @app.route("/dynamic/<name>/<id:int>")
    async def test_params(request, name, id:int):
        return text("yeehaww {} {}".format(name, id))

    @app.route("/await")
    async def test_await(request):
        import asyncio
        await asyncio.sleep(5)
        return text("I'm feeling sleepy")

    # ----------------------------------------------- #
    # Read from request
    # ----------------------------------------------- #

    @app.route("/json")
    async def post_json(request):
        return json({"received": True, "message": request.json})

    @app.route("/form")
    async def post_json(request):
        return json({"received": True, "form_data": request.form,
                     "test": request.form.get('test')})

    @app.route("/query")
    async def query_string(request):
        return json({"parsed": True, "args": request.args, "url": request.url,
                     "query_string": request.query_string})

    # ----------------------------------------------- #
    # Exceptions
    # ----------------------------------------------- #

    @app.route("/exception")
    async def exception(request):
        raise ServerError("It's dead jim")

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


def main(debug=False):
    # loop
    loop = async_loop.new_event_loop()
    asyncio.set_event_loop(loop)
    # database
    database = PostgresqlDatabase(database=settings.DATABASE)
    #  templates
    view = View({"HTML_TEMPLATES_DIR": settings.TEMPLATES_DIR})
    # app
    app = make_app(view, database)
    app.blueprint(sessions, db=database, db_name='sessions', loop=loop)
    app.blueprint(users, db=database, db_name='users', loop=loop,
                  sessions_db_name='sessions')
    app.blueprint(blog, db=database, db_name='blog', loop=loop)
    app.run(host="0.0.0.0", port=8000, loop=loop, debug=debug)


if __name__ == '__main__':
    main(debug=True)
