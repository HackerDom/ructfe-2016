from sanic import Blueprint

from .models import make_models
from .service import _has_entry_service, EntryService, \
    _set_default_entry_service, _register_entry_service

bp = Blueprint('entries')


@bp.record
def module_registered(state):
    app = state.app
    db = state.options.get('db')
    db_name = state.options.get('db_name')
    loop = state.options.get('loop')

    if not db_name:
        raise RuntimeError(
            "This blueprint expects you to provide database access! "
            "Use: app.blueprint(bp, db_name=...)")
    if _has_entry_service(db_name):
        raise RuntimeError(
            "This blueprint already registered with this db_name! "
            "Use other db_name: app.blueprint(bp, db_name=...)")
    if not db:
        raise RuntimeError(
            "This blueprint expects you to provide database access! "
            "Use: app.blueprint(bp, db=...)")

    initdb, dropdb, manager, model = make_models(db, db_name, loop)
    service = EntryService(app, db_name, initdb, dropdb, manager, model)
    _register_entry_service(db_name, service)
    _set_default_entry_service(db_name)
