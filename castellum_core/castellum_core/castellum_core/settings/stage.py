from .default import *


# FIXME: These values need to be changed
SECRET_KEY = 'i#$kwk(s24ysn+l%+c!*z9u4+45)oex!-s#!bux#wf2pv2cc0d'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ALLOWED_HOSTS = [
    'localhost',
]

