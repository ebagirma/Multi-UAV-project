from os import environ, path

basedir = path.abspath(path.dirname(__file__))

class Config:
    """Set Flask configuration vars from .env file."""

    # General
    TESTING = environ.get('TESTING')
    FLASK_DEBUG = environ.get('FLASK_DEBUG') or True
    SECRET_KEY = environ.get('SECRET_KEY')
    UPLOAD_FOLDER = environ.get('UPLOAD_FOLDER') or path.join(basedir, 'uploads/')

    # Database
    # SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI') or 'postgresql://natminyel:password@localhost:5432/farmlands'
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') or False