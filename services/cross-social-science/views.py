import os

from jinja2 import FileSystemLoader, Environment


class View:
    """
    Viewer class. Just represent anything

    >>> view = View({"HTML_TEMPLATES_DIR": "templates"})
    >>> view.render('index', {})
    """
    class ViewError(Exception):
        pass

    def __init__(self, settings):
        if not isinstance(settings, dict):
            raise TypeError('settings is not a dict')
        templates_dir = settings['HTML_TEMPLATES_DIR']
        if not os.path.exists(templates_dir):
            raise ValueError("settings['HTML_TEMPLATES_DIR'] does not exists")
        loader = FileSystemLoader([templates_dir])
        self.engine = Environment(loader=loader)

    def render_as_html(self, template, context):
        t = self.engine.get_template(template + '.html')
        return t.render(**context)

    def render(self, template, context=None, format='html'):
        if not context:
            context = {}
        renderer = getattr(self, 'render_as_' + format, None)
        if renderer and callable(renderer):
            try:
                return renderer(template, context)
            except Exception as e:
                raise self.ViewError(
                    'View "%s" renderer problem: %s: %s' %
                    (format, type(e).__name__, e))
        raise self.ViewError('View format="%s" is not known' % format)
