from sanic.response import HTTPResponse


def redirect(request, to_url, headers=None, status=None, content_type=None):
    """
    Aborts execution and causes a 303 or 302 redirect, depending on
    the HTTP 1.1 method.
    """
    if not content_type:
        content_type = "text/html; charset=utf-8"
    if not status:
        if request.method == "POST":
            # See: https://en.wikipedia.org/wiki/HTTP_303
            status = 303
        else:
            status = 302
    if not to_url.startswith("/") and not to_url.startswith("http"):
        to_url = "/" + to_url
    if headers is None:
        headers = {}
    # According to RFC 7231, a relative URI is now permitted.
    headers['Location'] = to_url
    return HTTPResponse(status=status, headers=headers,
                        content_type=content_type)
