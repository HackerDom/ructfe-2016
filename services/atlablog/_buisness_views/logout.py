from sanic import Blueprint

from _buisness_views import USER_DB_NAME, REDIRECT_AFTER_LOGOUT
from users import get_user_service
from utils import redirect

bp = Blueprint('logout')


@bp.record
def registered(state):
    app = state.app
    view = state.options.get('view')

    if not view:
        raise RuntimeError(
            "This blueprint expects you to provide view object! "
            "Use: app.blueprint(bp, view=...)")

    bp.view = view


@bp.route('/logout')
async def logout(request):
    response = redirect(request, REDIRECT_AFTER_LOGOUT)
    # TODO: remove this line to make a venerability!
    if request.method == 'POST':
        service = get_user_service(USER_DB_NAME)
        await service.set_request_user(request, response, user=None)
    return response
