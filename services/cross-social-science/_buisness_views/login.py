from sanic import Blueprint
from sanic.response import html
from wtforms import Form, StringField, validators, PasswordField

from _buisness_views import USER_DB_NAME, REDIRECT_AFTER_LOGIN
from users import get_user_service
from utils import redirect

bp = Blueprint('login')


@bp.record
def registered(state):
    app = state.app
    view = state.options.get('view')

    if not view:
        raise RuntimeError(
            "This blueprint expects you to provide view object! "
            "Use: app.blueprint(bp, view=...)")

    bp.view = view


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Length(min=5, max=25)])


@bp.route('/login')
async def login(request):
    form = LoginForm(request.form) if request.method == 'POST' else \
        LoginForm()
    if request.method == 'POST' and form.validate():
        service = get_user_service(USER_DB_NAME)
        username = form.username.data
        password = form.password.data
        try:
            user = await service.validate_credentials_and_get_user(
                username, password)
            response = redirect(request, REDIRECT_AFTER_LOGIN)
            await service.set_request_user(request, response, user)
            return response
        except service.UserServiceError as e:
            form.username.errors.append(str(e))
    return html(bp.view.render('registration', {'form': form}))
