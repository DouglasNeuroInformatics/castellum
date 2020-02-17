import ldap
from django_auth_ldap.config import LDAPSearch

from .default import *

# FIXME: These values need to be changed
SECRET_KEY = 'i#$kwk(s24ysn+l%+c!*z9u4+45)oex!-s#!bux#wf2pv2cc0d'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'CHANGEME',
        'HOST': 'db_default',
    },
    'contacts': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'CHANGEME',
        'HOST': 'db_contacts',
    }
}

ALLOWED_HOSTS = ['*']

MEDIA_ROOT = '/media'

# The example deployment does not contain a mail server, so use dummy instead
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# LDAP
# See https://django-auth-ldap.readthedocs.io/
AUTHENTICATION_BACKENDS.append("django_auth_ldap.backend.LDAPBackend")

AUTH_LDAP_SERVER_URI = 'ldap://ldap'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = 'admin'
AUTH_LDAP_USER_SEARCH = LDAPSearch('dc=example,dc=org', ldap.SCOPE_SUBTREE, '(uid=%(user)s)')
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
}

CASTELLUM_DOMAINS = {
    'contact': {
        'key': 'dac7466e-db47-4c1c-a69d-f8b98850f777',
        'bits': 40,
    }
}

# Limit login attempts
# See https://django-axes.readthedocs.io/
INSTALLED_APPS.append('axes')
AUTHENTICATION_BACKENDS.insert(0, 'axes.backends.AxesBackend')
MIDDLEWARE.append('axes.middleware.AxesMiddleware')
AXES_META_PRECEDENCE_ORDER = ['HTTP_X_REAL_IP']
