import os

class Config:
    SECRET_KEY = 'a_secret_key'  #update later
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "site.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
