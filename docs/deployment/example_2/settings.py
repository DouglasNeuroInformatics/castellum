#
# Exemplary Castellum settings file. See also castellum/docs/example_1/settings.py
#
# Lines that need to be modified based on your setup are marked CHANGEME
import os

import ldap
from django_auth_ldap.config import LDAPSearch, NestedActiveDirectoryGroupType

from .default import *

SECRET_KEY = os.getenv('DJANGO_SECRET')

# Define hosts than can connect
ALLOWED_HOSTS = ['.example.com', '192.168.10.*']  # CHANGEME

# Database setup. NOTE: The values of `NAME` and `USER` given here have to match
# the actual database name and user set in postgres! See docs/example_2/guide.md
# for more details.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'castellum_default',
        'USER': 'castellum_default_user',
        'PASSWORD': os.getenv('DB_DEFAULT_PW'),
        'HOST': 'localhost',
    },
    'contacts': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'castellum_contacts',
        'USER': 'castellum_contacts_user',
        'PASSWORD': os.getenv('DB_CONTACTS_PW'),
        'HOST': 'castellum-db',  # CHANGEME
    },
}

# Use nginx to serve uploaded files
PROTECTED_MEDIA_SERVER = 'nginx'

# Email settings
DEFAULT_FROM_EMAIL = 'Subject Recruitment at Example <sr@example.com>'  # CHANGEME
SERVER_EMAIL = 'root@castellum-sv'  # CHANGEME
EMAIL_HOST = 'smtp.example.com'  # CHANGEME
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# People who get code error notifications in production
# CHANGEME
ADMINS = [
    ('admin1', 'admin1@example.com'),
    ('admin2', 'admin2@example.com'),
]

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
            'filename': '/var/log/castellum_monitoring.log',
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
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# LDAP setup.
AUTHENTICATION_BACKENDS.append('django_auth_ldap.backend.LDAPBackend')

# CHANGEME Everything below must be adapted to your organization's LDAP setup
# See https://django-auth-ldap.readthedocs.io for details about each setting
AUTH_LDAP_SERVER_URI = 'ldap://auth-sv'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PW')
AUTH_LDAP_USER_SEARCH = LDAPSearch('dc=example,dc=org', ldap.SCOPE_SUBTREE, "sAMAccountName=%(user)s")
AUTH_LDAP_USER_ATTR_MAP = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(group_lookup, ldap.SCOPE_SUBTREE, "(objectCategory=Group)")
AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300  # in seconds

CASTELLUM_GDPR_NOTIFICATION_TO = ['data-protection@example.com']  # CHANGEME
