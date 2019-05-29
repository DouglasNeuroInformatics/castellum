from castellum.settings.default import *

FOO_DIR = os.path.dirname(__file__)

SECRET_KEY = 'i#$kwk(s24ysn+l%+c!*z9u4+45)oex!-s#!bux#wf2pv2cc0d'

DEBUG = True


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(FOO_DIR, 'db.sqlite3'),
    },
    'contacts': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(FOO_DIR, 'contacts.sqlite3'),
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DOMAINS = {
    'contact': '04d0e64e-a58a-41b3-bf6b-7a90dae84199',
}
