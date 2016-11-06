from sanic import Blueprint

from .models import make_models
from .service import _has_blog_service, BlogService, \
    _set_default_blog_service, _register_blog_service

bp = Blueprint('blog')


@bp.record
def blog_module_registered(state):
    app = state.app
    db = state.options.get('db')
    db_name = state.options.get('db_name')
    loop = state.options.get('loop')

    if not db_name:
        raise RuntimeError(
            "This blueprint expects you to provide database access! "
            "Use: app.blueprint(bp, db_name=...)")
    if _has_blog_service(db_name):
        raise RuntimeError(
            "This blueprint already registered with this db_name! "
            "Use other db_name: app.blueprint(bp, db_name=...)")
    if not db:
        raise RuntimeError(
            "This blueprint expects you to provide database access! "
            "Use: app.blueprint(bp, db=...)")

    initdb, dropdb, manager, model = make_models(db, db_name, loop)
    service = BlogService(app, db_name, initdb, dropdb, manager, model)
    _register_blog_service(db_name, service)
    _set_default_blog_service(db_name)
