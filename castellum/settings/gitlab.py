from .default import *

SECRET_KEY = 'CHANGEME'

# disable cache busting (necessary for testing)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

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

CASTELLUM_COVERLETTER_TEMPLATE = BASE_DIR / 'subjects' / 'fixtures' / 'demo_coverletter.docx'
CASTELLUM_API_ENABLED = True

# Setup geofilters
INSTALLED_APPS.append('django.contrib.gis')
INSTALLED_APPS.append('castellum.geofilters')
