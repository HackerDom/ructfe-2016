import os
from time import time

from sanic import Blueprint
from sanic.response import html
from wtforms import Form, StringField, validators, TextAreaField, HiddenField

import settings
from _buisness_views import USER_DB_NAME, BLOG_ENTRY_DB_NAME, \
    COMMENT_ENTRY_DB_NAME, MEDIA_URL
from entries import get_entry_service
from users import get_user_service
from users.decorators import login_required
from utils import redirect

bp = Blueprint('blog')


@bp.record
def registered(state):
    app = state.app
    view = state.options.get('view')

    if not view:
        raise RuntimeError(
            "This blueprint expects you to provide view object! "
            "Use: app.blueprint(bp, view=...)")

    bp.view = view


class BlogEntryForm(Form):
    title = StringField('Title', [
        validators.Length(min=6, message='Little short for an title?'),
        validators.Length(max=1000, message='Longer then usual title!'),
    ])
    text = TextAreaField('Text', [
        validators.Length(min=6, message='Little short for an blog entry?'),
        validators.Length(max=65000, message='Longer then usual blog entry!'),
    ])
    attachments = HiddenField()


class BlogCommentForm(Form):
    text = TextAreaField('Text', [
        validators.Length(min=6, message='Little short for an blog entry?'),
        validators.Length(max=65000, message='Longer then usual blog entry!'),
    ])


def _clean_attachments(data):
    if not data:
        return []
    links = []
    for x in data.split(';'):
        x = x.strip()
        if not x:
            continue
        if '..' in x:
            continue
        if not x.startswith(MEDIA_URL + '/'):
            continue
        x = x[len(MEDIA_URL + '/'):]
        if not os.path.exists(os.path.join(settings.DATA_DIR, x)):
            continue
        links.append(x)
    return links


@bp.route('/')
@login_required(login_url='/login')
async def blog(request):
    form = BlogEntryForm(request.form) if request.method == 'POST' else \
        BlogEntryForm()
    blog = get_entry_service(BLOG_ENTRY_DB_NAME)
    if request.method == 'POST' and form.validate():
        user = get_user_service(USER_DB_NAME)
        text = form.text.data
        title = form.title.data
        attachments = _clean_attachments(form.attachments.data)
        print(attachments)
        try:
            await blog.create_entry(title, content=text, meta={
                'user': (await user.get_request_user(request)).username,
                'attachments': attachments,
            })
            return redirect(request, '/')
        except Exception as e:
            form.text.errors.append(str(e))
    entries = await blog.get_entries(limit=10)
    return html(bp.view.render('blog', {'form': form, 'entries': entries}))


@bp.route('/<name>')
@login_required(login_url='/login')
async def comment(request, name):
    blog = get_entry_service(BLOG_ENTRY_DB_NAME)
    comments = get_entry_service(COMMENT_ENTRY_DB_NAME)
    try:
        entry = await blog.get_entries(limit=1, slug=name)
        entry = entry[0]
    except IndexError:
        return redirect(request, '/')
    comment_entries = await comments.get_entries(
        limit=100, slug__startswith=name)
    form = BlogCommentForm(request.form) if request.method == 'POST' else \
        BlogCommentForm()
    if request.method == 'POST' and form.validate():
        user = get_user_service(USER_DB_NAME)
        text = form.text.data
        try:
            slug = name + str(time())
            await comments.create_entry("", content=text, slug=slug, meta={
                'user': (await user.get_request_user(request)).username
            })
            return redirect(request, '/' + name)
        except Exception as e:
            form.text.errors.append(str(e))
    return html(bp.view.render('entry', {
        'form': form, 'entry': entry, 'comments': comment_entries
    }))
