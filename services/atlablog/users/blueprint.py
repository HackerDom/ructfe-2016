from sanic import Blueprint

from sessions import get_session_service
from .models import make_models
from .service import _has_user_service, UserService, \
    _set_default_user_service, _register_user_service

bp = Blueprint('users')


@bp.record
def module_registered(state):
    app = state.app
    db = state.options.get('db')
    db_name = state.options.get('db_name')
    sessions_db_name = state.options.get('sessions_db_name')
    loop = state.options.get('loop')

    if not db_name:
        raise RuntimeError(
            "This blueprint expects you to provide database access! "
            "Use: app.blueprint(bp, db_name=...)")
    if _has_user_service(db_name):
        raise RuntimeError(
            "This blueprint already registered with this db_name! "
            "Use other db_name: app.blueprint(bp, db_name=...)")
    if not db:
        raise RuntimeError(
            "This blueprint expects you to provide database access! "
            "Use: app.blueprint(bp, db=...)")

    try:
        get_session_service(sessions_db_name)
    except (TypeError, ValueError):
        raise RuntimeError(
            "This blueprint expects `sessions` blueprint! Register it before"
            "and pass the `sessions_db_name` options"
        )

    initdb, dropdb, manager, model = make_models(db, db_name, loop)  # noqa
    service = UserService(app, db_name, initdb, dropdb, manager, model)
    service.sessions_db_name = sessions_db_name
    _register_user_service(db_name, service)
    _set_default_user_service(db_name)


# @bp.route("/register")
# def registration(request):
#     return service.registration(request)
#
# @bp.route("/auth")
# def authorization(request):
#     return service.authorization(request)
