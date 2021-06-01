import os

import ldap
from django_auth_ldap.config import LDAPSearch

from castellum.settings.default import *  # isort:skip

# FIXME: These values need to be changed
SECRET_KEY = 'CHANGEME'

# Only postgres/postgis are officially supported for castellum.
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
    }
}

ALLOWED_HOSTS = ['*']

MEDIA_ROOT = Path('/media')
PROTECTED_MEDIA_SERVER = 'uwsgi'

# The example deployment does not contain a mail server, so use dummy instead
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# See https://docs.djangoproject.com/en/stable/topics/logging/
ADMINS = [('admin', 'admin@example.com')]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'monitoring-file': {
            'class': 'logging.FileHandler',
            'filename': '/log/monitoring.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # 'monitoring' is our custom logger namespace to identify and
        # retrace suspicious user behavior. It contains potentially
        # sensitive information (e.g. subject search terms). Monitoring
        # logs will not be created unless configured.
        'monitoring': {
            'handlers': ['monitoring-file'],
            'level': 'INFO',
        }
    },
}

# LDAP
# See https://django-auth-ldap.readthedocs.io/
AUTHENTICATION_BACKENDS.append("django_auth_ldap.backend.LDAPBackend")

AUTH_LDAP_SERVER_URI = 'ldap://ldap:3389'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = 'admin'
AUTH_LDAP_USER_SEARCH = LDAPSearch('dc=example,dc=org', ldap.SCOPE_SUBTREE, '(uid=%(user)s)')
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
}

# Limit login attempts
# See https://django-axes.readthedocs.io/
INSTALLED_APPS.append('axes')
AUTHENTICATION_BACKENDS.insert(0, 'axes.backends.AxesBackend')
MIDDLEWARE.append('axes.middleware.AxesMiddleware')
AXES_META_PRECEDENCE_ORDER = ['HTTP_X_REAL_IP']

# Setup geofilters
INSTALLED_APPS.append('castellum.geofilters')
NOMINATIM = {
    # see https://geopy.readthedocs.io/en/stable/#geopy.geocoders.Nominatim
    'domain': 'nominatim:8080',
    'scheme': 'http',
}

SCHEDULER_URL = os.getenv('CASTELLUM_SCHEDULER_URL', 'http://scheduler:8000')
SCHEDULER_TOKEN = 'CHANGEME'

CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID = 3
CASTELLUM_COVERLETTER_TEMPLATE = BASE_DIR / 'subjects' / 'fixtures' / 'demo_coverletter.docx'
