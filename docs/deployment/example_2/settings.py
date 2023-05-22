import os

import ldap
from django_auth_ldap.config import LDAPSearch

from castellum.settings.default import *

SECRET_KEY = os.getenv('DJANGO_SECRET')

# Define hosts than can connect
ALLOWED_HOSTS = ['.example.com', '192.168.10.*']

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
        'HOST': 'castellum-db',
    },
}

# Use nginx to serve uploaded files
PROTECTED_MEDIA_SERVER = 'nginx'

# Email settings
DEFAULT_FROM_EMAIL = 'Subject Recruitment at Example <sr@example.com>'
SERVER_EMAIL = 'root@castellum-sv'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# People who get code error notifications in production
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

# LDAP
# See https://django-auth-ldap.readthedocs.io/
AUTHENTICATION_BACKENDS.append('django_auth_ldap.backend.LDAPBackend')

AUTH_LDAP_SERVER_URI = 'ldap://auth-sv'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PW')
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
MFA_DOMAIN = 'example.com'
MFA_SITE_TITLE = 'Castellum Demo'

# Limit login attempts
# See https://django-axes.readthedocs.io/
INSTALLED_APPS.append('axes')
AUTHENTICATION_BACKENDS.insert(0, 'axes.backends.AxesBackend')
MIDDLEWARE.append('axes.middleware.AxesMiddleware')
AXES_META_PRECEDENCE_ORDER = ['HTTP_X_REAL_IP']

CASTELLUM_GDPR_NOTIFICATION_TO = ['data-protection@example.com']
CASTELLUM_REPORT_NOTIFICATION_TO = ['report@example.com']
