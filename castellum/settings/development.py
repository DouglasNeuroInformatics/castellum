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
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'CHANGEME',
        'HOST': os.environ.get('DB_DEFAULT_HOST', 'localhost'),
        'PORT': '6670',
    },
    'contacts': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'CHANGEME',
        'HOST': os.environ.get('DB_CONTACTS_HOST', 'localhost'),
        'PORT': '6671',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CASTELLUM_COVERLETTER_TEMPLATE = os.path.join(BASE_DIR, 'subjects', 'fixtures', 'demo_coverletter.docx')
CASTELLUM_DELETE_NOTIFICATION_TO = 'data-protection@example.com'
CASTELLUM_STUDY_STATUS_NOTIFICATION_TO = 'pr@example.com'

# Setup geofilters
INSTALLED_APPS.append('castellum.geofilters')
