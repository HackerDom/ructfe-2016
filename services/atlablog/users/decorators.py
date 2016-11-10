from functools import wraps
from inspect import isawaitable

from utils import redirect
from . import get_user_service


def login_required(*, login_url='/login', user_db_name=None):
    if not isinstance(login_url, str):
        raise TypeError('login_url is not a str')

    def decorate(func):
        async def wrapper(request, *args, **kwargs):
            service = get_user_service(user_db_name)
            user = await service.get_request_user(request)
            if not user.is_authenticated():
                return redirect(request, login_url)

            response = func(request, *args, **kwargs)
            if isawaitable(response):
                response = await response
            return response

        return wrapper

    return decorate
