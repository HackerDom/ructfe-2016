from sanic import Blueprint
from sanic.response import html
from wtforms import Form, BooleanField, StringField, validators, PasswordField

from _buisness_views import USER_DB_NAME, REDIRECT_AFTER_LOGIN
from users import get_user_service
from utils import redirect

bp = Blueprint('registration')


@bp.record
def registered(state):
    app = state.app
    view = state.options.get('view')

    if not view:
        raise RuntimeError(
            "This blueprint expects you to provide view object! "
            "Use: app.blueprint(bp, view=...)")

    bp.view = view


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [
        validators.Length(min=6, message='Little short for an email address?'),
        validators.Length(max=45, message='Longer then usual email!'),
        validators.Email(message='That\'s not a valid email address.')])
    password = PasswordField('Password', [validators.Length(min=5, max=25)])
    accept_rules = BooleanField(
        'I accept the site rules', [validators.InputRequired()])


@bp.route('/registration')
async def registration(request):
    form = RegistrationForm(request.form) if request.method == 'POST' else \
        RegistrationForm()
    if request.method == 'POST' and form.validate():
        service = get_user_service(USER_DB_NAME)
        username = form.username.data
        password = form.password.data
        email = form.email.data
        try:
            user = await service.create_user(username, password, meta={
                'email': email,
            })
            response = redirect(request, REDIRECT_AFTER_LOGIN)
            await service.set_request_user(request, response, user)
            return response
        except service.UserServiceError as e:
            form.username.errors.append(str(e))
    return html(bp.view.render('registration', {'form': form}))
