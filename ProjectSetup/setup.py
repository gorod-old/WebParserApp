"""Project Settings: Development/Production"""
import os


class ProjSetup:

    def __init__(self, base_dir):
        self.PROJ_TITLE = os.environ.get('PROJ_TITLE')
        self.PROJ_SUBTITLE = os.environ.get('PROJ_SUBTITLE')
        dev = os.environ.get('DEV')
        self.DEV = True if dev == 'True' else False  # development version (True/False)
        debug = os.environ.get('DEBUG')
        self.DEBUG = True if debug == 'True' else False
        self.DOMAIN = os.environ.get('DOMAIN')
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        self.ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*'] if self.DEV else [self.DOMAIN, '*']
        self.DATABASES = self.__get_databases(base_dir)

    def __get_databases(self, base_dir):
        dev_db = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': base_dir / 'db.sqlite3',
            }
        }
        prod_db = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('DB_NAME'),
                'USER': os.environ.get('DB_USER'),
                'PASSWORD': os.environ.get('DB_PASSWORD'),
                'HOST': os.environ.get('DB_HOST'),
                'PORT': os.environ.get('DB_PORT'),
            }
        }
        return dev_db if self.DEV else prod_db
