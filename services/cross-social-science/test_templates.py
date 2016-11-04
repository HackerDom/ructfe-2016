from templates import render


def test_render_without_context():
    html = render('example.html')
    assert '<!DOCTYPE html>' in html
    assert '<h1>hello! </h1>' in html


def test_render_with_context():
    html = render('example.html', name='AKJWFaawkjfbaw')
    assert '<!DOCTYPE html>' in html
    assert '<h1>hello! AKJWFaawkjfbaw</h1>' in html
