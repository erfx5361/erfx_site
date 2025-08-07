import os
basedir = os.path.abspath(os.path.dirname(__file__))
appdir = os.path.join(basedir, 'app')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'temporary_secret_123'
    GITHUB_URL = 'https://github.com/erfx5361'





