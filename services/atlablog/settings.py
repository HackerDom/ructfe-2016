import os


BASE_DIR = os.path.abspath(os.path.dirname(__name__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
DATA_DIR = os.path.join(BASE_DIR, '__data__')

DATABASE = 'test'
