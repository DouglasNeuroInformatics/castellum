from .default import *

SECRET_KEY = 'CHANGEME'

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

DEBUG = True

PROTECTED_MEDIA_SERVER = 'django'

# disable cache busting (necessary for testing)
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

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

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_COLLAPSED': True,
    }
except ImportError:
    pass


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR.parent / 'db.sqlite3',
    },
    'contacts': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': BASE_DIR.parent / 'contacts.sqlite3',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID = 3
CASTELLUM_GDPR_NOTIFICATION_TO = ['data-protection@example.com']
CASTELLUM_REPORT_NOTIFICATION_TO = ['report@example.com']
CASTELLUM_API_ENABLED = True
CASTELLUM_SUBJECT_CREATION_REQUESTS_ENABLED = True

# Setup geofilters
INSTALLED_APPS.append('django.contrib.gis')
INSTALLED_APPS.append('castellum.geofilters')

MFA_DOMAIN = 'localhost'
