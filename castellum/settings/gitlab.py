from .default import *

SECRET_KEY = 'CHANGEME'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'CHANGEME',
        'HOST': 'db_default',
    },
    'contacts': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'CHANGEME',
        'HOST': 'db_contacts',
    },
}

CASTELLUM_API_ENABLED = True

CASTELLUM_EMAIL_BASE_URL = 'https://example.com'

# Setup geofilters
INSTALLED_APPS.append('django.contrib.gis')
INSTALLED_APPS.append('castellum.geofilters')
