from jinja2 import Environment, FileSystemLoader

import settings

engine = Environment(loader=FileSystemLoader([settings.TEMPLATES_DIR]))


def render(template, **context):
    t = engine.get_template(template)
    return t.render(**context)
