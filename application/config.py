from os import environ, path
from dotenv import load_dotenv

BASE_DIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASE_DIR, '..', '.env'))

LOCAL = environ.get('LOCAL')
TESTING = environ.get('TESTING')
DEBUG = environ.get('DEBUG')
DATABASE_HOST = environ.get('DATABASE_HOST')
DATABASE_USER = environ.get('DATABASE_USER')
DATABASE_PASSWORD = environ.get('DATABASE_PASSWORD')
DATABASE_NAME = environ.get('DATABASE_NAME')
SSL_CA = environ.get('SSL_CA')
CA_PATH = path.join(BASE_DIR, SSL_CA)

if LOCAL:
    ENGINE = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
    REMOTE_HOST = environ.get('REMOTE_HOST')
    REMOTE_USER = environ.get('REMOTE_USER')
    REMOTE_PASSWORD = environ.get('REMOTE_PASSWORD')
    REMOTE_NAME = environ.get('REMOTE_NAME')
    REMOTE_ENGINE = f"mysql+pymysql://{REMOTE_USER}:{REMOTE_PASSWORD}@{REMOTE_HOST}/{REMOTE_NAME}?ssl_cs={CA_PATH}"
else:
    ENGINE = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}?ssl_cs={CA_PATH}"
