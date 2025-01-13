import os

import ldap
from django_auth_ldap.config import LDAPSearch

from castellum.settings.default import *

# FIXME: These values need to be changed
SECRET_KEY = 'CHANGEME'

ALLOWED_HOSTS = ['*']

# Only postgres/postgis are officially supported for Castellum.
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

MEDIA_ROOT = Path('/app/media')
PROTECTED_MEDIA_SERVER = 'uwsgi'

# The example deployment does not contain a mail server, so use dummy instead
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# People who get code error notifications in production
ADMINS = [
    ('admin1', 'admin1@example.com'),
    ('admin2', 'admin2@example.com'),
]

# LDAP
# See https://django-auth-ldap.readthedocs.io/
AUTHENTICATION_BACKENDS.append('django_auth_ldap.backend.LDAPBackend')

AUTH_LDAP_SERVER_URI = 'ldap://ldap:3389'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = 'admin'
AUTH_LDAP_USER_QUERY_FIELD = 'username'
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    'dc=example,dc=org',
    ldap.SCOPE_SUBTREE,
    '(|(uid=%(user)s)(mail=%(user)s))',
)
AUTH_LDAP_USER_ATTR_MAP = {
    'username': 'uid',
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
}
# Alternatively you can manage permissions directly in LDAP
# See https://django-auth-ldap.readthedocs.io/en/latest/permissions.html#using-groups-directly
# AUTH_LDAP_FIND_GROUP_PERMS = True

# See https://github.com/xi/django-mfa3
MFA_DOMAIN = 'castellum.example.com'
MFA_SITE_TITLE = 'Castellum Demo'

# Limit login attempts
# See https://django-axes.readthedocs.io/
INSTALLED_APPS.append('axes')
AUTHENTICATION_BACKENDS.insert(0, 'axes.backends.AxesBackend')
MIDDLEWARE.append('axes.middleware.AxesMiddleware')
AXES_IPWARE_META_PRECEDENCE_ORDER = ['HTTP_X_REAL_IP']

CASTELLUM_EMAIL_BASE_URL = 'https://castellum.example.com'
CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID = 3
CASTELLUM_GDPR_NOTIFICATION_TO = ['data-protection@example.com']
CASTELLUM_REPORT_NOTIFICATION_TO = ['report@example.com']

# Setup geofilters
INSTALLED_APPS.append('django.contrib.gis')
INSTALLED_APPS.append('castellum.geofilters')
NOMINATIM = {
    # see https://geopy.readthedocs.io/en/stable/#geopy.geocoders.Nominatim
    'domain': 'nominatim:8080',
    'scheme': 'http',
}

# See https://git.mpib-berlin.mpg.de/castellum/castellum_scheduler/
SCHEDULER_URL = os.getenv('CASTELLUM_SCHEDULER_URL', 'http://scheduler:8000')
SCHEDULER_TOKEN = 'CHANGEME'

# See https://git.mpib-berlin.mpg.de/castellum/django-storage-timestamps/
INSTALLED_APPS.append('storage_timestamps')
STORAGES = {
    **STORAGES,
    'default': {
        'BACKEND': 'storage_timestamps.storage.TimestampedFileSystemStorage',
    },
}
TIMESTAMP_AUTHORITY = 'https://freetsa.org/tsr'
