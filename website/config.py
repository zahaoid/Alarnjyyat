import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'who-cares'
    DATABASE = {'database': os.environ.get('POSTGRES_DB'), 'user': os.environ.get('POSTGRES_USER'), 'password': os.environ.get('POSTGRES_PASSWORD'), 'host': 'database', 'port': 5432}