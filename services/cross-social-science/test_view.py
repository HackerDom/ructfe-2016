import pytest

from views import View


def test_render_without_context():
    view = View({"HTML_TEMPLATES_DIR": 'templates'})
    html = view.render('example')
    assert '<!DOCTYPE html>' in html
    assert '<h1>hello! </h1>' in html


def test_render_with_context():
    view = View({"HTML_TEMPLATES_DIR": 'templates'})
    html = view.render('example', {'name': 'AKJWFaawkjfbaw'})
    assert '<!DOCTYPE html>' in html
    assert '<h1>hello! AKJWFaawkjfbaw</h1>' in html


def test_render_not_found_template():
    view = View({"HTML_TEMPLATES_DIR": 'templates'})
    with pytest.raises(view.ViewError) as excinfo:
        view.render('example.html')
    excinfo.match(r'View "html" .*TemplateNotFound.*example\.html\.html')
