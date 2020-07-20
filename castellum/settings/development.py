from .default import *

SECRET_KEY = 'CHANGEME'

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

CASTELLUM_COVERLETTER_TEMPLATE = os.path.join(BASE_DIR, 'subjects', 'fixtures', 'demo_coverletter.docx')
CASTELLUM_DELETE_NOTIFICATION_TO = 'data-protection@example.com'

# Setup geofilters
INSTALLED_APPS.append('castellum.geofilters')
