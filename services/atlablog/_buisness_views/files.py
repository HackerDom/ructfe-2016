from uuid import uuid4
import os

from sanic import Blueprint
from sanic.response import json
from wtforms import Form, validators, FileField

import settings
from _buisness_views import USER_DB_NAME, FILES_ENTRY_DB_NAME, MEDIA_URL
from entries import get_entry_service
from users import get_user_service
from users.decorators import login_required

bp = Blueprint('files')


@bp.record
def registered(state):
    app = state.app
    app.static(MEDIA_URL, settings.DATA_DIR)
    view = state.options.get('view')

    if not view:
        raise RuntimeError(
            "This blueprint expects you to provide view object! "
            "Use: app.blueprint(bp, view=...)")

    bp.view = view


class FileForm(Form):
    file = FileField('file', [validators.DataRequired()])


def _save_file_on_localhost_filesystem(name, data):
    try:
        name, ext = name.rsplit('.', 1)
        filename = str(uuid4()) + '.' + ext
        filepath = os.path.join(settings.DATA_DIR, filename)
        with open(filepath, mode="wb") as f:
            f.write(data)
    except Exception as e:
        raise ValueError("Bad file object: " + str(e))
    return MEDIA_URL + "/" + filename


@bp.route('/upload')
@login_required(login_url='/login')
async def upload(request):
    files = get_entry_service(FILES_ENTRY_DB_NAME)
    errors = []
    if request.method == 'POST':
        user = get_user_service(USER_DB_NAME)
        data = request.body or b''
        name = request.headers.get('X-File-Name')
        if name:
            try:
                url = _save_file_on_localhost_filesystem(name, data)
                entry = await files.create_entry(
                    name, content=url, slug=url, meta={
                        'user': (await user.get_request_user(request)).username
                    })
                return json({'status': 'ok', 'url': url, 'entry': entry.slug})
            except Exception as e:
                errors.append(str(e))
        else:
            errors.append('No filename header!')
    return json({'status': 'error', 'errors': errors}, status=400)
