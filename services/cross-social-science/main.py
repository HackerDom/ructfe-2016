from sanic import Sanic

from sanic.response import json, text, html
from sanic.exceptions import ServerError

from hooks import after_start
from hooks import before_stop


def make_app():
    app = Sanic(__name__)

    @app.route("/index")
    async def test_index(request):
        from templates import render
        return html(render('example.html', name='variables'))

    @app.route("/async")
    async def test_async(request):
        return json({"test": True})

    @app.route("/sync", methods=['GET', 'POST'])
    def test_sync(request):
        return json({"test": True})

    @app.route("/dynamic/<name>/<id:int>")
    def test_params(request, name, id):
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

    @app.exception(Exception)
    async def test(request, exception):
        return json(
            {"exception": "{}".format(exception),
             "status": exception.status_code},
            status=exception.status_code)

    return app


# ----------------------------------------------- #
# Run Server
# ----------------------------------------------- #

if __name__ == '__main__':
    app = make_app()
    app.run(host="0.0.0.0", port=8000, debug=True, loop=None,
            after_start=after_start,
            before_stop=before_stop)