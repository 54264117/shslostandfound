import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this-is-a-test-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_FROMADDRESS = os.environ.get('MAIL_FROMADDRESS')
    ADMINS = ['liam@lockwd.com']
    ITEMS_PER_PAGE = 3
    EMAIL_TOKEN_EXPIRATION = 600
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    IMAGE_FOLDER = 'images/'
    RESOURCES_FOLDER = 'resources/'
    THUMBNAIL_MEDIA_ROOT = 'static/images/'
    THUMBNAIL_MEDIA_URL = 'images/'

    SERVER_NAME = os.environ.get('SERVER_NAME') or 'localhost:5000'
