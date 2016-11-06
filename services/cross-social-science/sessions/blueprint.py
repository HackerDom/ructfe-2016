from sanic.response import json
from sanic import Blueprint

from .models import make_models
from .service import _has_session_service, SessionService, \
    _set_default_session_service, _register_session_service, \
    get_session_service

bp = Blueprint('sessions')


@bp.record
def session_module_registered(state):
    app = state.app
    db = state.options.get('db')
    db_name = state.options.get('db_name')
    loop = state.options.get('loop')

    if not db_name:
        raise RuntimeError(
            "This blueprint expects you to provide database access! "
            "Use: app.blueprint(bp, db_name=...)")
    if _has_session_service(db_name):
        raise RuntimeError(
            "This blueprint already registered with this db_name! "
            "Use other db_name: app.blueprint(bp, db_name=...)")
    if not db:
        raise RuntimeError(
            "This blueprint expects you to provide database access! "
            "Use: app.blueprint(bp, db=...)")

    initdb, dropdb, manager, model = make_models(db, db_name, loop)
    service = SessionService(app, db_name, initdb, dropdb, manager, model)
    _register_session_service(db_name, service)
    _set_default_session_service(db_name)


@bp.route('/info')
async def get_session_info(request):
    session = get_session_service()
    data = await session.get_request_session_data(request)
    return json({'data': data})
