from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '..', '.env'))

TESTING = environ.get('TESTING')
DEBUG = environ.get('DEBUG')
DATABASE_HOST = environ.get('DATABASE_HOST')
DATABASE_USER = environ.get('DATABASE_USER')
DATABASE_PASSWORD = environ.get('DATABASE_PASSWORD')
DATABASE_NAME = environ.get('DATABASE_NAME')