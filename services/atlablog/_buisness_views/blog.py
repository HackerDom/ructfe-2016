import asyncio
from collections import defaultdict

import os
from time import time

from sanic import Blueprint
from sanic.response import html, json
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
        validators.Length(min=3, message='Little short for an title?'),
        validators.Length(max=1000, message='Longer then usual title!'),
    ])
    text = TextAreaField('Text (drop the file here)', [
        validators.Length(min=3, message='Little short for an blog entry?'),
        validators.Length(max=65000, message='Longer then usual blog entry!'),
    ])
    attachments = HiddenField()


class BlogCommentForm(Form):
    text = TextAreaField('Text (drop the file here)', [
        validators.Length(min=1, message='Little short for comment?'),
        validators.Length(max=65000, message='Longer then usual comment!'),
    ])
    attachments = HiddenField()


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


@bp.route('/blog-count.json')
async def blog_count(request):
    blog = get_entry_service(BLOG_ENTRY_DB_NAME)
    entries_count = await blog.get_entries_count()
    pages = entries_count // 10
    return json({
        'first': '/?page=0', 'last': '/?page=' + str(pages),
        'pages': pages + 1,
        'entries_count': entries_count,
        'per_page': 10,
    })


notify = defaultdict(asyncio.Future)


@bp.route('/blog-notify')
async def blog_signal(request):
    blog = get_entry_service(BLOG_ENTRY_DB_NAME)
    entries_count = await blog.get_entries_count()
    count = request.args.get('count', "no")
    count = int(count) if count.isdigit() else entries_count + 1
    if count <= entries_count:
        return await blog_count(request)
    elif entries_count + 10 < count:
        return json({'error': 'you try to see so far into the future!'},
                    status=400)
    await notify[count]
    return await blog_count(request)


@bp.route('/')
@login_required(login_url='/login')
async def blog(request):
    form = BlogEntryForm(request.form) if request.method == 'POST' else \
        BlogEntryForm()
    blog = get_entry_service(BLOG_ENTRY_DB_NAME)
    entries_count = await blog.get_entries_count()
    user_service = get_user_service(USER_DB_NAME)
    user = await user_service.get_request_user(request)
    if request.method == 'POST' and form.validate():
        text = form.text.data
        title = form.title.data
        attachments = _clean_attachments(form.attachments.data)
        try:
            slug = blog.slugify(title) + '-' + str(time()).replace('.', '')
            await blog.create_entry(title, content=text, slug=slug, meta={
                'user': user.username,
                'attachments': attachments,
            })
            notify[entries_count + 1].set_result(True)
            for key, value in list(notify.items()):
                if key < entries_count:
                    value.cancel()
                    del notify[key]
            return redirect(request, '/')
        except Exception as e:
            form.text.errors.append(str(e))
    pages = entries_count // 10
    page = request.args.get('page', "0")
    page = int(page) if page.isdigit() else 0
    offset = page * 10 if 0 < page <= pages else 0
    next_page = page + 1 if page + 1 <= pages else None
    entries = await blog.get_entries(
        limit=10, offset=offset, order_by='-created')
    return html(bp.view.render('blog', {
        'form': form, 'entries': entries, 'entries_count': entries_count,
        'user': user, 'next_page': next_page,
    }))


@bp.route('/<name>')
@login_required(login_url='/login')
async def comment(request, name):
    blog = get_entry_service(BLOG_ENTRY_DB_NAME)
    comments = get_entry_service(COMMENT_ENTRY_DB_NAME)
    user_service = get_user_service(USER_DB_NAME)
    user = await user_service.get_request_user(request)
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
        text = form.text.data
        attachments = _clean_attachments(form.attachments.data)
        try:
            slug = name + '-' + str(time()).replace('.', '')
            await comments.create_entry("", content=text, slug=slug, meta={
                'user': user.username,
                'attachments': attachments,
            })
            return redirect(request, '/' + name)
        except Exception as e:
            form.text.errors.append(str(e))
    return html(bp.view.render('entry', {
        'form': form, 'entry': entry, 'comments': comment_entries,
        'user': user,
    }))
