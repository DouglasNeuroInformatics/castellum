from .default import *


SECRET_KEY = 'i#$kwk(s24ysn+l%+c!*z9u4+45)oex!-s#!bux#wf2pv2cc0d'

DEBUG = True


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'subject_management': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'subject_management.sqlite3'),
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
