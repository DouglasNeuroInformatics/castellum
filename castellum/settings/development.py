from .default import *


SECRET_KEY = 'i#$kwk(s24ysn+l%+c!*z9u4+45)oex!-s#!bux#wf2pv2cc0d'

DEBUG = True


# setup debug toolbar

try:
    import debug_toolbar

    INTERNAL_IPS = ['127.0.0.1', 'localhost']

    INSTALLED_APPS += [
        'debug_toolbar',
    ]

    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE
except ImportError:
    pass


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'contacts': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'contacts.sqlite3'),
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DOMAINS = {
    'contact': '04d0e64e-a58a-41b3-bf6b-7a90dae84199',
    'attributeset': '4ad2404c-7ae6-4a65-9c25-8a23bcfbd694',
}
